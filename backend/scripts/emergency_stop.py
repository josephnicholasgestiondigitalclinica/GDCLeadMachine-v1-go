"""
EMERGENCY STOP - Clear everything and disable auto-discovery
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

async def emergency_stop():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🚨 EMERGENCY STOP - Clearing all fake data")
    print("="*60)
    
    # 1. Clear email queue completely
    queue_result = await db.email_queue.delete_many({})
    print(f"✅ Deleted {queue_result.deleted_count} emails from queue")
    
    # 2. Clear all clinics
    clinics_result = await db.clinics.delete_many({})
    print(f"✅ Deleted {clinics_result.deleted_count} clinics")
    
    # 3. Clear attachments
    attachments_result = await db.attachments.delete_many({})
    print(f"✅ Deleted {attachments_result.deleted_count} attachments")
    
    print("="*60)
    print("🛑 ALL DATA CLEARED")
    print("📧 EMAIL SENDING STOPPED (no items in queue)")
    print("⚠️  DO NOT TRIGGER DISCOVERY - waiting for real data import")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(emergency_stop())
