"""
WhatsApp Messaging Service
Sends automated WhatsApp messages to clinic leads
"""

import logging
import os
from typing import Dict, Optional
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR.parent / '.env')
load_dotenv(ROOT_DIR / '.env')
load_dotenv(ROOT_DIR.parent / '.env.example')

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    WhatsApp messaging service for automated outreach
    Uses WhatsApp Business API or Web API
    """
    
    def __init__(self):
        # WhatsApp API configuration
        self.api_key = os.environ.get('WHATSAPP_API_KEY', '')
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
        self.business_phone = os.environ.get('BUSINESS_PHONE', '637971233')
        self.business_name = os.environ.get('BUSINESS_NAME', 'Gestión Digital Clínica')
        self.business_owner = os.environ.get('BUSINESS_OWNER', 'José Cabrejas')
        
        # Message template
        self.message_template = """Hola {clinic_name},

Soy {owner} de {business}. He visto vuestra web y creo que podemos:
- evitar huecos en agenda
- reducir mensajes manuales por WhatsApp
- confirmar mejor las citas

No quiero complicaros: solo automatizar lo que ya hacéis (confirmaciones, no-shows, reservas/confirmaciones y pagos previos cuando toque).

¿Te cuento en 10-15 minutos lo que cambiaría en vuestro caso? Lo vemos por llamada o te dejo un resumen por aquí.

Saludos,
{owner}
📱 {phone}"""
    
    async def send_whatsapp_message(self, to_phone: str, clinic_name: str) -> Dict:
        """
        Send WhatsApp message to a clinic
        
        Args:
            to_phone: Destination phone number (Spanish format: 912345678 or 612345678)
            clinic_name: Name of the clinic
            
        Returns:
            Dict with status and message_id
        """
        try:
            # Clean phone number (remove spaces, dashes)
            clean_phone = to_phone.replace(' ', '').replace('-', '')
            
            # Ensure Spanish country code
            if not clean_phone.startswith('34'):
                if clean_phone.startswith('0'):
                    clean_phone = '34' + clean_phone[1:]
                else:
                    clean_phone = '34' + clean_phone
            
            # Format message
            message = self.message_template.format(
                clinic_name=clinic_name,
                owner=self.business_owner,
                business=self.business_name,
                phone=self.business_phone
            )
            
            # If WhatsApp API is configured, use it
            if self.api_key and self.phone_number_id:
                result = await self._send_via_api(clean_phone, message)
            else:
                # Otherwise, generate WhatsApp Web link (manual sending)
                result = self._generate_whatsapp_link(clean_phone, message)
            
            logger.info(f"WhatsApp message prepared for {clinic_name} ({to_phone})")
            return result
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {to_phone}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _send_via_api(self, phone: str, message: str) -> Dict:
        """
        Send via WhatsApp Business API (requires API key)
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "method": "api",
                            "message_id": data.get('messages', [{}])[0].get('id')
                        }
                    else:
                        error = await response.text()
                        logger.error(f"WhatsApp API error: {error}")
                        return {"success": False, "error": error}
        
        except Exception as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_whatsapp_link(self, phone: str, message: str) -> Dict:
        """
        Generate WhatsApp Web link (manual click-to-send)
        """
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        link = f"https://wa.me/{phone}?text={encoded_message}"
        
        return {
            "success": True,
            "method": "link",
            "whatsapp_link": link,
            "message": "WhatsApp link generated - manual sending required"
        }
    
    async def send_bulk_whatsapp(self, leads: list) -> Dict:
        """
        Send WhatsApp messages to multiple leads
        
        Args:
            leads: List of dicts with 'telefono' and 'clinica' fields
            
        Returns:
            Dict with success/failure counts
        """
        results = {"success": 0, "failed": 0, "links": []}
        
        for lead in leads:
            phone = lead.get('telefono')
            clinic_name = lead.get('clinica')
            
            if not phone or not clinic_name:
                results['failed'] += 1
                continue
            
            result = await self.send_whatsapp_message(phone, clinic_name)
            
            if result.get('success'):
                results['success'] += 1
                if result.get('method') == 'link':
                    results['links'].append({
                        'clinic': clinic_name,
                        'link': result['whatsapp_link']
                    })
            else:
                results['failed'] += 1
        
        return results

# Global instance
whatsapp_service = WhatsAppService()
