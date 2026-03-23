import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DiscoveryScheduler:
    """
    Automated lead discovery scheduler - 24/7 Operation
    NOW WITH GOOGLE PLACES API - Real leads from Google Maps!
    Runs every hour for 20 minutes as per user requirements
    """
    
    def __init__(self, automation_service, db):
        self.automation_service = automation_service
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.discovery_duration_minutes = 20  # Run for 20 minutes each cycle
        self.google_api_enabled = bool(os.environ.get('GOOGLE_API_KEY'))
        logger.info("Discovery Scheduler initialized - 24/7 automated mode")
        if self.google_api_enabled:
            logger.info("🗺️ Google Places API ENABLED - Real lead discovery active!")
    
    async def run_google_discovery(self, max_leads: int = 50) -> int:
        """
        Run Google Places API discovery to find NEW real leads
        """
        try:
            from services.google_places_discovery import google_places_discovery
            
            logger.info("🗺️ Starting Google Places discovery...")
            
            # Discover new leads from Google Maps
            new_leads = await google_places_discovery.discover_leads(max_leads=max_leads)
            
            if not new_leads:
                logger.info("📍 No new leads from Google Places")
                return 0
            
            logger.info(f"📍 Found {len(new_leads)} leads from Google Places")
            
            # Import leads into database
            imported = 0
            for lead in new_leads:
                try:
                    # Check for duplicates by name + city or place_id
                    existing = await self.db.clinics.find_one({
                        "$or": [
                            {"place_id": lead.get("place_id")},
                            {
                                "clinica": lead.get("clinica"),
                                "ciudad": lead.get("ciudad")
                            }
                        ]
                    })
                    
                    if not existing:
                        # Score the lead using AI
                        from services.ai_scoring_service import ai_scoring_service
                        scoring = await ai_scoring_service.score_clinic(lead)
                        
                        # Only import if not a filtered corporation
                        if scoring.get("should_contact", False):
                            lead["score"] = scoring.get("score", 5)
                            lead["scoring_details"] = scoring.get("details", [])
                            
                            await self.db.clinics.insert_one(lead)
                            imported += 1
                            logger.info(f"✅ Imported: {lead['clinica']} (Score: {lead['score']})")
                        else:
                            logger.debug(f"❌ Filtered: {lead['clinica']} - {scoring.get('details', [])}")
                    else:
                        logger.debug(f"⏭️ Duplicate: {lead['clinica']}")
                        
                except Exception as e:
                    logger.error(f"Error importing lead {lead.get('clinica')}: {str(e)}")
            
            logger.info(f"🗺️ Google Places: Imported {imported} new leads")
            return imported
            
        except Exception as e:
            logger.error(f"Error in Google discovery: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    async def run_discovery_cycle(self):
        """
        Run one cycle of lead discovery and processing
        1. First: Discover NEW leads from Google Places API
        2. Then: Process pending leads into email queue
        """
        if self.is_running:
            logger.info("Discovery cycle already running, skipping...")
            return
        
        self.is_running = True
        start_time = datetime.utcnow()
        
        try:
            logger.info("="*60)
            logger.info("🚀 STARTING 24/7 AUTOMATED LEAD DISCOVERY CYCLE")
            logger.info(f"⏱️ Will run for {self.discovery_duration_minutes} minutes")
            logger.info(f"🕐 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            logger.info("="*60)
            
            # PHASE 1: Discover NEW leads from Google Places
            new_discovered = 0
            if self.google_api_enabled:
                new_discovered = await self.run_google_discovery(max_leads=30)
            
            # Check current lead count
            current_count = await self.db.clinics.count_documents({})
            pending_count = await self.db.clinics.count_documents({"estado": "Sin contactar"})
            logger.info(f"📊 Total leads in database: {current_count}")
            logger.info(f"📋 Pending leads to process: {pending_count}")
            
            # PHASE 2: Process pending leads into email queue
            processed = 0
            queued = 0
            
            while True:
                # Check if we've exceeded our time limit
                elapsed = (datetime.utcnow() - start_time).total_seconds() / 60
                if elapsed >= self.discovery_duration_minutes:
                    logger.info(f"⏱️ Time limit reached ({self.discovery_duration_minutes} minutes)")
                    break
                
                # Get pending leads that haven't been processed
                pending_leads = await self.db.clinics.find({
                    "estado": "Sin contactar",
                    "email": {"$exists": True, "$ne": "", "$ne": None}
                }).limit(10).to_list(10)
                
                if not pending_leads:
                    logger.info("✅ No more pending leads to process")
                    break
                
                for lead in pending_leads:
                    try:
                        clinic_id = str(lead.get("_id"))
                        
                        # Check if already in email queue
                        in_queue = await self.db.email_queue.find_one({"clinic_id": clinic_id})
                        
                        if not in_queue:
                            # Add to email queue
                            queue_item = {
                                "clinic_id": clinic_id,
                                "clinic_data": {
                                    "clinica": lead.get("clinica"),
                                    "email": lead.get("email"),
                                    "ciudad": lead.get("ciudad"),
                                    "telefono": lead.get("telefono", "")
                                },
                                "status": "pending",
                                "attempts": 0,
                                "added_at": datetime.utcnow()
                            }
                            await self.db.email_queue.insert_one(queue_item)
                            queued += 1
                            logger.info(f"📧 Queued for email: {lead.get('clinica')}")
                        
                        # Update lead status
                        await self.db.clinics.update_one(
                            {"_id": lead["_id"]},
                            {"$set": {"estado": "En cola de contacto"}}
                        )
                        
                        processed += 1
                        
                        # Small delay to prevent overload
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error processing lead {lead.get('clinica')}: {str(e)}")
                
                # Brief pause between batches
                await asyncio.sleep(1)
            
            # Final stats
            new_count = await self.db.clinics.count_documents({})
            email_queue_count = await self.db.email_queue.count_documents({"status": "pending"})
            
            logger.info("="*60)
            logger.info("📊 AUTOMATED CYCLE COMPLETE")
            logger.info(f"🗺️ New leads discovered (Google): {new_discovered}")
            logger.info(f"✅ Leads processed: {processed}")
            logger.info(f"📧 Added to email queue: {queued}")
            logger.info(f"📬 Total pending in email queue: {email_queue_count}")
            logger.info(f"📈 Total leads in DB: {new_count}")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Error in discovery cycle: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self.is_running = False
    
    def start(self):
        """Start the discovery scheduler - 24/7 AUTOMATED MODE WITH GOOGLE PLACES"""
        logger.info("="*60)
        logger.info("🚀 STARTING 24/7 AUTOMATED LEAD DISCOVERY SCHEDULER")
        if self.google_api_enabled:
            logger.info("🗺️ Google Places API: ENABLED - Real lead discovery!")
        else:
            logger.info("⚠️ Google Places API: NOT CONFIGURED")
        logger.info("⏰ Schedule: Every hour, runs for 20 minutes")
        logger.info("🌙 Works while you sleep!")
        logger.info("="*60)
        
        # Add scheduled job - run every hour (60 minutes) as per user requirement
        self.scheduler.add_job(
            self.run_discovery_cycle,
            IntervalTrigger(minutes=60),
            id='automated_discovery_24_7',
            replace_existing=True
        )
        
        # Also run immediately on startup
        self.scheduler.add_job(
            self.run_discovery_cycle,
            'date',
            id='initial_discovery_run',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("✅ 24/7 Discovery scheduler started - Lead processing every hour!")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Discovery scheduler stopped")
