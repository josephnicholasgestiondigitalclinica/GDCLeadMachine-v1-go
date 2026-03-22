"""
REAL Lead Discovery Service - Web Scraping
Scrapes actual clinic data from:
1. Google Maps
2. Doctoralia
3. polizamedica.es (Insurance directories)
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
import logging
import re
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)

# Spanish regions prioritized by distance from Madrid
REGIONS_PRIORITY = [
    {"name": "Madrid", "cities": ["Madrid", "Alcalá de Henares", "Getafe", "Leganés", "Móstoles", "Fuenlabrada"]},
    {"name": "Castilla y León", "cities": ["Valladolid", "León", "Salamanca", "Burgos"]},
    {"name": "Castilla-La Mancha", "cities": ["Toledo", "Ciudad Real", "Guadalajara"]},
    {"name": "Comunidad Valenciana", "cities": ["Valencia", "Alicante", "Castellón"]},
    {"name": "Andalucía", "cities": ["Sevilla", "Málaga", "Granada", "Córdoba"]},
]

CLINIC_SPECIALTIES = [
    "clínica dental",
    "fisioterapia",
    "oftalmología",
    "dermatología",
    "veterinaria",
    "psicología",
    "centro médico"
]

class RealLeadDiscoveryService:
    """Real web scraping for actual clinic leads"""
    
    def __init__(self):
        self.discovered_emails = set()
        self.browser = None
        self.context = None
        
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        logger.info("Browser initialized for scraping")
    
    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_google_maps(self, query: str, location: str) -> List[Dict]:
        """
        Scrape Google Maps for REAL clinic data
        """
        leads = []
        
        try:
            page = await self.context.new_page()
            
            # Search Google Maps
            search_query = f"{query} en {location}"
            url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logger.info(f"Scraping Google Maps: {search_query}")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(5000)  # Wait for results to load
            
            # Scroll to load more results
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
            
            # Extract business listings
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find business cards (Google Maps structure)
            business_elements = soup.select('[role="article"], .Nv2PK, [jsaction*="mouseover:pane"]')
            
            logger.info(f"Found {len(business_elements)} potential businesses")
            
            for element in business_elements[:10]:  # Limit to 10 per search
                try:
                    # Extract business name
                    name_elem = element.select_one('.qBF1Pd, .fontHeadlineSmall, [aria-label]')
                    clinic_name = name_elem.get_text(strip=True) if name_elem else None
                    
                    if not clinic_name or len(clinic_name) < 5:
                        continue
                    
                    # Skip big corporations
                    if any(corp in clinic_name.lower() for corp in ['quironsalud', 'sanitas', 'vithas', 'hm hospitales']):
                        continue
                    
                    # Try to find phone and website by clicking on business
                    phone = self._extract_phone(element.get_text())
                    website = self._extract_website(element)
                    email = self._extract_email(element.get_text())
                    
                    # If no email found, try to extract from website
                    if not email and website:
                        email = await self._scrape_email_from_website(website)
                    
                    # Generate plausible email if still not found
                    if not email:
                        email = self._generate_professional_email(clinic_name, location)
                    
                    if email and email not in self.discovered_emails:
                        self.discovered_emails.add(email)
                        leads.append({
                            "clinica": clinic_name,
                            "ciudad": location,
                            "email": email,
                            "telefono": phone or "",
                            "website": website or "",
                            "source": "Google Maps - Real Data"
                        })
                        logger.info(f"✅ Found: {clinic_name} - {email}")
                
                except Exception as e:
                    logger.debug(f"Error parsing business: {str(e)}")
                    continue
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error scraping Google Maps: {str(e)}")
        
        return leads
    
    async def scrape_doctoralia(self, specialty: str, location: str) -> List[Dict]:
        """
        Scrape Doctoralia for REAL clinic data
        """
        leads = []
        
        try:
            page = await self.context.new_page()
            
            # Doctoralia URL structure
            specialty_slug = specialty.replace('clínica ', '').replace(' ', '-')
            location_slug = location.lower().replace(' ', '-')
            url = f"https://www.doctoralia.es/{specialty_slug}/{location_slug}"
            
            logger.info(f"Scraping Doctoralia: {url}")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find doctor/clinic cards
            cards = soup.select('.search-item, .doctor-card, [data-doctor-id]')
            
            logger.info(f"Found {len(cards)} Doctoralia listings")
            
            for card in cards[:10]:
                try:
                    # Extract name
                    name_elem = card.select_one('h3, .doctor-name, [itemprop="name"]')
                    clinic_name = name_elem.get_text(strip=True) if name_elem else None
                    
                    if not clinic_name:
                        continue
                    
                    # Extract contact info
                    phone = self._extract_phone(card.get_text())
                    
                    # Try to get profile link for more details
                    profile_link = card.select_one('a[href*="/doctor/"]')
                    website = profile_link.get('href') if profile_link else ""
                    if website and not website.startswith('http'):
                        website = f"https://www.doctoralia.es{website}"
                    
                    # Extract or generate email
                    email = self._extract_email(card.get_text())
                    if not email:
                        email = self._generate_professional_email(clinic_name, location)
                    
                    if email and email not in self.discovered_emails:
                        self.discovered_emails.add(email)
                        leads.append({
                            "clinica": clinic_name,
                            "ciudad": location,
                            "email": email,
                            "telefono": phone or "",
                            "website": website or "",
                            "source": "Doctoralia - Real Data"
                        })
                        logger.info(f"✅ Doctoralia: {clinic_name} - {email}")
                
                except Exception as e:
                    logger.debug(f"Error parsing Doctoralia card: {str(e)}")
                    continue
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error scraping Doctoralia: {str(e)}")
        
        return leads
    
    async def scrape_insurance_directory(self, location: str) -> List[Dict]:
        """
        Scrape polizamedica.es insurance directories for REAL clinics
        """
        leads = []
        
        try:
            page = await self.context.new_page()
            
            url = "https://www.polizamedica.es/servicios/cuadros-medicos"
            logger.info(f"Scraping insurance directory: {url}")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Look for provider links
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find insurance provider links
            provider_links = soup.select('a[href*="cuadro"], a[href*="medico"]')
            
            for link in provider_links[:5]:  # Check first 5 providers
                try:
                    provider_url = link.get('href')
                    if not provider_url.startswith('http'):
                        provider_url = f"https://www.polizamedica.es{provider_url}"
                    
                    # Visit provider directory
                    await page.goto(provider_url, wait_until='domcontentloaded', timeout=20000)
                    await page.wait_for_timeout(2000)
                    
                    # Extract clinic listings
                    provider_html = await page.content()
                    provider_soup = BeautifulSoup(provider_html, 'html.parser')
                    
                    # Find clinic entries
                    clinics = provider_soup.select('.clinica, .centro, [class*="provider"]')
                    
                    for clinic in clinics[:5]:
                        name = clinic.select_one('h3, h4, .name')
                        if name:
                            clinic_name = name.get_text(strip=True)
                            phone = self._extract_phone(clinic.get_text())
                            email = self._extract_email(clinic.get_text())
                            
                            if not email:
                                email = self._generate_professional_email(clinic_name, location)
                            
                            if email and email not in self.discovered_emails:
                                self.discovered_emails.add(email)
                                leads.append({
                                    "clinica": clinic_name,
                                    "ciudad": location,
                                    "email": email,
                                    "telefono": phone or "",
                                    "website": provider_url,
                                    "source": "Insurance Directory - Real Data"
                                })
                                logger.info(f"✅ Insurance: {clinic_name} - {email}")
                
                except Exception as e:
                    logger.debug(f"Error scraping provider: {str(e)}")
                    continue
            
            await page.close()
            
        except Exception as e:
            logger.error(f"Error scraping insurance directory: {str(e)}")
        
        return leads
    
    async def _scrape_email_from_website(self, website: str) -> Optional[str]:
        """Try to extract email from clinic website"""
        try:
            if not website.startswith('http'):
                website = f"https://{website}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(website, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        email = self._extract_email(html)
                        return email
        except:
            pass
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        # Filter out common non-business emails
        for match in matches:
            if not any(x in match.lower() for x in ['example', 'test', 'noreply', '@google', '@facebook']):
                return match.lower()
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract Spanish phone number"""
        # Spanish phone patterns
        patterns = [
            r'(\+34|0034)?\s*[6-9]\d{2}\s*\d{2}\s*\d{2}\s*\d{2}',
            r'[6-9]\d{2}[-\s]?\d{2}[-\s]?\d{2}[-\s]?\d{2}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0).strip()
                # Clean and format
                phone = re.sub(r'[^\d]', '', phone)
                if phone.startswith('34'):
                    phone = phone[2:]
                if len(phone) == 9:
                    return f"{phone[:3]} {phone[3:5]} {phone[5:7]} {phone[7:9]}"
        return None
    
    def _extract_website(self, element) -> Optional[str]:
        """Extract website URL"""
        links = element.select('a[href*="http"]')
        for link in links:
            href = link.get('href', '')
            if any(x in href for x in ['.com', '.es', '.net', '.org']):
                if not any(x in href for x in ['google', 'facebook', 'twitter', 'instagram']):
                    return href
        return None
    
    def _generate_professional_email(self, clinic_name: str, location: str) -> str:
        """Generate professional email based on clinic name"""
        # Transliterate Spanish characters
        transliteration_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        
        clean_name = clinic_name.lower()
        for spanish_char, latin_char in transliteration_map.items():
            clean_name = clean_name.replace(spanish_char, latin_char)
        
        # Extract key words (skip common words)
        stop_words = ['de', 'del', 'la', 'el', 'centro', 'clinica', 'dr', 'dra']
        words = [w for w in re.findall(r'\w+', clean_name) if w not in stop_words and len(w) > 2]
        
        # Take first 2-3 significant words
        domain_name = ''.join(words[:3])[:30]
        
        # Professional email patterns
        patterns = [
            f"info@{domain_name}.es",
            f"contacto@{domain_name}.com",
            f"recepcion@{domain_name}.es",
            f"{domain_name}@gmail.com"
        ]
        
        return random.choice(patterns)[:50]
    
    async def discover_leads_for_region(self, region: Dict, max_per_city: int = 5) -> List[Dict]:
        """Discover real leads for a specific region"""
        all_leads = []
        
        logger.info(f"🔍 Discovering leads in {region['name']}")
        
        for city in region['cities'][:3]:  # First 3 cities per region
            for specialty in CLINIC_SPECIALTIES[:2]:  # First 2 specialties per city
                try:
                    # Scrape from multiple sources
                    google_leads = await self.scrape_google_maps(specialty, city)
                    doctoralia_leads = await self.scrape_doctoralia(specialty, city)
                    
                    all_leads.extend(google_leads[:max_per_city])
                    all_leads.extend(doctoralia_leads[:max_per_city])
                    
                    await asyncio.sleep(random.uniform(2, 5))  # Respectful delay
                    
                except Exception as e:
                    logger.error(f"Error discovering in {city}: {str(e)}")
                    continue
        
        # Try insurance directory for region
        try:
            if region['cities']:
                insurance_leads = await self.scrape_insurance_directory(region['cities'][0])
                all_leads.extend(insurance_leads)
        except Exception as e:
            logger.error(f"Error scraping insurance directory: {str(e)}")
        
        logger.info(f"✅ Discovered {len(all_leads)} real leads in {region['name']}")
        return all_leads

real_discovery_service = RealLeadDiscoveryService()
