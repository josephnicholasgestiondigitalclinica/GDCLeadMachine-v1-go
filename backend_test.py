#!/usr/bin/env python3
"""
Backend API Testing for GDC LeadMachine
Tests the multi-channel contact history features and existing endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://deployment-core-1.preview.emergentagent.com/api"

def test_health_check():
    """Test GET /api/ - Health check endpoint"""
    print("\n=== Testing Health Check API ===")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify expected fields
            if "message" in data and "status" in data:
                print("✅ Health check passed - API is running")
                return True
            else:
                print("❌ Health check failed - missing expected fields")
                return False
        else:
            print(f"❌ Health check failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed - Connection error: {str(e)}")
        return False

def test_contacts_summary():
    """Test GET /api/contacts/summary - Contact summary with queue stats"""
    print("\n=== Testing Contact Summary API ===")
    try:
        response = requests.get(f"{BACKEND_URL}/contacts/summary", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify expected structure
            required_fields = ["contact_summary", "email_queue", "whatsapp_queue"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Check email_queue structure
                email_queue = data.get("email_queue", {})
                email_required = ["pending", "sent", "failed"]
                email_missing = [field for field in email_required if field not in email_queue]
                
                # Check whatsapp_queue structure
                whatsapp_queue = data.get("whatsapp_queue", {})
                whatsapp_required = ["pending", "sent", "failed"]
                whatsapp_missing = [field for field in whatsapp_required if field not in whatsapp_queue]
                
                if not email_missing and not whatsapp_missing:
                    print("✅ Contact summary API passed - all required fields present")
                    print(f"Email Queue Stats: {email_queue}")
                    print(f"WhatsApp Queue Stats: {whatsapp_queue}")
                    return True
                else:
                    print(f"❌ Contact summary API failed - missing queue fields: email={email_missing}, whatsapp={whatsapp_missing}")
                    return False
            else:
                print(f"❌ Contact summary API failed - missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Contact summary API failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Contact summary API failed - Connection error: {str(e)}")
        return False

def test_recent_contacts():
    """Test GET /api/contacts/recent?limit=10 - Recent contacts"""
    print("\n=== Testing Recent Contacts API ===")
    try:
        response = requests.get(f"{BACKEND_URL}/contacts/recent?limit=10", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify expected structure
            required_fields = ["contacts", "count"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                contacts = data.get("contacts", [])
                count = data.get("count", 0)
                
                print(f"✅ Recent contacts API passed - returned {count} contacts")
                
                # If there are contacts, verify their structure
                if contacts:
                    contact = contacts[0]
                    contact_fields = ["clinic_id", "method", "status", "timestamp"]
                    contact_missing = [field for field in contact_fields if field not in contact]
                    
                    if contact_missing:
                        print(f"⚠️ Warning: Contact records missing fields: {contact_missing}")
                    else:
                        print("✅ Contact record structure is correct")
                
                return True
            else:
                print(f"❌ Recent contacts API failed - missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Recent contacts API failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Recent contacts API failed - Connection error: {str(e)}")
        return False

def test_dashboard_stats():
    """Test GET /api/stats/dashboard - Dashboard statistics (regression test)"""
    print("\n=== Testing Dashboard Statistics API ===")
    try:
        response = requests.get(f"{BACKEND_URL}/stats/dashboard", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify expected fields
            required_fields = ["total_leads", "emails_sent", "responded", "clients", "high_score", "pending_followups"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Dashboard statistics API passed - all required fields present")
                return True
            else:
                print(f"❌ Dashboard statistics API failed - missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Dashboard statistics API failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard statistics API failed - Connection error: {str(e)}")
        return False

def test_clinics_list():
    """Test GET /api/clinics?limit=5 - List of clinics (regression test)"""
    print("\n=== Testing Clinics List API ===")
    try:
        response = requests.get(f"{BACKEND_URL}/clinics?limit=5", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify expected structure
            required_fields = ["clinics", "total", "skip", "limit"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                clinics = data.get("clinics", [])
                total = data.get("total", 0)
                
                print(f"✅ Clinics list API passed - returned {len(clinics)} clinics out of {total} total")
                
                # If there are clinics, verify their structure
                if clinics:
                    clinic = clinics[0]
                    clinic_fields = ["_id", "clinica", "ciudad", "email"]
                    clinic_missing = [field for field in clinic_fields if field not in clinic]
                    
                    if clinic_missing:
                        print(f"⚠️ Warning: Clinic records missing fields: {clinic_missing}")
                    else:
                        print("✅ Clinic record structure is correct")
                
                return True
            else:
                print(f"❌ Clinics list API failed - missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Clinics list API failed - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Clinics list API failed - Connection error: {str(e)}")
        return False

def main():
    """Run all backend API tests"""
    print(f"Starting GDC LeadMachine Backend API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Run all tests
    test_results = {
        "Health Check API": test_health_check(),
        "Contact Summary API": test_contacts_summary(),
        "Recent Contacts API": test_recent_contacts(),
        "Dashboard Statistics API": test_dashboard_stats(),
        "Clinics List API": test_clinics_list()
    }
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\n❌ Some tests failed. Check the detailed output above.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()