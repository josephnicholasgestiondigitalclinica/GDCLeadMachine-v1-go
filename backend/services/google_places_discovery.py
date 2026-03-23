"""
Google Places API Lead Discovery Service
Uses Google Maps Places API to discover real medical clinics in Spain
This is the REAL lead discovery - actual businesses from Google Maps!
"""

import os
import aiohttp
import asyncio
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Spanish regions and cities for search
SPANISH_CITIES = [
    # Madrid region
    "Madrid", "Alcalá de Henares", "Alcobendas", "Alcorcón", "Aranjuez",
    "Arganda del Rey", "Boadilla del Monte", "Collado Villalba", "Colmenar Viejo",
    "Coslada", "Fuenlabrada", "Getafe", "Las Rozas", "Leganés", "Majadahonda",
    "Móstoles", "Parla", "Pozuelo de Alarcón", "Rivas-Vaciamadrid", "San Sebastián de los Reyes",
    "Torrejón de Ardoz", "Tres Cantos", "Valdemoro", "Villanueva de la Cañada",
    # Barcelona region  
    "Barcelona", "L'Hospitalet de Llobregat", "Badalona", "Terrassa", "Sabadell",
    "Mataró", "Santa Coloma de Gramenet", "Cornellà de Llobregat", "Sant Boi de Llobregat",
    # Valencia region
    "Valencia", "Alicante", "Elche", "Castellón de la Plana", "Torrent", "Gandía",
    # Andalusia
    "Sevilla", "Málaga", "Córdoba", "Granada", "Jerez de la Frontera", "Almería", "Cádiz",
    # Other major cities
    "Bilbao", "Zaragoza", "Murcia", "Palma de Mallorca", "Las Palmas", "Valladolid",
    "Vigo", "Gijón", "A Coruña", "Vitoria-Gasteiz", "Santander", "Pamplona", "San Sebastián"
]

# Medical clinic search queries
CLINIC_SEARCH_QUERIES = [
    "clínica médica",
    "clínica dental",
    "consultorio médico",
    "centro médico",
    "fisioterapia",
    "podología",
    "clínica oftalmológica",
    "centro de salud privado",
    "clínica dermatológica",
    "clínica estética",
    "rehabilitación",
    "logopedia",
    "psicología clínica",
    "nutricionista",
    "clínica veterinaria"
]

# Excluded keywords (large chains/hospitals)
EXCLUDED_KEYWORDS = [
    "hospital", "hospitales", "universitario", "universitaria",
    "quironsalud", "quiron", "sanitas", "vithas", "viamed", "hospiten",
    "hm hospitales", "hm madrid", "ruber", "mapfre", "asisa", "adeslas",
    "dkv", "cigna", "grupo", "corporation", "corporacion"
]


