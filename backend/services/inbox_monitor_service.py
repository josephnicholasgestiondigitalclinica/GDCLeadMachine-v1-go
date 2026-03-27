import os
import imaplib
import email
import re
import aiohttp
import asyncio
from email.header import decode_header
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Senders that indicate a bounce / NDR message
BOUNCE_FROM_PATTERNS = [
    'mailer-daemon',
    'postmaster',
    'mail delivery subsystem',
    'mail delivery system',
    'delivery subsystem',
    'system administrator',
    'mail system',
]

# Subject keywords that indicate a bounce
BOUNCE_SUBJECT_PATTERNS = [
    'delivery status notification',
    'delivery failure',
    'mail delivery failed',
    'delivery notification',
    'undeliverable',
    'returned mail',
    'failure notice',
    'non-delivery',
    'delivery status',
    'message not delivered',
    'error de entrega',
    'mensaje no entregado',
    'devuelto',
    'no se pudo entregar',
    'entrega fallida',
]


class InboxMonitorService:
    """
    Monitors email inboxes via IMAP for bounce / Non-Delivery Reports.

    When a bounce is detected:
    1. The affected clinic is marked  email_bounced=True in MongoDB.
    2. Any pending queue items for that clinic are cancelled (status=bounced).
    3. GPT-4o-mini is asked to suggest a corrected email address.
    4. A record is stored in the email_bounces collection.

    A scheduler runs the scan every 5 minutes automatically.
    The scan can also be triggered manually via the API.
    """

    def __init__(self, db):
        self.db = db
        self.imap_host = os.environ.get('IMAP_HOST', '')
        self.imap_port = int(os.environ.get('IMAP_PORT', 993))
        self.llm_key = os.environ.get('EMERGENT_LLM_KEY', '')
        self.email_accounts: List[Dict] = []
        self.scheduler = AsyncIOScheduler()
        self._load_accounts()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _load_accounts(self):
        i = 1
        while True:
            username = os.getenv(f"EMAIL_{i}_USERNAME")
            password = os.getenv(f"EMAIL_{i}_PASSWORD")
            if not username or not password:
                break
            self.email_accounts.append({"username": username, "password": password})
            i += 1
        logger.info(f"InboxMonitor: loaded {len(self.email_accounts)} email accounts")

    # ------------------------------------------------------------------
    # Bounce detection helpers (all synchronous – run in executor)
    # ------------------------------------------------------------------

    def _is_bounce_message(self, from_header: str, subject: str) -> bool:
        from_lower = from_header.lower()
        subject_lower = subject.lower()
        for pattern in BOUNCE_FROM_PATTERNS:
            if pattern in from_lower:
                return True
        for pattern in BOUNCE_SUBJECT_PATTERNS:
            if pattern in subject_lower:
                return True
        return False

    def _decode_header_value(self, raw: str) -> str:
        parts = decode_header(raw or '')
        result = ''
        for part, enc in parts:
            if isinstance(part, bytes):
                result += part.decode(enc or 'utf-8', errors='ignore')
            else:
                result += str(part)
        return result

    def _extract_failed_recipients(self, msg) -> List[str]:
        """Extract failed recipient email addresses from a bounce message."""
        found: set = set()

        def _search_text(text: str):
            patterns = [
                r'Final-Recipient:\s*rfc822;\s*([^\s\n\r,>]+)',
                r'Original-Recipient:\s*rfc822;\s*([^\s\n\r,>]+)',
                r'X-Failed-Recipients:\s*([^\s\n\r,>]+)',
                r'failed to (?:send|deliver) (?:to|message to)\s+([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
                r'address(?:es)? rejected[:\s]+([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
                r'unknown user[:\s"]+([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
                r'no such (?:user|account)[:\s"]+([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    addr = match.group(1).strip().rstrip('.,;>').lower()
                    if re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', addr):
                        found.add(addr)

        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == 'message/delivery-status':
                    try:
                        payload = part.get_payload()
                        if isinstance(payload, list):
                            text = '\n'.join(str(p) for p in payload)
                        elif isinstance(payload, bytes):
                            text = payload.decode('utf-8', errors='ignore')
                        else:
                            text = str(payload)
                        _search_text(text)
                    except Exception:
                        pass
                elif ct in ('text/plain', 'text/html'):
                    try:
                        raw = part.get_payload(decode=True)
                        if raw:
                            _search_text(raw.decode('utf-8', errors='ignore'))
                    except Exception:
                        pass
        else:
            try:
                raw = msg.get_payload(decode=True)
                if raw:
                    _search_text(raw.decode('utf-8', errors='ignore'))
            except Exception:
                pass

        return list(found)

    def _scan_account_inbox(self, username: str, password: str) -> List[Tuple[str, str, List[str]]]:
        """
        Synchronous IMAP scan – intended to be called via run_in_executor.

        Returns a list of (message_uid, subject, [failed_email, ...]) tuples
        for every unread bounce message found in the inbox.
        """
        results: List[Tuple[str, str, List[str]]] = []

        if not self.imap_host:
            return results

        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(username, password)
            mail.select('INBOX', readonly=False)

            # Collect message UIDs from several targeted searches
            uid_set: set = set()
            for criteria in [
                'FROM "MAILER-DAEMON"',
                'FROM "postmaster"',
                'SUBJECT "delivery"',
                'SUBJECT "undeliverable"',
                'SUBJECT "returned"',
            ]:
                try:
                    status, data = mail.uid('search', None, criteria)
                    if status == 'OK' and data and data[0]:
                        for uid in data[0].split():
                            uid_set.add(uid)
                except Exception:
                    pass

            # Process up to 100 messages per account per scan
            for uid in list(uid_set)[:100]:
                try:
                    status, msg_data = mail.uid('fetch', uid, '(RFC822)')
                    if status != 'OK' or not msg_data or not msg_data[0]:
                        continue
                    raw_email = msg_data[0][1]
                    if not isinstance(raw_email, bytes):
                        continue

                    parsed = email.message_from_bytes(raw_email)
                    from_hdr = parsed.get('From', '')
                    subject = self._decode_header_value(parsed.get('Subject', ''))

                    if self._is_bounce_message(from_hdr, subject):
                        failed = self._extract_failed_recipients(parsed)
                        if failed:
                            msg_uid = parsed.get('Message-ID') or uid.decode()
                            results.append((msg_uid, subject, failed))
                            # Mark as seen so we don't re-process on the next scan
                            mail.uid('store', uid, '+FLAGS', '\\Seen')

                except Exception as exc:
                    logger.error(f"InboxMonitor: error parsing UID {uid} for {username}: {exc}")

            mail.close()
            mail.logout()

        except imaplib.IMAP4.error as exc:
            logger.error(f"InboxMonitor: IMAP error for {username}: {exc}")
        except Exception as exc:
            logger.error(f"InboxMonitor: unexpected error for {username}: {exc}")

        return results

    # ------------------------------------------------------------------
    # AI correction
    # ------------------------------------------------------------------

    async def _ai_suggest_correction(self, clinic_data: Dict, bounced_email: str) -> Optional[str]:
        """Ask GPT-4o-mini to suggest a corrected email address for a bounced address."""
        if not self.llm_key:
            return None

        try:
            clinic_name = clinic_data.get('clinica', '')
            website = clinic_data.get('website', '') or ''
            domain_hint = (
                website
                .replace('https://', '')
                .replace('http://', '')
                .replace('www.', '')
                .strip('/')
                .split('/')[0]
            )

            prompt = (
                f"El email '{bounced_email}' fue devuelto (no existe o tiene typo).\n\n"
                f"Clínica: {clinic_name}\n"
                f"Sitio web: {website or 'No disponible'}\n"
                f"Dominio detectado: {domain_hint or 'No disponible'}\n\n"
                "Sugiere la dirección de email correcta más probable.\n"
                "Patrones comunes: info@, contacto@, clinica@, recepcion@, admin@ + dominio.\n"
                "Si el email tiene un typo evidente (ej: infoo@, infp@), corrígelo.\n"
                "Si no puedes sugerir con alta confianza responde: NONE\n\n"
                "Responde SOLO con el email sugerido o NONE. Sin explicación."
            )

            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.llm_key}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50,
                }
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        suggestion = result["choices"][0]["message"]["content"].strip()
                        if suggestion.upper() == 'NONE' or not suggestion:
                            return None
                        suggestion = suggestion.lower().strip('<>"\' ')
                        if re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', suggestion):
                            return suggestion

        except Exception as exc:
            logger.error(f"InboxMonitor: AI suggestion error: {exc}")

        return None

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    async def _process_bounce(self, failed_email: str, source_account: str):
        """Record a detected bounce, mark clinic(s) and cancelled queue items."""
        try:
            # Skip if this email address has already been recorded
            if await self.db.email_bounces.find_one({"bounced_email": failed_email}):
                return

            clinics = await self.db.clinics.find({"email": failed_email}).to_list(20)

            await self.db.email_bounces.insert_one({
                "bounced_email": failed_email,
                "detected_at": datetime.utcnow(),
                "source_account": source_account,
                "clinic_ids": [str(c["_id"]) for c in clinics],
                "clinic_count": len(clinics),
            })

            for clinic in clinics:
                clinic_id = str(clinic["_id"])
                suggested_email = await self._ai_suggest_correction(clinic, failed_email)

                update_fields: Dict = {
                    "email_bounced": True,
                    "email_bounce_detected_at": datetime.utcnow(),
                    "email_bounce_source": source_account,
                }
                if suggested_email:
                    update_fields["email_suggested_correction"] = suggested_email

                await self.db.clinics.update_one(
                    {"_id": clinic["_id"]},
                    {"$set": update_fields},
                )

                # Cancel pending queue items for this clinic
                await self.db.email_queue.update_many(
                    {"clinic_id": clinic_id, "status": "pending"},
                    {"$set": {
                        "status": "bounced",
                        "bounce_detected_at": datetime.utcnow(),
                        "bounce_reason": "Email address invalid or does not exist",
                    }},
                )

                logger.info(
                    f"InboxMonitor: bounce recorded for {failed_email} "
                    f"(clinic: {clinic.get('clinica', 'Unknown')})"
                    + (f" – AI suggestion: {suggested_email}" if suggested_email else "")
                )

        except Exception as exc:
            logger.error(f"InboxMonitor: error processing bounce for {failed_email}: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def scan_all_inboxes(self) -> Dict:
        """Scan every configured email account inbox for bounce messages."""
        if not self.imap_host:
            logger.warning("InboxMonitor: IMAP_HOST not configured – scan skipped")
            return {"scanned": 0, "bounces_found": 0, "accounts_scanned": 0, "error": "IMAP_HOST not set"}

        total_bounces = 0
        accounts_scanned = 0

        for account in self.email_accounts:
            username = account.get("username", "")
            try:
                loop = asyncio.get_event_loop()
                results: List[Tuple[str, str, List[str]]] = await loop.run_in_executor(
                    None,
                    self._scan_account_inbox,
                    username,
                    account["password"],
                )
                accounts_scanned += 1

                for _msg_uid, _subject, failed_recipients in results:
                    for addr in failed_recipients:
                        await self._process_bounce(addr, username)
                        total_bounces += 1

                logger.info(
                    f"InboxMonitor: scanned {username} – "
                    f"{len(results)} bounce message(s) found"
                )

            except Exception as exc:
                logger.error(f"InboxMonitor: error scanning {username}: {exc}")

        return {
            "accounts_scanned": accounts_scanned,
            "bounces_found": total_bounces,
            "scan_time": datetime.utcnow().isoformat(),
        }

    async def get_bounce_stats(self) -> Dict:
        """Return aggregate statistics about detected bounces."""
        total_bounced = await self.db.clinics.count_documents({"email_bounced": True})
        with_suggestion = await self.db.clinics.count_documents({
            "email_bounced": True,
            "email_suggested_correction": {"$exists": True},
        })
        bounce_records = await self.db.email_bounces.count_documents({})
        queue_bounced = await self.db.email_queue.count_documents({"status": "bounced"})

        return {
            "total_bounced_clinics": total_bounced,
            "with_ai_suggestion": with_suggestion,
            "bounce_records": bounce_records,
            "queue_items_cancelled": queue_bounced,
        }

    async def get_bounced_clinics(self, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Return a paginated list of clinics whose email bounced."""
        projection = {
            "_id": 1,
            "clinica": 1,
            "ciudad": 1,
            "email": 1,
            "email_bounced": 1,
            "email_bounce_detected_at": 1,
            "email_suggested_correction": 1,
        }
        clinics = (
            await self.db.clinics
            .find({"email_bounced": True}, projection)
            .skip(skip)
            .limit(limit)
            .to_list(limit)
        )
        return clinics

    async def apply_email_correction(self, clinic_id: str) -> Dict:
        """Apply the AI-suggested email correction to a clinic and re-queue it."""
        from bson import ObjectId

        try:
            oid = ObjectId(clinic_id)
        except Exception:
            return {"success": False, "message": "Invalid clinic_id"}

        clinic = await self.db.clinics.find_one({"_id": oid})
        if not clinic:
            return {"success": False, "message": "Clinic not found"}

        suggested = clinic.get("email_suggested_correction")
        if not suggested:
            return {"success": False, "message": "No AI suggestion available for this clinic"}

        old_email = clinic.get("email", "")

        await self.db.clinics.update_one(
            {"_id": oid},
            {"$set": {
                "email": suggested,
                "email_bounced": False,
                "email_corrected_from": old_email,
                "email_corrected_at": datetime.utcnow(),
            }},
        )

        # Re-queue any previously cancelled items with the corrected address
        await self.db.email_queue.update_many(
            {"clinic_id": clinic_id, "status": "bounced"},
            {"$set": {
                "status": "pending",
                "attempts": 0,
                "clinic_data.email": suggested,
                "requeued_at": datetime.utcnow(),
            }},
        )

        logger.info(
            f"InboxMonitor: email corrected for {clinic.get('clinica')} "
            f"{old_email} → {suggested}"
        )

        return {
            "success": True,
            "old_email": old_email,
            "new_email": suggested,
            "message": "Email corrected and re-queued",
        }

    # ------------------------------------------------------------------
    # Scheduler lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Start the background inbox-monitor scheduler (every 5 minutes)."""
        if not self.imap_host:
            logger.warning("InboxMonitor: IMAP_HOST not set – scheduler not started")
            return

        self.scheduler.add_job(
            self.scan_all_inboxes,
            IntervalTrigger(minutes=5),
            id='inbox_monitor',
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("InboxMonitor: scheduler started – scanning inboxes every 5 minutes")

    def stop(self):
        """Stop the background scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("InboxMonitor: scheduler stopped")


# Singleton – will be properly initialised in server.py
inbox_monitor_service: Optional[InboxMonitorService] = None
