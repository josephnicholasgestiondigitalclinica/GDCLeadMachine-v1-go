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
load_dotenv(ROOT_DIR / '.env')

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
        """Generate personalized email based on template"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            max-width: 200px;
            height: auto;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .section {{
            margin: 20px 0;
        }}
        .section-title {{
            color: #17a2b8;
            font-weight: bold;
            margin: 15px 0 10px 0;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .signature {{
            border-top: 2px solid #17a2b8;
            padding-top: 20px;
            margin-top: 30px;
        }}
        .signature-name {{
            font-weight: bold;
            color: #1e3a5f;
        }}
        .signature-title {{
            color: #17a2b8;
            font-weight: bold;
        }}
        .contact-info {{
            margin-top: 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{self.business_info['logo_url']}" alt="GDC Logo" class="logo">
        </div>
        
        <div class="content">
            <p>Hola equipo de {clinic_name},</p>
            
            <p>Soy {self.business_info['owner']}, de {self.business_info['name']}.</p>
            
            <p>Ayudamos a clínicas privadas a implantar un sistema integral que centraliza la gestión diaria (agenda, seguimiento, tareas internas y procesos), para que todo quede en un único entorno y el equipo deje de trabajar con datos dispersos entre múltiples plataformas.</p>
            
            <div class="section">
                <p class="section-title">Cómo trabajamos (sin venderte "si encaja o no"):</p>
                <ol>
                    <li>Nos facilitas información de vuestros procesos actuales y puntos de fricción.</li>
                    <li>Realizamos un análisis del flujo de trabajo (especialmente tareas repetitivas y de alto consumo de tiempo).</li>
                    <li>Redactamos un plan de diseño del sistema para reducir —y cuando sea posible eliminar— esa carga operativa dentro del marco viable.</li>
                </ol>
                <p><strong>Plazo objetivo:</strong> hasta 30 días máximo.</p>
            </div>
            
            <div class="section">
                <p class="section-title">Qué cubre el sistema (ejemplos típicos):</p>
                <ul>
                    <li><strong>No-shows:</strong> recordatorios/confirmaciones automáticas y registro de respuestas</li>
                    <li><strong>Citación por WhatsApp automatizada,</strong> dentro y fuera del horario administrativo, liberando tiempo al equipo</li>
                    <li><strong>Categorización previa del paciente</strong> dentro del flujo (para organizar y evitar fricción):
                        <ul>
                            <li>Asegurado / Mutua</li>
                            <li>Privado</li>
                            <li>Privado con pago realizado (confirmación tras pago)</li>
                            <li>Privado con pago pendiente (se abona presencialmente el día de la cita)</li>
                        </ul>
                    </li>
                    <li><strong>Operativa y trazabilidad:</strong> tablero de "qué toca hoy", pagos pendientes, tareas, y seguimiento</li>
                    <li><strong>Garantía:</strong> diseñado para cumplir con las normativas vigentes de protección de datos aplicables</li>
                </ul>
            </div>
            
            <div class="section">
                <p class="section-title">Gestión de roles, permisos y accesos (panel de administración):</p>
                <ul>
                    <li><strong>Administrador principal:</strong> alta de personal, asignación de roles y permisos</li>
                    <li><strong>Administrador delegado:</strong> mismas capacidades para repartir carga y supervisión</li>
                    <li><strong>Equipo de recepción y gestión administrativa:</strong> citación y gestión de no-shows, facturación, emisión de facturas, facturación a aseguradoras, contabilidad operativa y trazabilidad de pagos pendientes</li>
                    <li><strong>Equipo médico:</strong> acceso a historia clínica de sus pacientes, redacción de informes, emisión de recetas, y otras funciones clínicas según el rol</li>
                </ul>
            </div>
            
            <div class="section">
                <p class="section-title">Portal del paciente (acceso propio):</p>
                <ul>
                    <li>Ver informes, recetas e instrucciones elaboradas por el profesional</li>
                    <li>Ver próxima cita y recordatorios para solicitar/renovar cita</li>
                    <li>Ver facturas y estado de pagos</li>
                    <li>Formulario para ejercer derechos del paciente según la normativa vigente</li>
                </ul>
            </div>
            
            <p>Si te parece bien podemos programar una llamada (o mantener contacto por correo como mejor sea) para comentar sobre el programa más a fondo y contestar cualquier duda que tenga.</p>
        </div>
        
        <div class="signature">
            <p class="signature-name">{self.business_info['owner']}</p>
            <p class="signature-title">{self.business_info['name']}</p>
            <div class="contact-info">
                <p>📧 {self.business_info['email']}</p>
                <p>🌐 {self.business_info['website']}</p>
                <p>📱 Tel/WhatsApp: {self.business_info['phone']}</p>
            </div>
            <div style="margin-top: 15px;">
                <img src="{self.business_info['logo_url']}" alt="GDC Logo" style="max-width: 150px; height: auto;">
            </div>
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
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"Sistema integral para centralizar la operativa de {clinic_name}"
            
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
