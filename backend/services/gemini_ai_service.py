"""
Google Gemini AI Service
Provides AI-powered lead scoring and email generation using Google's Gemini API
"""
import os
import logging
import google.generativeai as genai
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR.parent / '.env')
load_dotenv(ROOT_DIR / '.env')
load_dotenv(ROOT_DIR.parent / '.env.example')

logger = logging.getLogger(__name__)


class GeminiAIService:
    """
    Google Gemini AI Service for lead scoring and email generation
    Uses Gemini Pro for intelligent analysis and content creation
    """

    def __init__(self):
        self.api_key = (
            os.environ.get('GOOGLE_GEMINI_API_KEY')
            or os.environ.get('GEMINI_API_KEY')
            or os.environ.get('GOOGLE_AI_API_KEY')
            or ''
        )
        self.model_name = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
        self.is_configured = bool(self.api_key)

        if self.is_configured:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"🤖 Google Gemini AI Service initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error configuring Gemini: {str(e)}")
                self.is_configured = False
        else:
            logger.warning("⚠️ Google Gemini API key not configured")

    async def score_clinic_with_ai(self, clinic_data: Dict) -> Dict:
        """
        Use Gemini AI to score and analyze a clinic lead
        Returns score (1-3) and reasoning
        """
        if not self.is_configured:
            return {
                "score": 1,
                "reason": "AI scoring not available - using default",
                "available": False
            }

        try:
            prompt = f"""Analiza esta clínica y determina si es un buen prospecto para servicios de gestión digital clínica:

Clínica: {clinic_data.get('clinica', '')}
Ciudad: {clinic_data.get('ciudad', '')}
Email: {clinic_data.get('email', '')}
Teléfono: {clinic_data.get('telefono', '')}
Sitio web: {clinic_data.get('website', 'No tiene')}

Criterios para puntuación:
- Clínicas pequeñas/medianas son MEJORES prospectos (puntuación más alta)
- Clínicas sin sitio web profesional son MEJORES prospectos
- Clínicas con emails personales (gmail, hotmail) son MEJORES prospectos
- Grandes corporaciones (Quironsalud, Sanitas, HM, Vithas, etc.) NO son prospectos (puntuación 0)
- Hospitales públicos o universitarios NO son prospectos (puntuación 0)
- El email debe parecer real y activo

Responde EXACTAMENTE en este formato (una línea):
SCORE:X|RAZÓN:tu razón aquí (máximo 20 palabras)

Donde X es un número del 0-3:
0 = Gran corporación/hospital/no contactar
1 = Prospecto débil
2 = Buen prospecto
3 = Excelente prospecto"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Parse response
            score = 1
            reason = "Análisis completado"

            if "SCORE:" in content and "RAZÓN:" in content:
                parts = content.split("|")
                for part in parts:
                    if part.startswith("SCORE:"):
                        try:
                            score = int(part.replace("SCORE:", "").strip())
                            score = max(0, min(3, score))  # Clamp to 0-3
                        except:
                            pass
                    elif part.startswith("RAZÓN:"):
                        reason = part.replace("RAZÓN:", "").strip()
            else:
                # Fallback parsing if format is different
                reason = content[:100]  # First 100 chars

            logger.info(f"✅ Gemini AI scored {clinic_data.get('clinica')} -> {score}/3: {reason}")

            return {
                "score": score,
                "reason": reason,
                "available": True
            }

        except Exception as e:
            logger.error(f"Error in Gemini AI scoring: {str(e)}")
            return {
                "score": 1,
                "reason": f"Error en análisis AI: {str(e)[:50]}",
                "available": False
            }

    async def generate_personalized_email(self, clinic_data: Dict, business_info: Dict) -> Dict:
        """
        Generate a personalized outreach email using Gemini AI
        Returns email subject and body
        """
        if not self.is_configured:
            return {
                "subject": f"Transformación Digital para {clinic_data.get('clinica', 'su clínica')}",
                "body": self._get_fallback_email(clinic_data, business_info),
                "available": False
            }

        try:
            clinic_name = clinic_data.get('clinica', '')
            city = clinic_data.get('ciudad', '')
            website = clinic_data.get('website', 'No')

            prompt = f"""Genera un email personalizado de presentación para esta clínica:

INFORMACIÓN DE LA CLÍNICA:
Nombre: {clinic_name}
Ciudad: {city}
Tiene sitio web: {'Sí' if website else 'No'}

INFORMACIÓN DEL NEGOCIO (quien envía el email):
Nombre: {business_info.get('name', 'Gestión Digital Clínica')}
Owner: {business_info.get('owner', 'José Cabrejas')}
Email: {business_info.get('email', 'contacto@gestiondigitalclinica.es')}
Website: {business_info.get('website', 'www.gestiondigitalclinica.es')}
Teléfono: {business_info.get('phone', '637 971 233')}

