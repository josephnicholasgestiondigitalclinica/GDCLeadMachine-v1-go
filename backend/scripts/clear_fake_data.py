"""
Script to clear all fake/mock leads from database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

async def clear_fake_leads():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🗑️  Clearing all fake/mock leads...")
    
    # Delete all clinics (they're all fake from mock discovery)
    clinics_result = await db.clinics.delete_many({})
    print(f"✅ Deleted {clinics_result.deleted_count} fake clinics")
    
    # Delete all email queue items
    queue_result = await db.email_queue.delete_many({})
    print(f"✅ Deleted {queue_result.deleted_count} email queue items")
    
    # Delete attachments
    attachments_result = await db.attachments.delete_many({})
    print(f"✅ Deleted {attachments_result.deleted_count} attachments")
    
    print("\n✨ Database cleaned! Ready for real data.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_fake_leads())
