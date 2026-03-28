from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
import uuid
import asyncio
import time
from datetime import datetime
from bson import ObjectId

# Load environment variables before importing services.
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR.parent / '.env')
load_dotenv(ROOT_DIR / '.env')
load_dotenv(ROOT_DIR.parent / '.env.example')

# Import services
from services.notion_service import notion_service
from services.ai_scoring_service import ai_scoring_service
from services.email_service import email_service
from services.email_queue_service import EmailQueueService
from services.automation_service import automation_service
from services.discovery_scheduler import DiscoveryScheduler
from services.inbox_monitor_service import InboxMonitorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lightweight in-process cache for high-frequency stats endpoints.
_response_cache: Dict[str, Dict[str, Any]] = {}


def _cache_get(key: str, ttl_seconds: int):
    entry = _response_cache.get(key)
    if not entry:
        return None
    if (time.time() - entry["ts"]) > ttl_seconds:
        return None
    return entry["value"]


def _cache_set(key: str, value: Any):
    _response_cache[key] = {
        "ts": time.time(),
        "value": value,
    }

# Helper function to convert ObjectIds to strings
def convert_objectids(obj):
    """Recursively convert ObjectId fields to strings for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectids(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(item) for item in obj]
    else:
        return obj

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
from services.contact_history_service import ContactHistoryService
from services.whatsapp_queue_service import WhatsAppQueueService

email_queue_service_instance = EmailQueueService(db)
whatsapp_queue_service_instance = WhatsAppQueueService(db)
contact_history_service_instance = ContactHistoryService(db)
inbox_monitor_service_instance = InboxMonitorService(db)

automation_service.initialize(
    db, 
    email_queue_service_instance,
    whatsapp_queue_service_instance,
    contact_history_service_instance
)
discovery_scheduler_instance = DiscoveryScheduler(automation_service, db)

from services.test_run_service import TestRunService
test_run_service_instance = TestRunService(db)

# Create the main app
app = FastAPI(title="GDC Lead Management System")
api_router = APIRouter(prefix="/api")

# Models
class ClinicCreate(BaseModel):
    clinica: str
    ciudad: str
    email: str
    telefono: Optional[str] = ""
    website: Optional[str] = ""

class ClinicBulkImport(BaseModel):
    clinics: List[ClinicCreate]
    source: Optional[str] = "Bulk Import"

class EmailAccount(BaseModel):
    username: str
    password: str

class EmailStats(BaseModel):
    total_sent: int
    pending: int
    failed: int
    active_accounts: int

from services.whatsapp_service import whatsapp_service

# WhatsApp endpoints
@api_router.post("/whatsapp/send")
async def send_whatsapp(clinic_id: str):
    """Send WhatsApp message to a specific clinic"""
    try:
        # Get clinic data
        clinic = await db.clinics.find_one({"_id": clinic_id})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        if not clinic.get('telefono'):
            raise HTTPException(status_code=400, detail="Clinic has no phone number")
        
        result = await whatsapp_service.send_whatsapp_message(
            clinic['telefono'],
            clinic['clinica']
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/whatsapp/bulk")
async def send_bulk_whatsapp(score_threshold: int = 7):
    """Send WhatsApp messages to leads with high scores"""
    try:
        # Get high-scoring leads with phone numbers
        leads = await db.clinics.find({
            "score": {"$gte": score_threshold},
            "telefono": {"$exists": True, "$ne": ""}
        }).limit(50).to_list(50)
        
        if not leads:
            return {"message": "No leads found with phone numbers"}
        
        result = await whatsapp_service.send_bulk_whatsapp(leads)
        
        return {
            "message": "WhatsApp messages prepared",
            "success": result['success'],
            "failed": result['failed'],
            "links": result.get('links', [])
        }
    except Exception as e:
        logger.error(f"Error sending bulk WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@api_router.get("/")
async def root():
    return {"message": "GDC Lead Management System API", "status": "running"}

# Clinic endpoints
@api_router.post("/clinics")
async def create_clinic(clinic: ClinicCreate):
    """Add new clinic - triggers automated scoring and queuing"""
    try:
        result = await automation_service.process_new_clinic(
            clinic.dict(),
            source="Manual"
        )
        return result
    except Exception as e:
        logger.error(f"Error creating clinic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/clinics/bulk")
async def bulk_import_clinics(bulk_data: ClinicBulkImport):
    """Bulk import clinics - processes all automatically"""
    try:
        results = await automation_service.batch_process_clinics(
            [c.dict() for c in bulk_data.clinics],
            bulk_data.source
        )
        return results
    except Exception as e:
        logger.error(f"Error bulk importing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/clinics")
async def get_clinics(skip: int = 0, limit: int = 100, comunidad: Optional[str] = None):
    """Get clinics from database, optionally filtered by Comunidad Autónoma"""
    try:
        filter_dict = {}
        if comunidad:
            filter_dict["comunidad_autonoma"] = comunidad
        
        # Optimized query with projection to fetch only needed fields
        projection = {
            "_id": 1, 
            "clinica": 1, 
            "ciudad": 1, 
            "email": 1, 
            "telefono": 1, 
            "website": 1, 
            "score": 1, 
            "estado": 1, 
            "comunidad_autonoma": 1,
            "scoring_details": 1,
            "fuente": 1
        }
        
        clinics = await db.clinics.find(filter_dict, projection).skip(skip).limit(limit).to_list(limit)
        total = await db.clinics.count_documents(filter_dict)
        
        # Convert ObjectIds to strings
        clinics = convert_objectids(clinics)
        
        return {
            "clinics": clinics,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting clinics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/clinics/{clinic_id}/score")
async def score_clinic(clinic_id: str):
    """Manually trigger scoring for a clinic"""
    try:
        clinic = await db.clinics.find_one({"_id": clinic_id})
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        result = await ai_scoring_service.score_clinic(clinic)
        
        # Update in database
        await db.clinics.update_one(
            {"_id": clinic_id},
            {"$set": {"score": result["score"], "scoring_details": result["details"]}}
        )
        
        return result
    except Exception as e:
        logger.error(f"Error scoring clinic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Email management endpoints
@api_router.post("/email-accounts")
async def add_email_account(account: EmailAccount):
    """Add new email account for sending"""
    try:
        await email_queue_service_instance.add_email_account(
            account.username,
            account.password
        )
        return {"message": "Email account added successfully"}
    except Exception as e:
        logger.error(f"Error adding email account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/email-accounts")
async def get_email_accounts():
    """Get list of email accounts (passwords hidden)"""
    accounts = [
        {"username": acc["username"], "last_sent": acc.get("last_sent")}
        for acc in email_queue_service_instance.email_accounts
    ]
    return {"accounts": accounts}

@api_router.get("/email/stats")
async def get_email_stats():
    """Get email statistics"""
    try:
        cached = _cache_get("email_stats", ttl_seconds=5)
        if cached is not None:
            return cached

        total_sent, pending, failed = await asyncio.gather(
            db.email_queue.count_documents({"status": "sent"}),
            db.email_queue.count_documents({"status": "pending"}),
            db.email_queue.count_documents({"status": "failed"}),
        )

        payload = {
            "total_sent": total_sent,
            "pending": pending,
            "failed": failed,
            "active_accounts": len(email_queue_service_instance.email_accounts)
        }
        _cache_set("email_stats", payload)
        return payload
    except Exception as e:
        logger.error(f"Error getting email stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/email/queue")
async def get_email_queue(status: Optional[str] = None):
    """Get email queue"""
    try:
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        # Optimized query with projection to fetch only needed fields
        projection = {
            "_id": 1,
            "clinic_id": 1,
            "status": 1,
            "added_at": 1,
            "sent_at": 1,
            "attempts": 1,
            "clinic_data": 1
        }
        
        queue_items = await db.email_queue.find(filter_dict, projection).limit(100).to_list(100)
        
        # Convert ObjectIds to strings
        queue_items = convert_objectids(queue_items)
        
        return {"queue": queue_items}
    except Exception as e:
        logger.error(f"Error getting queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/email/attachments")
async def upload_attachment(file: UploadFile = File(...)):
    """Upload PDF attachment for emails"""
    try:
        # Save file
        file_path = f"/tmp/attachments/{uuid.uuid4()}_{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Save to database
        attachment_doc = {
            "filename": file.filename,
            "path": file_path,
            "uploaded_at": datetime.utcnow()
        }
        result = await db.attachments.insert_one(attachment_doc)
        
        return {
            "message": "Attachment uploaded",
            "id": str(result.inserted_id),
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Error uploading attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard stats
@api_router.get("/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        cached = _cache_get("dashboard_stats", ttl_seconds=10)
        if cached is not None:
            return cached

        (
            total_leads,
            emails_sent,
            responded,
            clients,
            high_score,
            pending_followups,
        ) = await asyncio.gather(
            db.clinics.count_documents({}),
            db.email_queue.count_documents({"status": "sent"}),
            db.clinics.count_documents({"estado": "Respondió"}),
            db.clinics.count_documents({"estado": "Cliente"}),
            db.clinics.count_documents({"score": {"$gte": 7}}),
            db.clinics.count_documents({"estado": "Seguimiento pendiente"}),
        )
        
        # Group by Comunidad Autónoma
        by_region = await db.clinics.aggregate([
            {"$group": {"_id": "$comunidad_autonoma", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]).to_list(20)
        
        payload = {
            "total_leads": total_leads,
            "emails_sent": emails_sent,
            "responded": responded,
            "clients": clients,
            "high_score": high_score,
            "pending_followups": pending_followups,
            "response_rate": round((responded / emails_sent * 100) if emails_sent > 0 else 0, 2),
            "by_region": by_region
        }
        _cache_set("dashboard_stats", payload)
        return payload
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/discovery/trigger")
async def trigger_discovery():
    """Manually trigger lead discovery with Google Places API"""
    try:
        # Run discovery in background
        asyncio.create_task(discovery_scheduler_instance.run_discovery_cycle())
        google_enabled = discovery_scheduler_instance.google_api_enabled
        return {
            "message": "Lead discovery triggered" + (" with Google Places API!" if google_enabled else ""),
            "status": "running",
            "google_places_enabled": google_enabled
        }
    except Exception as e:
        logger.error(f"Error triggering discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/discovery/status")
async def get_discovery_status():
    """Get lead discovery status"""
    return {
        "is_running": discovery_scheduler_instance.is_running,
        "scheduler_running": discovery_scheduler_instance.scheduler.running,
        "google_places_enabled": discovery_scheduler_instance.google_api_enabled,
        "cumulative_new_clinics_discovered": discovery_scheduler_instance.total_new_clinics_discovered,
        "cumulative_leads_processed": discovery_scheduler_instance.total_leads_processed,
        "last_cycle_new_clinics": discovery_scheduler_instance.last_cycle_new_clinics,
        "last_cycle_at": (
            discovery_scheduler_instance.last_cycle_at.isoformat()
            if discovery_scheduler_instance.last_cycle_at
            else None
        ),
    }

@api_router.post("/discovery/google-places")
async def trigger_google_places_discovery(max_leads: int = 50):
    """Manually trigger Google Places API discovery only"""
    try:
        if not discovery_scheduler_instance.google_api_enabled:
            raise HTTPException(status_code=400, detail="Google API key not configured")
        
        # Run Google discovery
        new_leads = await discovery_scheduler_instance.run_google_discovery(max_leads=max_leads)
        
        return {
            "success": True,
            "message": f"Google Places discovery completed",
            "new_leads_found": new_leads
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google Places discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# PDF Lead Import endpoint
@api_router.post("/leads/import-pdf")
async def import_pdf_leads(pdf_data: List[dict]):
    """
    Import leads from PDF extraction data.
    Expects a list of clinic objects with: clinic_name, city, address, phone_numbers, email
    """
    try:
        from services.pdf_lead_processor import get_pdf_processor
        processor = get_pdf_processor(db)
        
        stats = await processor.process_pdf_data(pdf_data)
        
        return {
            "success": True,
            "message": f"PDF import completed",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error importing PDF leads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/status")
async def get_automation_status():
    """Get full 24/7 automation status"""
    try:
        cached = _cache_get("automation_status", ttl_seconds=5)
        if cached is not None:
            return cached

        # Get queue counts
        (
            email_pending,
            email_sent,
            email_failed,
            whatsapp_pending,
            whatsapp_sent,
            total_leads,
            pending_leads,
            in_queue,
        ) = await asyncio.gather(
            db.email_queue.count_documents({"status": "pending"}),
            db.email_queue.count_documents({"status": "sent"}),
            db.email_queue.count_documents({"status": "failed"}),
            db.whatsapp_queue.count_documents({"status": "pending"}),
            db.whatsapp_queue.count_documents({"status": "sent"}),
            db.clinics.count_documents({}),
            db.clinics.count_documents({"estado": "Sin contactar"}),
            db.clinics.count_documents({"estado": "En cola de contacto"}),
        )
        
        # Get scheduler jobs
        jobs = []
        for job in discovery_scheduler_instance.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            })
        
        payload = {
            "automation_active": True,
            "google_places_api": {
                "enabled": discovery_scheduler_instance.google_api_enabled,
                "status": "ACTIVE - Real lead discovery!" if discovery_scheduler_instance.google_api_enabled else "Not configured"
            },
            "discovery": {
                "is_running": discovery_scheduler_instance.is_running,
                "scheduler_active": discovery_scheduler_instance.scheduler.running,
                "scheduled_jobs": jobs,
                "mode": "24/7 Automated - Every hour for 20 minutes"
            },
            "email_queue": {
                "pending": email_pending,
                "sent": email_sent,
                "failed": email_failed,
                "interval": f"{email_queue_service_instance.interval_seconds} seconds",
                "accounts_active": len(email_queue_service_instance.email_accounts)
            },
            "whatsapp_queue": {
                "pending": whatsapp_pending,
                "sent": whatsapp_sent
            },
            "leads": {
                "total": total_leads,
                "pending_contact": pending_leads,
                "in_queue": in_queue
            }
        }
        _cache_set("automation_status", payload)
        return payload
    except Exception as e:
        logger.error(f"Error getting automation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notion/status")
async def get_notion_status():
    """Check Notion integration status"""
    try:
        status = await notion_service.test_connection()
        
        # Also try to get database info
        if status.get("connection_working"):
            schema = await notion_service.get_database_schema()
            if schema:
                status["database_title"] = schema.get("title", [{}])[0].get("plain_text", "Unknown")
                status["properties"] = list(schema.get("properties", {}).keys())
                # Check if it's a synced database
                if schema.get("is_inline"):
                    status["warning"] = "This is an inline database which may have restrictions"
        
        return status
    except Exception as e:
        logger.error(f"Error checking Notion status: {str(e)}")
        return {
            "configured": False,
            "connection_working": False,
            "message": f"Error: {str(e)}"
        }

@api_router.post("/notion/sync-all")
async def sync_all_leads_to_notion(limit: int = 50):
    """Sync existing leads to Notion (batch operation)"""
    try:
        if not notion_service.is_configured:
            raise HTTPException(status_code=400, detail="Notion not configured")
        
        # Get leads not yet synced to Notion
        leads = await db.clinics.find({
            "notion_page_id": {"$exists": False},
            "score": {"$gte": 5}
        }).limit(limit).to_list(limit)
        
        synced = 0
        failed = 0
        
        for lead in leads:
            try:
                lead_data = {
                    "clinica": lead.get("clinica", ""),
                    "ciudad": lead.get("ciudad", ""),
                    "email": lead.get("email", ""),
                    "telefono": lead.get("telefono", ""),
                    "score": lead.get("score"),
                    "estado": lead.get("estado", "Sin contactar"),
                    "website": lead.get("website", ""),
                    "fuente": lead.get("fuente", "Import")
                }
                
                page_id = await notion_service.add_clinic(lead_data)
                
                if page_id:
                    await db.clinics.update_one(
                        {"_id": lead["_id"]},
                        {"$set": {"notion_page_id": page_id}}
                    )
                    synced += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Error syncing lead to Notion: {str(e)}")
                failed += 1
        
        return {
            "success": True,
            "synced": synced,
            "failed": failed,
            "message": f"Synced {synced} leads to Notion"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch Notion sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Contact History endpoints
@api_router.get("/contacts/history/{clinic_id}")
async def get_clinic_contact_history(clinic_id: str, method: Optional[str] = None):
    """Get contact history for a specific clinic"""
    try:
        history = await contact_history_service_instance.get_contact_history(
            clinic_id=clinic_id,
            method=method
        )
        
        stats = await contact_history_service_instance.get_clinic_stats(clinic_id)
        
        return {
            "clinic_id": clinic_id,
            "history": history,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting contact history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/contacts/summary")
async def get_contacts_summary():
    """Get overall contact statistics"""
    try:
        cached = _cache_get("contacts_summary", ttl_seconds=5)
        if cached is not None:
            return cached

        summary = await contact_history_service_instance.get_all_contacts_summary()
        
        # Get queue stats
        pending, sent, failed = await asyncio.gather(
            db.email_queue.count_documents({"status": "pending"}),
            db.email_queue.count_documents({"status": "sent"}),
            db.email_queue.count_documents({"status": "failed"}),
        )
        email_stats = {
            "pending": pending,
            "sent": sent,
            "failed": failed,
        }
        
        whatsapp_stats = await whatsapp_queue_service_instance.get_queue_stats()
        
        payload = {
            "contact_summary": summary,
            "email_queue": email_stats,
            "whatsapp_queue": whatsapp_stats
        }
        _cache_set("contacts_summary", payload)
        return payload
    except Exception as e:
        logger.error(f"Error getting contacts summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/contacts/recent")
async def get_recent_contacts(limit: int = 50, method: Optional[str] = None):
    """Get recent contact attempts across all clinics"""
    try:
        query = {}
        if method:
            query["method"] = method
        
        projection = {
            "clinic_id": 1,
            "method": 1,
            "status": 1,
            "timestamp": 1,
            "date": 1,
            "time": 1,
            "details": 1
        }
        
        contacts = await db.contact_history.find(
            query,
            projection
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Convert ObjectIds
        contacts = convert_objectids(contacts)
        
        return {
            "contacts": contacts,
            "count": len(contacts)
        }
    except Exception as e:
        logger.error(f"Error getting recent contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Inbox monitor / bounce detection endpoints

@api_router.get("/email/bounces")
async def get_bounced_emails(skip: int = 0, limit: int = 50):
    """List clinics whose outbound emails bounced back (invalid / non-existent address)"""
    try:
        clinics = await inbox_monitor_service_instance.get_bounced_clinics(skip=skip, limit=limit)
        stats = await inbox_monitor_service_instance.get_bounce_stats()
        clinics = convert_objectids(clinics)
        return {
            "bounced_clinics": clinics,
            "count": len(clinics),
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Error fetching bounce list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/email/bounces/scan")
async def trigger_bounce_scan():
    """Manually trigger an IMAP inbox scan to detect new bounce messages"""
    try:
        result = await inbox_monitor_service_instance.scan_all_inboxes()
        return {
            "message": "Inbox scan completed",
            "result": result,
        }
    except Exception as e:
        logger.error(f"Error during bounce scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/email/bounces/{clinic_id}/fix")
async def apply_bounce_correction(clinic_id: str):
    """Apply the AI-suggested email correction for a bounced clinic and re-queue the email"""
    try:
        result = await inbox_monitor_service_instance.apply_email_correction(clinic_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying bounce correction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Test-Run endpoints  (/api/test-run/...)
# ---------------------------------------------------------------------------

class TestRunStartRequest(BaseModel):
    duration_hours: float = 2.0
    notes: Optional[str] = None


@api_router.post("/test-run/start")
async def start_test_run(body: TestRunStartRequest):
    """
    Start a timed test run.  The service records a baseline snapshot of
    key counters (total clinics, emails sent) and then auto-finishes after
    *duration_hours* (default 2 h).  A report is saved to MongoDB.

    Only one run can be active at a time.
    """
    try:
        result = await test_run_service_instance.start_test_run(
            duration_hours=body.duration_hours,
            notes=body.notes,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error(f"Error starting test run: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@api_router.get("/test-run/status")
async def get_test_run_status():
    """
    Return live status of the currently active test run (or the most recent
    one).  Shows elapsed / remaining time and a live delta of new clinics
    found and emails sent so far.
    """
    try:
        return await test_run_service_instance.get_status()
    except Exception as exc:
        logger.error(f"Error getting test run status: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@api_router.post("/test-run/finish")
async def finish_test_run():
    """
    Manually finish the active test run early and retrieve the final report.
    """
    try:
        return await test_run_service_instance.finish_test_run()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error(f"Error finishing test run: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@api_router.get("/test-run/report/{run_id}")
async def get_test_run_report(run_id: str):
    """Retrieve the saved report for a specific run_id."""
    try:
        report = await test_run_service_instance.get_report(run_id)
        if report is None:
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
        return report
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error fetching test run report: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@api_router.get("/test-run/history")
async def get_test_run_history(limit: int = 20):
    """List past test runs, most recent first."""
    try:
        return await test_run_service_instance.list_runs(limit=limit)
    except Exception as exc:
        logger.error(f"Error listing test run history: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# /mcp  – Model Context Protocol manifest endpoint
# ---------------------------------------------------------------------------

@app.get("/mcp")
async def mcp_manifest():
    """
    MCP (Model Context Protocol) manifest endpoint.

    Returns a JSON description of the tools this service exposes so that
    an MCP-compatible client (e.g. Emergent platform) can auto-discover
    capabilities and wire them into an AI agent.
    """
    base_url = "/api"
    return {
        "schema_version": "v1",
        "name": "GDC LeadMachine",
        "description": (
            "24/7 automated lead discovery, AI scoring, and email outreach "
            "for Spanish health clinics (dental, physio, ophthalmology, "
            "dermatology, psychology, medical centres, veterinary)."
        ),
        "tools": [
            {
                "name": "get_dashboard_stats",
                "description": "Get overall system stats: total leads, emails sent, response rate.",
                "method": "GET",
                "path": f"{base_url}/stats/dashboard",
            },
            {
                "name": "trigger_discovery",
                "description": "Manually trigger a lead discovery cycle using Google Places API.",
                "method": "POST",
                "path": f"{base_url}/discovery/trigger",
            },
            {
                "name": "get_automation_status",
                "description": "Get full 24/7 automation pipeline status (discovery, email queue, leads).",
                "method": "GET",
                "path": f"{base_url}/automation/status",
            },
            {
                "name": "start_test_run",
                "description": (
                    "Start a timed test run (default 2 hours). "
                    "Records baseline stats and auto-generates a report "
                    "showing new clinics found and emails sent."
                ),
                "method": "POST",
                "path": f"{base_url}/test-run/start",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "duration_hours": {
                            "type": "number",
                            "default": 2.0,
                            "description": "How long the test run should last in hours.",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional free-text notes for this run.",
                        },
                    },
                },
            },
            {
                "name": "get_test_run_status",
                "description": "Check live progress of the current test run.",
                "method": "GET",
                "path": f"{base_url}/test-run/status",
            },
            {
                "name": "finish_test_run",
                "description": "Manually finish the active test run and retrieve the final report.",
                "method": "POST",
                "path": f"{base_url}/test-run/finish",
            },
            {
                "name": "get_test_run_report",
                "description": "Get the saved report for a specific run_id.",
                "method": "GET",
                "path": f"{base_url}/test-run/report/{{run_id}}",
            },
            {
                "name": "list_test_run_history",
                "description": "List past test runs, most recent first.",
                "method": "GET",
                "path": f"{base_url}/test-run/history",
            },
            {
                "name": "get_email_stats",
                "description": "Get email queue statistics (total sent, pending, failed).",
                "method": "GET",
                "path": f"{base_url}/email/stats",
            },
            {
                "name": "list_clinics",
                "description": "Get paginated list of clinics with optional region filter.",
                "method": "GET",
                "path": f"{base_url}/clinics",
            },
        ],
    }


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Start email queue processor and lead discovery on startup"""
    logger.info("Starting GDC Lead Management System...")

    # Validate key environment variables at startup so misconfiguration
    # is surfaced immediately rather than silently failing at runtime.
    # Note: MONGO_URL and DB_NAME are already accessed with hard brackets
    # above (raising KeyError on startup if missing); the check here adds
    # a friendly warning for the remaining recommended variables.
    recommended_env_vars = [
        "BUSINESS_NAME",
        "BUSINESS_EMAIL",
        "EMAIL_1_USERNAME",
        "EMERGENT_LLM_KEY",
    ]
    missing = [v for v in recommended_env_vars if not os.environ.get(v)]
    if missing:
        logger.warning(
            f"⚠️  Missing recommended environment variables: {', '.join(missing)}. "
            "Some features may not work correctly."
        )
    
    # Create database indexes for query optimization
    try:
        logger.info("Creating database indexes...")
        await db.email_queue.create_index([("status", 1), ("attempts", 1)])
        await db.email_queue.create_index([("status", 1), ("clinic_data.email_verified", 1), ("attempts", 1)])
        await db.email_queue.create_index([("clinic_id", 1)])
        await db.whatsapp_queue.create_index([("status", 1), ("attempts", 1)])
        await db.contact_history.create_index([("clinic_id", 1), ("timestamp", -1)])
        await db.contact_history.create_index([("method", 1), ("status", 1)])
        await db.clinics.create_index([("comunidad_autonoma", 1)])
        await db.clinics.create_index([("score", 1)])
        await db.clinics.create_index([("estado", 1)])
        await db.clinics.create_index([("estado", 1), ("email_verified", 1)])
        await db.clinics.create_index([("email_bounced", 1)])
        await db.email_bounces.create_index([("bounced_email", 1)], unique=True)
        # Index for test run lookups
        await db.test_runs.create_index([("run_id", 1)], unique=True)
        await db.test_runs.create_index([("started_at", -1)])
        await db.test_runs.create_index([("status", 1)])
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning (may already exist): {str(e)}")
    
    email_queue_service_instance.start()
    logger.info("Email queue processor started - sending 1 email per 120 seconds per account")
    
    # Start WhatsApp queue processor
    whatsapp_queue_service_instance.start()
    logger.info("WhatsApp queue processor started - sending 1 message per 60 seconds")
    
    # Start inbox monitor - detects bounced emails every 5 minutes
    inbox_monitor_service_instance.start()
    
    # Start lead discovery scheduler - 24/7 MODE
    discovery_scheduler_instance.start()
    logger.info("="*60)
    logger.info("🚀 24/7 AUTOMATION ACTIVE")
    logger.info("📧 Email sending: Every 120 seconds")
    logger.info("📱 WhatsApp sending: Every 60 seconds") 
    logger.info("🔍 Lead processing: Every hour for 20 minutes")
    logger.info("📬 Inbox monitor: Every 5 minutes (bounce detection)")
    logger.info("🌙 System works while you sleep!")
    logger.info("⏱️  Test runs available at POST /api/test-run/start")
    logger.info("🔌 MCP manifest available at GET /mcp")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Stop email queue processor and discovery scheduler on shutdown"""
    email_queue_service_instance.stop()
    whatsapp_queue_service_instance.stop()
    inbox_monitor_service_instance.stop()
    discovery_scheduler_instance.stop()
    client.close()
    logger.info("Shutdown complete")
