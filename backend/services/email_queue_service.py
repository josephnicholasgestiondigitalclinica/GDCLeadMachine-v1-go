import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

logger = logging.getLogger(__name__)

class EmailQueueService:
    def __init__(self, db):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.email_accounts = []
        self.interval_seconds = int(os.getenv("EMAIL_INTERVAL_SECONDS", 120))
        self.load_email_accounts()
    
    def load_email_accounts(self):
        """Load email accounts from environment"""
        accounts = []
        i = 1
        while True:
            username = os.getenv(f"EMAIL_{i}_USERNAME")
            password = os.getenv(f"EMAIL_{i}_PASSWORD")
            
            if not username or not password:
                break
            
            accounts.append({
                "username": username,
                "password": password,
                "last_sent": None
            })
            i += 1
        
        self.email_accounts = accounts
        logger.info(f"Loaded {len(accounts)} email accounts")
    
    async def add_email_account(self, username: str, password: str):
        """Add new email account"""
        self.email_accounts.append({
            "username": username,
            "password": password,
            "last_sent": None
        })
        
        # Save to database
        await self.db.email_accounts.insert_one({
            "username": username,
            "password": password,
            "added_at": datetime.utcnow()
        })
        
        logger.info(f"Added new email account: {username}")
    
    async def add_to_queue(self, clinic_id: str, clinic_data: Dict):
        """Add clinic to email queue"""
        try:
            queue_item = {
                "clinic_id": clinic_id,
                "clinic_data": clinic_data,
                "status": "pending",
                "attempts": 0,
                "added_at": datetime.utcnow(),
                "scheduled_for": None
            }
            
            await self.db.email_queue.insert_one(queue_item)
            logger.info(f"Added to email queue: {clinic_data.get('clinica')}")
            
        except Exception as e:
            logger.error(f"Error adding to queue: {str(e)}")
    
    async def get_next_available_account(self) -> Dict:
        """Get next email account that can send (respecting 120s interval)"""
        now = datetime.utcnow()
        
        for account in self.email_accounts:
            last_sent = account.get("last_sent")
            
            # If never sent or enough time has passed
            if not last_sent or (now - last_sent).total_seconds() >= self.interval_seconds:
                return account
        
        return None
    
    async def process_queue(self):
        """Process email queue - called by scheduler"""
        from services.email_service import email_service
        from services.notion_service import notion_service
        
        try:
            # Get next account available to send
            account = await self.get_next_available_account()
            
            if not account:
                logger.debug("No email accounts available (respecting rate limits)")
                return
            
            # Get next pending email from queue
            pending_email = await self.db.email_queue.find_one({
                "status": "pending",
                "attempts": {"$lt": 3}
            })
            
            if not pending_email:
                logger.debug("No pending emails in queue")
                return
            
            clinic_data = pending_email["clinic_data"]
            
            # Send email
            success = await email_service.send_email(
                to_email=clinic_data["email"],
                clinic_name=clinic_data["clinica"],
                from_email=account["username"],
                from_password=account["password"],
                personalization=clinic_data
            )
            
            if success:
                # Update queue item
                await self.db.email_queue.update_one(
                    {"_id": pending_email["_id"]},
                    {
                        "$set": {
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "sent_from": account["username"]
                        }
                    }
                )
                
                # Update clinic in Notion
                await notion_service.update_clinic(
                    pending_email["clinic_id"],
                    {
                        "estado": "Email enviado",
                        "email_sent": True,
                        "last_email_date": datetime.utcnow().isoformat()
                    }
                )
                
                # Update account last_sent time
                account["last_sent"] = datetime.utcnow()
                
                logger.info(f"Successfully sent email to {clinic_data['clinica']} from {account['username']}")
            else:
                # Increment attempts
                await self.db.email_queue.update_one(
                    {"_id": pending_email["_id"]},
                    {
                        "$inc": {"attempts": 1},
                        "$set": {"last_attempt": datetime.utcnow()}
                    }
                )
                logger.warning(f"Failed to send email to {clinic_data['clinica']}, attempt {pending_email['attempts'] + 1}")
                
        except Exception as e:
            logger.error(f"Error processing email queue: {str(e)}")
    
    def start(self):
        """Start the email scheduler"""
        # Run every 10 seconds to check if we can send
        self.scheduler.add_job(
            self.process_queue,
            IntervalTrigger(seconds=10),
            id='email_queue_processor',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Email queue scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Email queue scheduler stopped")

# This will be initialized in server.py
email_queue_service = None
