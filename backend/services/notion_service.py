import os
from notion_client import AsyncClient
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class NotionService:
    def __init__(self):
        api_key = os.getenv("NOTION_API_KEY", "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")
        self.client = AsyncClient(auth=api_key)
        self.database_id = os.getenv("NOTION_DATABASE_ID", "DIRECTORY_1_MAD_SEG")
    
    async def add_clinic(self, clinic_data: Dict) -> str:
        """Add a clinic to Notion database"""
        try:
            properties = {
                "Nombre": {"title": [{"text": {"content": clinic_data.get("clinica", "")}}]},
                "Ciudad": {"rich_text": [{"text": {"content": clinic_data.get("ciudad", "")}}]},
                "Email": {"email": clinic_data.get("email", "")},
                "Teléfono": {"phone_number": clinic_data.get("telefono", "")},
                "Score": {"number": clinic_data.get("score")},
                "Estado": {"select": {"name": clinic_data.get("estado", "Sin contactar")}},
                "Website": {"url": clinic_data.get("website", "")},
                "Fuente": {"rich_text": [{"text": {"content": clinic_data.get("fuente", "Manual")}}]},
            }
            
            response = await self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"Added clinic to Notion: {clinic_data.get('clinica')}")
            return response["id"]
        except Exception as e:
            logger.error(f"Error adding clinic to Notion: {str(e)}")
            raise
    
    async def update_clinic(self, page_id: str, updates: Dict):
        """Update clinic in Notion"""
        try:
            properties = {}
            
            if "score" in updates:
                properties["Score"] = {"number": updates["score"]}
            if "estado" in updates:
                properties["Estado"] = {"select": {"name": updates["estado"]}}
            if "email_sent" in updates:
                properties["Email Enviado"] = {"checkbox": updates["email_sent"]}
            if "last_email_date" in updates:
                properties["Último Email"] = {"date": {"start": updates["last_email_date"]}}
            
            await self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            logger.info(f"Updated clinic in Notion: {page_id}")
        except Exception as e:
            logger.error(f"Error updating clinic in Notion: {str(e)}")
            raise
    
    async def get_clinics(self, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Get clinics from Notion"""
        try:
            query_params = {"database_id": self.database_id}
            if filter_dict:
                query_params["filter"] = filter_dict
            
            response = await self.client.databases.query(**query_params)
            
            clinics = []
            for page in response["results"]:
                props = page["properties"]
                clinic = {
                    "id": page["id"],
                    "clinica": props.get("Nombre", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
                    "ciudad": props.get("Ciudad", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
                    "email": props.get("Email", {}).get("email", ""),
                    "telefono": props.get("Teléfono", {}).get("phone_number", ""),
                    "score": props.get("Score", {}).get("number"),
                    "estado": props.get("Estado", {}).get("select", {}).get("name", ""),
                    "website": props.get("Website", {}).get("url", ""),
                }
                clinics.append(clinic)
            
            return clinics
        except Exception as e:
            logger.error(f"Error getting clinics from Notion: {str(e)}")
            raise

notion_service = NotionService()
