"""
Test script for Google Gemini AI integration
Run this to verify Gemini is working correctly
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

async def test_gemini_integration():
    """Test Gemini AI service"""
    print("=" * 60)
    print("Testing Google Gemini AI Integration")
    print("=" * 60)

    # Test data
    test_clinic = {
        "clinica": "Clínica Dental Test",
        "ciudad": "Madrid",
        "email": "info@test-dental.com",
        "telefono": "+34 600 123 456",
        "website": "www.test-dental.com"
    }

    business_info = {
        "name": "Gestión Digital Clínica",
        "owner": "José Cabrejas",
        "email": "contacto@gestiondigitalclinica.es",
        "website": "www.gestiondigitalclinica.es",
        "phone": "637 971 233"
    }

    try:
        from services.gemini_ai_service import gemini_ai_service

        print(f"\n1. Checking Gemini configuration...")
        print(f"   Configured: {gemini_ai_service.is_configured}")
        print(f"   Model: {gemini_ai_service.model_name}")

        if not gemini_ai_service.is_configured:
            print("\n❌ Gemini not configured. Set GOOGLE_GEMINI_API_KEY environment variable.")
            print("   The system will use fallback templates instead.")
            return

        print("\n2. Testing lead scoring...")
        scoring_result = await gemini_ai_service.score_clinic_with_ai(test_clinic)
        print(f"   Available: {scoring_result.get('available', False)}")
        print(f"   Score: {scoring_result.get('score', 0)}/3")
        print(f"   Reason: {scoring_result.get('reason', 'N/A')}")

        print("\n3. Testing email generation...")
        email_result = await gemini_ai_service.generate_personalized_email(
            test_clinic,
            business_info
        )
        print(f"   Available: {email_result.get('available', False)}")
        print(f"   Subject: {email_result.get('subject', 'N/A')}")
        print(f"   Body preview: {email_result.get('body', 'N/A')[:100]}...")

        print("\n" + "=" * 60)
        print("✅ Gemini AI Integration Test Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error testing Gemini: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check for API key in environment
    api_key = (
        os.environ.get('GOOGLE_GEMINI_API_KEY')
        or os.environ.get('GEMINI_API_KEY')
        or os.environ.get('GOOGLE_AI_API_KEY')
    )

    if not api_key:
        print("\n⚠️  WARNING: No Gemini API key found in environment variables")
        print("   Set GOOGLE_GEMINI_API_KEY to test the integration")
        print("   The test will show fallback behavior\n")

    asyncio.run(test_gemini_integration())