class GooglePlacesDiscovery:
    """
    Real lead discovery using Google Maps Places API
    Finds actual medical clinics with their contact info
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY', '')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.discovered_place_ids = set()  # Avoid duplicates
        
        if self.api_key:
            logger.info("🗺️ Google Places Discovery initialized with API key")
        else:
            logger.warning("⚠️ Google API key not configured")
    
    def _is_excluded(self, name: str) -> bool:
        """Check if the place should be excluded (large chain/hospital)"""
        name_lower = name.lower()
        for keyword in EXCLUDED_KEYWORDS:
            if keyword in name_lower:
                return True
        return False
    
    def _extract_email_from_website(self, website: str) -> Optional[str]:
        """Generate potential email from website domain"""
        if not website:
            return None
        
        try:
            # Extract domain
            domain = website.replace("https://", "").replace("http://", "").replace("www.", "")
            domain = domain.split("/")[0]
            
            # Common email patterns
            return f"info@{domain}"
        except:
            return None
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize Spanish phone number"""
        if not phone:
            return ""
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Add Spanish country code if missing
        if len(cleaned) == 9 and cleaned[0] in '6789':
            cleaned = f"+34{cleaned}"
        
        return cleaned
    
    async def search_nearby(self, query: str, city: str) -> List[Dict]:
        """
        Search for places using Text Search API
        """
        if not self.api_key:
            return []
        
        results = []
        search_query = f"{query} en {city}, España"
        
        try:
            url = f"{self.base_url}/textsearch/json"
            params = {
                "query": search_query,
                "key": self.api_key,
                "language": "es",
                "region": "es"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "OK":
                            for place in data.get("results", []):
                                place_id = place.get("place_id")
                                
                                # Skip if already processed
                                if place_id in self.discovered_place_ids:
                                    continue
                                
                                name = place.get("name", "")
                                
                                # Skip excluded businesses
                                if self._is_excluded(name):
                                    logger.debug(f"Excluded: {name}")
                                    continue
                                
                                self.discovered_place_ids.add(place_id)
                                
                                # Get detailed info
                                details = await self._get_place_details(place_id)
                                
                                if details:
                                    results.append(details)
                                    logger.info(f"✅ Found: {details['clinica']} - {details.get('telefono', 'No phone')}")
                        
                        elif data.get("status") == "ZERO_RESULTS":
                            logger.debug(f"No results for: {search_query}")
                        else:
                            logger.warning(f"API status: {data.get('status')} - {data.get('error_message', '')}")
        
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
        
        return results
    
    async def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place including phone, website
        """
        try:
            url = f"{self.base_url}/details/json"
            params = {
                "place_id": place_id,
                "key": self.api_key,
                "language": "es",
                "fields": "name,formatted_address,formatted_phone_number,international_phone_number,website,types,rating,user_ratings_total,opening_hours,business_status"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "OK":
                            result = data.get("result", {})
                            
                            name = result.get("name", "")
                            address = result.get("formatted_address", "")
                            phone = result.get("formatted_phone_number", "") or result.get("international_phone_number", "")
                            website = result.get("website", "")
                            rating = result.get("rating", 0)
                            reviews = result.get("user_ratings_total", 0)
                            
                            # Skip if no contact info
                            if not phone and not website:
                                return None
                            
                            # Extract city from address
                            city = ""
                            address_parts = address.split(",")
                            if len(address_parts) >= 2:
                                city = address_parts[-2].strip()
                            
                            # Generate email from website
                            email = self._extract_email_from_website(website)
                            
                            return {
                                "clinica": name,
                                "ciudad": city,
                                "direccion": address,
                                "telefono": self._normalize_phone(phone),
                                "email": email,
                                "website": website,
                                "fuente": "Google Places API",
                                "estado": "Sin contactar",
                                "google_rating": rating,
                                "google_reviews": reviews,
                                "place_id": place_id,
                                "discovered_at": datetime.utcnow().isoformat()
                            }
        
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
        
        return None
    
    async def discover_leads(self, max_leads: int = 100, cities: List[str] = None) -> List[Dict]:
        """
        Discover leads from Google Places API
        Searches multiple cities and clinic types
        """
        if not self.api_key:
            logger.warning("Google API key not configured - cannot discover leads")
            return []
        
        logger.info("="*60)
        logger.info("🗺️ STARTING GOOGLE PLACES LEAD DISCOVERY")
        logger.info(f"🎯 Target: {max_leads} leads")
        logger.info("="*60)
        
        all_leads = []
        cities_to_search = cities or SPANISH_CITIES[:20]  # Limit cities per cycle
        
        for city in cities_to_search:
            if len(all_leads) >= max_leads:
                break
            
            # Rotate through different search queries
            for query in CLINIC_SEARCH_QUERIES[:5]:  # Limit queries per city
                if len(all_leads) >= max_leads:
                    break
                
                leads = await self.search_nearby(query, city)
                all_leads.extend(leads)
                
                # Rate limiting - be nice to the API
                await asyncio.sleep(0.5)
            
            logger.info(f"📍 {city}: Found {len(all_leads)} total leads so far")
        
        logger.info("="*60)
        logger.info(f"✅ DISCOVERY COMPLETE: {len(all_leads)} leads found")
        logger.info("="*60)
        
        return all_leads[:max_leads]


# Singleton instance
google_places_discovery = GooglePlacesDiscovery()
