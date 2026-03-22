"""
WhatsApp Queue Service
Automated WhatsApp messaging with rate limiting
Similar to email queue but for WhatsApp messages
"""

import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class WhatsAppQueueService:
    def __init__(self, db):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        # WhatsApp rate limiting: 1 message every 60 seconds (faster than email)
        self.interval_seconds = int(os.getenv("WHATSAPP_INTERVAL_SECONDS", 60))
        self.last_sent = None
        self.enabled = bool(os.getenv("WHATSAPP_API_KEY"))
    
    async def add_to_queue(self, clinic_id: str, clinic_data: Dict):
        """Add clinic to WhatsApp queue"""
        try:
            # Only queue if clinic has phone number
            if not clinic_data.get('telefono'):
                logger.debug(f"Skipping WhatsApp queue for {clinic_data.get('clinica')} - no phone")
                return
            
            queue_item = {
                "clinic_id": clinic_id,
                "clinic_data": clinic_data,
                "status": "pending",
                "attempts": 0,
                "added_at": datetime.utcnow(),
                "scheduled_for": None
            }
            
            await self.db.whatsapp_queue.insert_one(queue_item)
            logger.info(f"Added to WhatsApp queue: {clinic_data.get('clinica')}")
            
        except Exception as e:
            logger.error(f"Error adding to WhatsApp queue: {str(e)}")
    
    async def can_send_now(self) -> bool:
        """Check if enough time has passed since last send"""
        if not self.last_sent:
            return True
        
        now = datetime.utcnow()
        elapsed = (now - self.last_sent).total_seconds()
        return elapsed >= self.interval_seconds
    
    async def process_queue(self):
        """Process WhatsApp queue - called by scheduler"""
        from services.whatsapp_service import whatsapp_service
        from services.contact_history_service import contact_history_service
        
        try:
            # Check if we can send
            if not await self.can_send_now():
                logger.debug("WhatsApp rate limit active, waiting...")
                return
            
            # Get next pending WhatsApp from queue
            projection = {
                "_id": 1,
                "clinic_id": 1,
                "clinic_data": 1,
                "attempts": 1,
                "status": 1
            }
            
            pending_whatsapp = await self.db.whatsapp_queue.find_one({
                "status": "pending",
                "attempts": {"$lt": 3}
            }, projection)
            
            if not pending_whatsapp:
                logger.debug("No pending WhatsApp messages in queue")
                return
            
            clinic_data = pending_whatsapp["clinic_data"]
            clinic_id = pending_whatsapp["clinic_id"]
            
            # Send WhatsApp message
            result = await whatsapp_service.send_whatsapp_message(
                to_phone=clinic_data["telefono"],
                clinic_name=clinic_data["clinica"]
            )
            
            if result.get("success"):
                # Update queue item
                await self.db.whatsapp_queue.update_one(
                    {"_id": pending_whatsapp["_id"]},
                    {
                        "$set": {
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "method": result.get("method"),
                            "message_id": result.get("message_id") or result.get("whatsapp_link")
                        }
                    }
                )
                
                # Record in contact history
                if contact_history_service:
                    await contact_history_service.record_contact(
                        clinic_id=clinic_id,
                        method="whatsapp",
                        status="sent",
                        details={
                            "phone": clinic_data["telefono"],
                            "message_id": result.get("message_id"),
                            "api_method": result.get("method"),
                            "link": result.get("whatsapp_link")
                        }
                    )
                
                # Update last_sent time
                self.last_sent = datetime.utcnow()
                
                logger.info(f"Successfully sent WhatsApp to {clinic_data['clinica']}")
            else:
                # Increment attempts
                await self.db.whatsapp_queue.update_one(
                    {"_id": pending_whatsapp["_id"]},
                    {
                        "$inc": {"attempts": 1},
                        "$set": {"last_attempt": datetime.utcnow()}
                    }
                )
                
                # Record failed attempt
                if contact_history_service:
                    await contact_history_service.record_contact(
                        clinic_id=clinic_id,
                        method="whatsapp",
                        status="failed",
                        details={
                            "phone": clinic_data["telefono"],
                            "error": result.get("error"),
                            "attempt": pending_whatsapp["attempts"] + 1
                        }
                    )
                
                logger.warning(f"Failed to send WhatsApp to {clinic_data['clinica']}, attempt {pending_whatsapp['attempts'] + 1}")
                
        except Exception as e:
            logger.error(f"Error processing WhatsApp queue: {str(e)}")
    
    def start(self):
        """Start the WhatsApp queue scheduler"""
        if not self.enabled:
            logger.info("WhatsApp queue not started - API key not configured")
            return
        
        # Run every 15 seconds to check if we can send
        self.scheduler.add_job(
            self.process_queue,
            IntervalTrigger(seconds=15),
            id='whatsapp_queue_processor',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("WhatsApp queue scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("WhatsApp queue scheduler stopped")
    
    async def get_queue_stats(self) -> Dict:
        """Get WhatsApp queue statistics"""
        try:
            pending = await self.db.whatsapp_queue.count_documents({"status": "pending"})
            sent = await self.db.whatsapp_queue.count_documents({"status": "sent"})
            failed = await self.db.whatsapp_queue.count_documents({"status": "failed"})
            
            return {
                "pending": pending,
                "sent": sent,
                "failed": failed,
                "total": pending + sent + failed
            }
        except Exception as e:
            logger.error(f"Error getting queue stats: {str(e)}")
            return {"pending": 0, "sent": 0, "failed": 0, "total": 0}

# This will be initialized in server.py
whatsapp_queue_service = None
