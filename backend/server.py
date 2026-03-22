from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging
import uuid
import asyncio
from datetime import datetime
from bson import ObjectId

# Import services
from services.notion_service import notion_service
from services.ai_scoring_service import ai_scoring_service
from services.email_service import email_service
from services.email_queue_service import EmailQueueService
from services.automation_service import automation_service
from services.discovery_scheduler import DiscoveryScheduler

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
email_queue_service_instance = EmailQueueService(db)
automation_service.initialize(db, email_queue_service_instance)
discovery_scheduler_instance = DiscoveryScheduler(automation_service, db)

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
        total_sent = await db.email_queue.count_documents({"status": "sent"})
        pending = await db.email_queue.count_documents({"status": "pending"})
        failed = await db.email_queue.count_documents({"status": "failed"})
        
        return {
            "total_sent": total_sent,
            "pending": pending,
            "failed": failed,
            "active_accounts": len(email_queue_service_instance.email_accounts)
        }
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
        total_leads = await db.clinics.count_documents({})
        emails_sent = await db.email_queue.count_documents({"status": "sent"})
        responded = await db.clinics.count_documents({"estado": "Respondió"})
        clients = await db.clinics.count_documents({"estado": "Cliente"})
        high_score = await db.clinics.count_documents({"score": {"$gte": 7}})
        pending_followups = await db.clinics.count_documents({"estado": "Seguimiento pendiente"})
        
        # Group by Comunidad Autónoma
        by_region = await db.clinics.aggregate([
            {"$group": {"_id": "$comunidad_autonoma", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]).to_list(20)
        
        return {
            "total_leads": total_leads,
            "emails_sent": emails_sent,
            "responded": responded,
            "clients": clients,
            "high_score": high_score,
            "pending_followups": pending_followups,
            "response_rate": round((responded / emails_sent * 100) if emails_sent > 0 else 0, 2),
            "by_region": by_region
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/discovery/trigger")
async def trigger_discovery():
    """Manually trigger REAL lead discovery with web scraping"""
    try:
        # Run discovery in background
        asyncio.create_task(discovery_scheduler_instance.run_discovery_cycle())
        return {"message": "REAL lead discovery triggered (web scraping)", "status": "running"}
    except Exception as e:
        logger.error(f"Error triggering discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/discovery/status")
async def get_discovery_status():
    """Get lead discovery status"""
    return {
        "is_running": discovery_scheduler_instance.is_running,
        "scheduler_running": discovery_scheduler_instance.scheduler.running
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
    
    # Create database indexes for query optimization
    try:
        logger.info("Creating database indexes...")
        await db.email_queue.create_index([("status", 1), ("attempts", 1)])
        await db.clinics.create_index([("comunidad_autonoma", 1)])
        await db.clinics.create_index([("score", 1)])
        await db.clinics.create_index([("estado", 1)])
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Index creation warning (may already exist): {str(e)}")
    
    email_queue_service_instance.start()
    logger.info("Email queue processor started - sending 1 email per 120 seconds per account")
    
    # Start lead discovery scheduler
    discovery_scheduler_instance.start()
    logger.info("Lead discovery scheduler started - running every 2 hours")
    logger.info("System ready: Automated lead discovery → AI scoring → Email sending")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop email queue processor and discovery scheduler on shutdown"""
    email_queue_service_instance.stop()
    discovery_scheduler_instance.stop()
    client.close()
    logger.info("Shutdown complete")
