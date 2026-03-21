import os
import aiohttp
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError
from typing import Dict, Optional
import logging
import re
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class AIScoringService:
    def __init__(self):
        self.llm_key = os.environ['EMERGENT_LLM_KEY']
        self.excluded_corporations = [
            "quironsalud", "sanitas", "vithas", "hm hospitales", 
            "hospital universitario", "hospital general"
        ]
    
    async def score_clinic(self, clinic_data: Dict) -> Dict:
        """
        Score clinic based on:
        - Email authenticity
        - Website quality
        - Domain type (prefers non-corporate, gmail/hotmail gets bonus)
        - Excludes big corporations
        """
        try:
            score = 0
            details = []
            
            # 1. Check if it's a big corporation (auto-reject)
            clinic_name = clinic_data.get("clinica", "").lower()
            if any(corp in clinic_name for corp in self.excluded_corporations):
                return {
                    "score": 0,
                    "authentic": False,
                    "details": ["Corporación grande excluida"],
                    "should_contact": False
                }
            
            # 2. Validate email
            email = clinic_data.get("email", "")
            email_score, email_details = await self._score_email(email)
            score += email_score
            details.extend(email_details)
            
            # 3. Check website (if provided)
            website = clinic_data.get("website", "")
            if website:
                web_score, web_details = await self._score_website(website, clinic_name)
                score += web_score
                details.extend(web_details)
            else:
                score += 2  # Bonus for no website (potential client!)
                details.append("Sin sitio web propio (+2 - buen prospecto)")
            
            # 4. Use AI to verify authenticity
            ai_verification = await self._ai_verify(clinic_data)
            score += ai_verification["score"]
            details.extend(ai_verification["details"])
            
            # Normalize score to 1-10
            final_score = min(10, max(1, score))
            
            return {
                "score": final_score,
                "authentic": final_score >= 5,
                "details": details,
                "should_contact": final_score >= 5
            }
            
        except Exception as e:
            logger.error(f"Error scoring clinic: {str(e)}")
            return {
                "score": 0,
                "authentic": False,
                "details": [f"Error: {str(e)}"],
                "should_contact": False
            }
    
    async def _score_email(self, email: str) -> tuple:
        """Score email address - lenient validation to avoid false negatives"""
        score = 0
        details = []
        
        try:
            # Basic email format validation only (no deliverability check)
            # Deliverability checks are too strict and reject valid emails
            validation = validate_email(email, check_deliverability=False)
            email = validation.normalized
            score += 3
            details.append("Email válido (+3)")
            
            # Check domain
            domain = email.split("@")[1].lower()
            
            # Bonus for personal email (gmail, hotmail, outlook)
            personal_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "yahoo.es"]
            if any(pd in domain for pd in personal_domains):
                score += 3
                details.append(f"Email personal ({domain}) (+3 - buen prospecto)")
            
            # Bonus for generic emails (info@, contacto@)
            if email.startswith(("info@", "contacto@", "admin@", "recepcion@", "clinica@")):
                score += 1
                details.append("Email genérico (+1)")
            
        except EmailNotValidError as e:
            # Even if validation fails, give partial score if format looks reasonable
            if "@" in email and "." in email.split("@")[-1]:
                score += 2
                details.append(f"Email con formato básico válido (+2)")
            else:
                details.append(f"Email no válido: {str(e)}")
        
        return score, details
    
    async def _score_website(self, website: str, clinic_name: str) -> tuple:
        """Score website quality"""
        score = 0
        details = []
        
        try:
            # Normalize URL
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(website, timeout=10, allow_redirects=True) as response:
                    if response.status == 200:
                        score += 1
                        details.append("Sitio web activo (+1)")
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Check if clinic name appears on website
                        if clinic_name.lower() in html.lower():
                            score += 2
                            details.append("Nombre coincide con sitio web (+2)")
                        
                        # Check for poor quality indicators (good for us!)
                        if not soup.find("meta", attrs={"name": "description"}):
                            score += 1
                            details.append("Sin SEO básico (+1 - buen prospecto)")
                        
                        # Check if it's a simple site (good for us!)
                        if len(soup.find_all("a")) < 10:
                            score += 1
                            details.append("Sitio web simple (+1 - buen prospecto)")
                    else:
                        score -= 1
                        details.append(f"Sitio web inaccesible ({response.status})")
        except Exception as e:
            score += 2  # Can't access = probably poor website = good prospect!
            details.append(f"Sitio web problemático (+2 - buen prospecto)")
        
        return score, details
    
    async def _ai_verify(self, clinic_data: Dict) -> Dict:
        """Use AI to verify clinic authenticity"""
        try:
            prompt = f"""Analiza esta clínica y determina si es un buen prospecto para servicios de gestión digital clínica:

Clínica: {clinic_data.get('clinica', '')}
Ciudad: {clinic_data.get('ciudad', '')}
Email: {clinic_data.get('email', '')}
Teléfono: {clinic_data.get('telefono', '')}
Sitio web: {clinic_data.get('website', 'No tiene')}

Criterios:
- Clínicas pequeñas/medianas son MEJORES prospectos
- Clínicas sin sitio web propio son MEJORES prospectos
- Clínicas con emails personales (gmail, hotmail) son MEJORES prospectos
- Grandes corporaciones (Quironsalud, Sanitas, etc.) NO son prospectos
- El email debe parecer real y activo

Responde SOLO con un número del 1-3 y una razón breve (máximo 20 palabras):
Formato: SCORE:X|RAZÓN:tu razón aquí"""

            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.llm_key}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # Parse response
                        score_match = re.search(r"SCORE:(\d+)", content)
                        reason_match = re.search(r"RAZÓN:(.+)", content)
                        
                        score = int(score_match.group(1)) if score_match else 1
                        reason = reason_match.group(1).strip() if reason_match else "Verificado por IA"
                        
                        return {
                            "score": score,
                            "details": [f"IA: {reason} (+{score})"]
                        }
        except Exception as e:
            logger.error(f"AI verification error: {str(e)}")
        
        return {"score": 1, "details": ["Verificación IA no disponible"]}

ai_scoring_service = AIScoringService()
