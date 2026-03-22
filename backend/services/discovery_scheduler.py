import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

class DiscoveryScheduler:
    """Schedules REAL lead discovery with web scraping"""
    
    def __init__(self, automation_service, db):
        self.automation_service = automation_service
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def run_discovery_cycle(self):
        """Run one REAL discovery cycle with web scraping"""
        if self.is_running:
            logger.info("Discovery cycle already running, skipping...")
            return
        
        self.is_running = True
        logger.info("="*60)
        logger.info("🚀 STARTING REAL LEAD DISCOVERY CYCLE")
        logger.info("="*60)
        
        try:
            from services.simplified_lead_discovery import simplified_discovery_service, REGIONS_PRIORITY
            
            # Initialize HTTP session
            await simplified_discovery_service.initialize()
            
            total_discovered = 0
            total_queued = 0
            
            # Discover leads region by region (first 3 regions)
            for region in REGIONS_PRIORITY[:3]:
                try:
                    logger.info(f"\n📍 Discovering in {region['name']}")
                    
                    # Discover real leads
                    leads = await simplified_discovery_service.discover_leads_for_region(region, max_per_city=5)
                    
                    total_discovered += len(leads)
                    
                    # Process each lead
                    for lead in leads:
                        try:
                            lead['comunidad_autonoma'] = region['name']
                            
                            result = await self.automation_service.process_new_clinic(
                                lead,
                                source=lead.get('source', 'Real Discovery')
                            )
                            
                            if result.get('queued'):
                                total_queued += 1
                        
                        except Exception as e:
                            logger.error(f"Error processing lead: {str(e)}")
                            continue
                    
                    logger.info(f"✅ {region['name']}: {len(leads)} discovered, {total_queued} queued")
                    
                    # Respectful delay
                    await asyncio.sleep(10)
                
                except Exception as e:
                    logger.error(f"Error in region {region['name']}: {str(e)}")
                    continue
            
            # Close HTTP session
            await simplified_discovery_service.close()
            
            logger.info("="*60)
            logger.info("✅ REAL DISCOVERY COMPLETE")
            logger.info(f"✓ Total discovered: {total_discovered}")
            logger.info(f"✓ Total queued: {total_queued}")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Error in discovery cycle: {str(e)}")
        finally:
            self.is_running = False
    
    def start(self):
        """Start the discovery scheduler - runs every 6 hours"""
        # Run discovery every 6 hours (more respectful)
        self.scheduler.add_job(
            self.run_discovery_cycle,
            IntervalTrigger(hours=6),
            id='real_lead_discovery',
            replace_existing=True
        )
        
        # DON'T run immediately on startup - only scheduled
        # This prevents auto-scraping on every restart
        
        self.scheduler.start()
        logger.info("REAL Lead discovery scheduler started - running every 6 hours")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Discovery scheduler stopped")

discovery_scheduler = None
