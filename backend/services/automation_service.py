import logging
from typing import Dict
from services.ai_scoring_service import ai_scoring_service
from services.notion_service import notion_service
from services.email_queue_service import email_queue_service

logger = logging.getLogger(__name__)

class AutomationService:
    """
    Handles the automated pipeline:
    New Clinic → AI Scoring → Save to Notion → Queue Email → Send
    """
    
    async def process_new_clinic(self, clinic_data: Dict, source: str = "Manual") -> Dict:
        """
        Complete automation pipeline for new clinic:
        1. Score with AI
        2. Save to Notion
        3. Queue email if score is good
        """
        try:
            logger.info(f"Processing new clinic: {clinic_data.get('clinica')}")
            
            # Step 1: AI Scoring
            scoring_result = await ai_scoring_service.score_clinic(clinic_data)
            clinic_data["score"] = scoring_result["score"]
            clinic_data["scoring_details"] = scoring_result["details"]
            clinic_data["fuente"] = source
            
            logger.info(f"Scored {clinic_data.get('clinica')}: {scoring_result['score']}/10")
            
            # Step 2: Save to Notion (if score is good enough)
            if scoring_result["should_contact"]:
                notion_page_id = await notion_service.add_clinic(clinic_data)
                clinic_data["notion_id"] = notion_page_id
                
                # Step 3: Queue email
                await email_queue_service.add_to_queue(notion_page_id, clinic_data)
                
                logger.info(f"Clinic added to queue: {clinic_data.get('clinica')}")
                
                return {
                    "success": True,
                    "score": scoring_result["score"],
                    "message": f"Clínica procesada y añadida a cola de emails (Score: {scoring_result['score']}/10)",
                    "details": scoring_result["details"],
                    "queued_for_email": True
                }
            else:
                logger.info(f"Clinic rejected (low score): {clinic_data.get('clinica')}")
                return {
                    "success": False,
                    "score": scoring_result["score"],
                    "message": f"Clínica rechazada - score muy bajo ({scoring_result['score']}/10)",
                    "details": scoring_result["details"],
                    "queued_for_email": False
                }
                
        except Exception as e:
            logger.error(f"Error processing clinic: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "queued_for_email": False
            }
    
    async def batch_process_clinics(self, clinics: list, source: str = "Bulk Import") -> Dict:
        """Process multiple clinics at once"""
        results = {
            "total": len(clinics),
            "processed": 0,
            "queued": 0,
            "rejected": 0,
            "errors": 0
        }
        
        for clinic in clinics:
            try:
                result = await self.process_new_clinic(clinic, source)
                results["processed"] += 1
                
                if result["success"]:
                    results["queued"] += 1
                else:
                    results["rejected"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing clinic {clinic.get('clinica')}: {str(e)}")
                results["errors"] += 1
        
        return results

automation_service = AutomationService()
