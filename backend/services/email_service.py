import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR.parent / '.env')
load_dotenv(ROOT_DIR / '.env')
load_dotenv(ROOT_DIR.parent / '.env.example')

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.environ['SMTP_HOST']
        self.smtp_port = int(os.environ['SMTP_PORT'])
        self.business_info = {
            "name": os.environ['BUSINESS_NAME'],
            "owner": os.environ['BUSINESS_OWNER'],
            "email": os.environ['BUSINESS_EMAIL'],
            "website": os.environ['BUSINESS_WEBSITE'],
            "phone": os.environ['BUSINESS_PHONE'],
            "logo_url": os.environ['BUSINESS_LOGO_URL']
        }
    
    def _generate_email_body(self, clinic_name: str, personalization: Dict) -> str:
        """Generate the simplified outreach email body"""

        clinic_display = clinic_name or personalization.get("clinica") or "la clínica"
        ciudad = personalization.get("ciudad")
        web_line = f"He estado viendo vuestra web de {clinic_display}"
        if ciudad:
            web_line += f" en {ciudad}"
        web_line += " y cómo gestionáis las citas."

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #1f2937; }}
        .container {{ max-width: 640px; margin: 0 auto; padding: 16px; }}
        h2 {{ color: #0f172a; margin-bottom: 8px; }}
        ul {{ margin: 8px 0 16px 20px; padding: 0; }}
        li {{ margin-bottom: 6px; }}
        .signature {{ border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px; color: #475569; }}
    </style>
</head>
<body>
    <div class="container">
        <p>Hola {clinic_display},</p>

        <p>{web_line}</p>

        <p>En vuestro caso hay margen directo para mejorar sin cambiar cómo trabajáis:</p>
        <ul>
            <li>evitar huecos en agenda</li>
            <li>reducir mensajes manuales por WhatsApp</li>
            <li>confirmar mejor las citas y perder menos pacientes por el camino</li>
        </ul>

        <p>No se trata de meter un sistema complejo, sino de automatizar lo que ya hacéis para que funcione solo.</p>

        <p>Por ejemplo:</p>
        <ul>
            <li>confirmaciones automáticas de citas y gestión básica de no-shows</li>
            <li>pacientes que pueden reservar o confirmar sin depender siempre de vosotros</li>
            <li>menos idas y vueltas por WhatsApp con mensajes preparados</li>
            <li>opción de dejar citas ya confirmadas o pagadas antes de que lleguen</li>
        </ul>

        <p>En clínicas como la vuestra esto suele traducirse en menos gestión y más agenda llena sin aumentar horas.</p>

        <p>Si quieres, puedo mirar vuestro caso concreto y decirte exactamente qué cambiaría yo, sin compromiso. Lo vemos por llamada o por aquí mismo si prefieres.</p>

        <div class="signature">
            <p style="font-weight: 600; color: #0f172a;">{self.business_info['owner']}</p>
            <p style="margin: 0;">{self.business_info['name']}</p>
            <p style="margin: 0;">📧 {self.business_info['email']}</p>
            <p style="margin: 0;">🌐 {self.business_info['website']}</p>
            <p style="margin: 0;">📱 Tel/WhatsApp: {self.business_info['phone']}</p>
        </div>
    </div>
</body>
</html>
"""
        return html_body
    
    async def send_email(
        self, 
        to_email: str, 
        clinic_name: str,
        from_email: str,
        from_password: str,
        attachment_path: Optional[str] = None,
        personalization: Optional[Dict] = None
    ) -> bool:
        """Send personalized email to clinic"""
        try:
            clinic_display = clinic_name or (personalization or {}).get("clinica") or "la clínica"
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"Agenda y WhatsApp en {clinic_display}"
            
            # Generate personalized body
            html_body = self._generate_email_body(clinic_name, personalization or {})
            msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=from_email,
                password=from_password,
                use_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email} from {from_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

email_service = EmailService()
