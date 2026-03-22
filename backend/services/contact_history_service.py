"""
Contact History Service
Tracks all contact attempts (Email, WhatsApp) with leads
Ensures database is always updated with contact information
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ContactHistoryService:
    """
    Manages contact history for all leads
    Records every email and WhatsApp interaction
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        logger.info("Contact History Service initialized")
    
    async def record_contact(
        self,
        clinic_id: str,
        method: str,  # "email" or "whatsapp"
        status: str,  # "sent", "failed", "pending"
        details: Dict = None
    ) -> Dict:
        """
        Record a contact attempt in history
        
        Args:
            clinic_id: ID of the clinic
            method: "email" or "whatsapp"
            status: "sent", "failed", "pending"
            details: Additional details (from_email, phone, message_id, etc.)
        
        Returns:
            Dict with success status
        """
        try:
            contact_record = {
                "clinic_id": clinic_id,
                "method": method,
                "status": status,
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().isoformat(),
                "time": datetime.utcnow().strftime("%H:%M:%S"),
                "details": details or {}
            }
            
            # Insert into contact_history collection
            result = await self.db.contact_history.insert_one(contact_record)
            
            # Update clinic document with latest contact info
            update_data = {
                f"last_contact_{method}": datetime.utcnow().isoformat(),
                f"{method}_sent": status == "sent",
                "last_contact_method": method,
                "last_contact_date": datetime.utcnow().isoformat(),
                "last_contact_status": status
            }
            
            # Update estado based on contact
            if status == "sent":
                if method == "email":
                    update_data["estado"] = "Email enviado"
                elif method == "whatsapp":
                    update_data["estado"] = "WhatsApp enviado"
            
            await self.db.clinics.update_one(
                {"_id": clinic_id},
                {"$set": update_data}
            )
            
            logger.info(f"Contact recorded: {method} - {status} for clinic {clinic_id}")
            
            return {
                "success": True,
                "contact_id": str(result.inserted_id),
                "timestamp": contact_record["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error recording contact: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_contact_history(
        self,
        clinic_id: str,
        method: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get contact history for a clinic
        
        Args:
            clinic_id: ID of the clinic
            method: Optional filter by method ("email" or "whatsapp")
            limit: Maximum number of records to return
        
        Returns:
            List of contact records
        """
        try:
            query = {"clinic_id": clinic_id}
            if method:
                query["method"] = method
            
            projection = {
                "method": 1,
                "status": 1,
                "timestamp": 1,
                "date": 1,
                "time": 1,
                "details": 1
            }
            
            contacts = await self.db.contact_history.find(
                query,
                projection
            ).sort("timestamp", -1).limit(limit).to_list(limit)
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error getting contact history: {str(e)}")
            return []
    
    async def get_clinic_stats(self, clinic_id: str) -> Dict:
        """
        Get contact statistics for a clinic
        
        Returns:
            Dict with email/whatsapp counts and last contact info
        """
        try:
            # Count contacts by method
            email_count = await self.db.contact_history.count_documents({
                "clinic_id": clinic_id,
                "method": "email",
                "status": "sent"
            })
            
            whatsapp_count = await self.db.contact_history.count_documents({
                "clinic_id": clinic_id,
                "method": "whatsapp",
                "status": "sent"
            })
            
            # Get last contact
            last_contact = await self.db.contact_history.find_one(
                {"clinic_id": clinic_id},
                sort=[("timestamp", -1)]
            )
            
            return {
                "total_contacts": email_count + whatsapp_count,
                "email_sent": email_count,
                "whatsapp_sent": whatsapp_count,
                "last_contact": {
                    "method": last_contact.get("method") if last_contact else None,
                    "date": last_contact.get("date") if last_contact else None,
                    "status": last_contact.get("status") if last_contact else None
                } if last_contact else None
            }
            
        except Exception as e:
            logger.error(f"Error getting clinic stats: {str(e)}")
            return {
                "total_contacts": 0,
                "email_sent": 0,
                "whatsapp_sent": 0,
                "last_contact": None
            }
    
    async def get_all_contacts_summary(self) -> Dict:
        """
        Get summary of all contacts in the system
        
        Returns:
            Dict with overall statistics
        """
        try:
            total_emails = await self.db.contact_history.count_documents({
                "method": "email",
                "status": "sent"
            })
            
            total_whatsapp = await self.db.contact_history.count_documents({
                "method": "whatsapp",
                "status": "sent"
            })
            
            pending_emails = await self.db.contact_history.count_documents({
                "method": "email",
                "status": "pending"
            })
            
            pending_whatsapp = await self.db.contact_history.count_documents({
                "method": "whatsapp",
                "status": "pending"
            })
            
            failed_contacts = await self.db.contact_history.count_documents({
                "status": "failed"
            })
            
            return {
                "total_sent": total_emails + total_whatsapp,
                "emails_sent": total_emails,
                "whatsapp_sent": total_whatsapp,
                "pending_emails": pending_emails,
                "pending_whatsapp": pending_whatsapp,
                "failed": failed_contacts
            }
            
        except Exception as e:
            logger.error(f"Error getting contacts summary: {str(e)}")
            return {
                "total_sent": 0,
                "emails_sent": 0,
                "whatsapp_sent": 0,
                "pending_emails": 0,
                "pending_whatsapp": 0,
                "failed": 0
            }

# This will be initialized in server.py
contact_history_service = None
