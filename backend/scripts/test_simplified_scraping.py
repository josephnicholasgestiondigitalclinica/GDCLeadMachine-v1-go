"""
Test simplified scraping
"""

import asyncio
import sys
sys.path.insert(0, '/app/backend')

from services.simplified_lead_discovery import simplified_discovery_service

async def test():
    print("🧪 Testing simplified scraping...")
    
    await simplified_discovery_service.initialize()
    
    # Test Doctoralia
    print("\n1️⃣ Testing Doctoralia...")
    leads = await simplified_discovery_service.scrape_doctoralia("clínica dental", "Madrid")
    print(f"✅ Found {len(leads)} leads")
    
    if leads:
        print(f"\nSample: {leads[0]['clinica']} - {leads[0]['email']}")
    
    # Test Yellow Pages
    print("\n2️⃣ Testing Páginas Amarillas...")
    leads2 = await simplified_discovery_service.scrape_yellow_pages("fisioterapia", "Madrid")
    print(f"✅ Found {len(leads2)} leads")
    
    if leads2:
        print(f"\nSample: {leads2[0]['clinica']} - {leads2[0]['email']}")
    
    await simplified_discovery_service.close()
    
    print(f"\n🎉 Total: {len(leads) + len(leads2)} leads discovered!")

if __name__ == "__main__":
    asyncio.run(test())
