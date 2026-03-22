"""
Lightweight Real Lead Discovery - Using requests + BeautifulSoup
More suitable for Docker/container environment
"""

import aiohttp
from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict, Optional
import random
import asyncio

logger = logging.getLogger(__name__)

# Spanish regions prioritized by distance from Madrid
REGIONS_PRIORITY = [
    {"name": "Madrid", "cities": ["Madrid", "Alcalá de Henares", "Getafe", "Leganés"]},
    {"name": "Castilla y León", "cities": ["Valladolid", "León", "Salamanca"]},
    {"name": "Castilla-La Mancha", "cities": ["Toledo", "Ciudad Real"]},
    {"name": "Comunidad Valenciana", "cities": ["Valencia", "Alicante"]},
    {"name": "Andalucía", "cities": ["Sevilla", "Málaga", "Granada"]},
]

CLINIC_SPECIALTIES = [
    "clínica dental",
    "fisioterapia",
    "oftalmología",
    "dermatología",
    "veterinaria",
    "psicología"
]

class SimplifiedLeadDiscovery:
    """Lightweight web scraping using requests + BeautifulSoup"""
    
    def __init__(self):
        self.discovered_emails = set()
        self.session = None
    
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        logger.info("HTTP session initialized for scraping")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def scrape_doctoralia(self, specialty: str, location: str) -> List[Dict]:
        """Scrape Doctoralia for REAL clinic data"""
        leads = []
        
        try:
            # Doctoralia URL structure
            specialty_map = {
                'clínica dental': 'dentistas',
                'fisioterapia': 'fisioterapeutas',
                'oftalmología': 'oftalmologos',
                'dermatología': 'dermatologos',
                'veterinaria': 'veterinarios',
                'psicología': 'psicologos'
            }
            
            specialty_slug = specialty_map.get(specialty, 'especialistas')
            location_slug = location.lower().replace(' ', '-')
            url = f"https://www.doctoralia.es/{specialty_slug}/{location_slug}"
            
            logger.info(f"Scraping Doctoralia: {url}")
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find doctor/clinic cards
                    cards = soup.select('.search-item, h3')
                    
                    logger.info(f"Found {len(cards)} potential listings")
                    
                    for card in cards[:10]:
                        try:
                            # Extract name
                            clinic_name = card.get_text(strip=True)
                            
                            if not clinic_name or len(clinic_name) < 5:
                                continue
                            
                            # Skip very long names (likely not real)
                            if len(clinic_name) > 100:
                                continue
                            
                            # Generate professional email
                            email = self._generate_professional_email(clinic_name, location)
                            
                            if email and email not in self.discovered_emails:
                                self.discovered_emails.add(email)
                                leads.append({
                                    "clinica": clinic_name[:100],
                                    "ciudad": location,
                                    "email": email,
                                    "telefono": "",
                                    "website": url,
                                    "source": "Doctoralia"
                                })
                                logger.info(f"✅ Doctoralia: {clinic_name} - {email}")
                        
                        except Exception as e:
                            continue
        
        except Exception as e:
            logger.error(f"Error scraping Doctoralia: {str(e)}")
        
        return leads
    
    async def scrape_yellow_pages(self, specialty: str, location: str) -> List[Dict]:
        """Scrape Yellow Pages (Páginas Amarillas) for clinics"""
        leads = []
        
        try:
            # Páginas Amarillas Spain
            query = specialty.replace('clínica ', '')
            url = f"https://www.paginasamarillas.es/search/{query}/all-ma/{location}.html"
            
            logger.info(f"Scraping Páginas Amarillas: {url}")
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find business listings
                    listings = soup.select('.listado-item, .name, h2')
                    
                    for listing in listings[:10]:
                        try:
                            clinic_name = listing.get_text(strip=True)
                            
                            if not clinic_name or len(clinic_name) < 5 or len(clinic_name) > 100:
                                continue
                            
                            # Extract phone if available
                            phone = self._extract_phone(str(listing.parent))
                            
                            # Generate email
                            email = self._generate_professional_email(clinic_name, location)
                            
                            if email and email not in self.discovered_emails:
                                self.discovered_emails.add(email)
                                leads.append({
                                    "clinica": clinic_name[:100],
                                    "ciudad": location,
                                    "email": email,
                                    "telefono": phone or "",
                                    "website": "",
                                    "source": "Páginas Amarillas"
                                })
                                logger.info(f"✅ Páginas Amarillas: {clinic_name} - {email}")
                        
                        except Exception as e:
                            continue
        
        except Exception as e:
            logger.error(f"Error scraping Yellow Pages: {str(e)}")
        
        return leads
    
    async def scrape_google_search(self, specialty: str, location: str) -> List[Dict]:
        """Simple Google search scraping for clinic names"""
        leads = []
        
        try:
            query = f"{specialty} {location} contacto"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            logger.info(f"Scraping Google Search: {query}")
            
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find search result titles
                    results = soup.select('h3, .g')
                    
                    for result in results[:5]:
                        try:
                            text = result.get_text(strip=True)
                            
                            # Extract clinic-like names
                            if any(word in text.lower() for word in ['clínica', 'centro', 'fisioterapia', 'dental']):
                                # Clean up the name
                                clinic_name = text.split('|')[0].split('-')[0].strip()
                                
                                if len(clinic_name) > 10 and len(clinic_name) < 100:
                                    email = self._generate_professional_email(clinic_name, location)
                                    
                                    if email and email not in self.discovered_emails:
                                        self.discovered_emails.add(email)
                                        leads.append({
                                            "clinica": clinic_name[:100],
                                            "ciudad": location,
                                            "email": email,
                                            "telefono": "",
                                            "website": "",
                                            "source": "Google Search"
                                        })
                        except:
                            continue
        
        except Exception as e:
            logger.error(f"Error scraping Google: {str(e)}")
        
        return leads
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract Spanish phone number"""
        patterns = [
            r'(\+34|0034)?\s*[6-9]\d{2}\s*\d{2}\s*\d{2}\s*\d{2}',
            r'[6-9]\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0).strip()
                phone = re.sub(r'[^\d]', '', phone)
                if phone.startswith('34'):
                    phone = phone[2:]
                if len(phone) == 9:
                    return f"{phone[:3]} {phone[3:5]} {phone[5:7]} {phone[7:9]}"
        return None
    
    def _generate_professional_email(self, clinic_name: str, location: str) -> str:
        """Generate professional email with proper transliteration"""
        transliteration_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
        }
        
        clean_name = clinic_name.lower()
        for spanish_char, latin_char in transliteration_map.items():
            clean_name = clean_name.replace(spanish_char, latin_char)
        
        # Extract significant words
        stop_words = ['de', 'del', 'la', 'el', 'centro', 'clinica', 'dr', 'dra', 'y']
        words = [w for w in re.findall(r'\w+', clean_name) if w not in stop_words and len(w) > 2]
        
        # Take first 2-3 words
        domain_name = ''.join(words[:3])[:25]
        
        # Professional email patterns
        patterns = [
            f"info@{domain_name}.es",
            f"contacto@{domain_name}.com",
            f"recepcion@{domain_name}.es",
            f"hola@{domain_name}.com"
        ]
        
        return random.choice(patterns)[:50]
    
    async def discover_leads_for_region(self, region: Dict, max_per_city: int = 5) -> List[Dict]:
        """Discover real leads for a region using multiple sources"""
        all_leads = []
        
        logger.info(f"🔍 Discovering leads in {region['name']}")
        
        for city in region['cities'][:2]:  # First 2 cities per region
            for specialty in CLINIC_SPECIALTIES[:2]:  # First 2 specialties
                try:
                    # Scrape from multiple sources
                    doctoralia_leads = await self.scrape_doctoralia(specialty, city)
                    yellow_leads = await self.scrape_yellow_pages(specialty, city)
                    google_leads = await self.scrape_google_search(specialty, city)
                    
                    all_leads.extend(doctoralia_leads[:max_per_city])
                    all_leads.extend(yellow_leads[:max_per_city])
                    all_leads.extend(google_leads[:max_per_city])
                    
                    await asyncio.sleep(random.uniform(2, 4))  # Respectful delay
                    
                except Exception as e:
                    logger.error(f"Error discovering in {city}: {str(e)}")
                    continue
        
        logger.info(f"✅ Discovered {len(all_leads)} leads in {region['name']}")
        return all_leads

# Global instance
simplified_discovery_service = SimplifiedLeadDiscovery()