INSTRUCCIONES:
1. Email profesional pero cercano, en español
2. Personaliza según la clínica (menciona su nombre y ciudad)
3. Si no tienen sitio web, menciona que podemos ayudarles con presencia digital
4. Si tienen sitio web, menciona que podemos mejorar su captación de pacientes
5. Destaca: diseño web, SEO, redes sociales, gestión de reseñas Google
6. Mantén el email corto (máximo 150 palabras)
7. Call-to-action claro: agendar llamada o responder email

FORMATO DE RESPUESTA (exacto):
ASUNTO:tu asunto aquí
---
CUERPO:
tu email aquí (con saltos de línea y formato)"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            # Parse response
            subject = f"Transformación Digital para {clinic_name}"
            body = self._get_fallback_email(clinic_data, business_info)

            if "ASUNTO:" in content and "CUERPO:" in content:
                parts = content.split("---")
                if len(parts) >= 2:
                    # Extract subject
                    subject_part = parts[0].strip()
                    if "ASUNTO:" in subject_part:
                        subject = subject_part.replace("ASUNTO:", "").strip()

                    # Extract body
                    body_part = parts[1].strip()
                    if "CUERPO:" in body_part:
                        body = body_part.replace("CUERPO:", "").strip()
            else:
                # Use the generated content as body if format is different
                body = content

            logger.info(f"✅ Gemini generated email for {clinic_name}")

            return {
                "subject": subject,
                "body": body,
                "available": True
            }

        except Exception as e:
            logger.error(f"Error in Gemini email generation: {str(e)}")
            return {
                "subject": f"Transformación Digital para {clinic_data.get('clinica', 'su clínica')}",
                "body": self._get_fallback_email(clinic_data, business_info),
                "available": False
            }

    def _get_fallback_email(self, clinic_data: Dict, business_info: Dict) -> str:
        """Fallback email template when AI is not available"""
        clinic_name = clinic_data.get('clinica', 'su clínica')
        city = clinic_data.get('ciudad', '')

        return f"""Estimado/a responsable de {clinic_name},

Me llamo {business_info.get('owner', 'José Cabrejas')} y me especializo en ayudar a clínicas de salud en {city} a aumentar su visibilidad online y atraer más pacientes.

¿Le gustaría mejorar su presencia digital? Ofrecemos:
- Diseño web profesional optimizado para conversión
- SEO local para aparecer en las primeras búsquedas de Google
- Gestión de redes sociales y reseñas
- Estrategias de captación de pacientes

¿Tendría 15 minutos esta semana para una llamada exploratoria sin compromiso?

Saludos cordiales,
{business_info.get('owner', 'José Cabrejas')}
{business_info.get('name', 'Gestión Digital Clínica')}
Tel: {business_info.get('phone', '637 971 233')}
Web: {business_info.get('website', 'www.gestiondigitalclinica.es')}"""

    async def analyze_email_bounce(self, bounce_message: str, clinic_email: str) -> Dict:
        """
        Analyze a bounced email and suggest corrections using Gemini AI
        """
        if not self.is_configured:
            return {
                "is_bounce": True,
                "reason": "Email inválido o no existe",
                "suggested_email": None,
                "available": False
            }

        try:
            prompt = f"""Analiza este mensaje de rebote de email y determina:
1. ¿Por qué rebotó el email?
2. ¿Puedes sugerir un email correcto basado en el mensaje de error?

EMAIL ORIGINAL: {clinic_email}

MENSAJE DE REBOTE:
{bounce_message[:500]}

Responde en formato:
RAZÓN:explicación breve
SUGERENCIA:email sugerido (o "ninguna" si no puedes sugerir)"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            reason = "Email inválido o no existe"
            suggested_email = None

            for line in content.split("\n"):
                if line.startswith("RAZÓN:"):
                    reason = line.replace("RAZÓN:", "").strip()
                elif line.startswith("SUGERENCIA:"):
                    suggestion = line.replace("SUGERENCIA:", "").strip().lower()
                    if suggestion != "ninguna" and "@" in suggestion:
                        suggested_email = suggestion

            return {
                "is_bounce": True,
                "reason": reason,
                "suggested_email": suggested_email,
                "available": True
            }

        except Exception as e:
            logger.error(f"Error analyzing bounce with Gemini: {str(e)}")
            return {
                "is_bounce": True,
                "reason": "Error analizando rebote",
                "suggested_email": None,
                "available": False
            }


# Singleton instance
gemini_ai_service = GeminiAIService()
