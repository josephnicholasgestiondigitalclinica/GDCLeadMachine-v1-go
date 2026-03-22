"""
Test script to verify real web scraping works
"""

import asyncio
import sys
sys.path.insert(0, '/app/backend')

from services.real_lead_discovery import real_discovery_service

async def test_scraping():
    print("🧪 Testing REAL web scraping...")
    print("="*60)
    
    # Initialize browser
    await real_discovery_service.initialize()
    
    # Test 1: Google Maps scraping
    print("\n1️⃣ Testing Google Maps scraping...")
    test_region = {"name": "Madrid", "cities": ["Madrid"]}
    
    google_leads = await real_discovery_service.scrape_google_maps(
        "clínica dental", 
        "Madrid"
    )
    
    print(f"✅ Found {len(google_leads)} leads from Google Maps")
    if google_leads:
        print("\nSample lead:")
        print(f"  Clínica: {google_leads[0]['clinica']}")
        print(f"  Email: {google_leads[0]['email']}")
        print(f"  Teléfono: {google_leads[0]['telefono']}")
        print(f"  Website: {google_leads[0]['website']}")
    
    # Test 2: Doctoralia scraping
    print("\n2️⃣ Testing Doctoralia scraping...")
    doctoralia_leads = await real_discovery_service.scrape_doctoralia(
        "clínica dental",
        "Madrid"
    )
    
    print(f"✅ Found {len(doctoralia_leads)} leads from Doctoralia")
    if doctoralia_leads:
        print("\nSample lead:")
        print(f"  Clínica: {doctoralia_leads[0]['clinica']}")
        print(f"  Email: {doctoralia_leads[0]['email']}")
    
    # Close browser
    await real_discovery_service.close()
    
    print("\n" + "="*60)
    print(f"🎉 Test complete! Total: {len(google_leads) + len(doctoralia_leads)} real leads")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_scraping())
