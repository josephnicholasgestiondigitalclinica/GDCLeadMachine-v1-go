# GDC LeadMachine - Product Requirements Document

## Overview
Automated 24/7 lead generation system for medical clinics in Spain. The system discovers real medical clinics using Google Places API, scores them using AI, and automatically sends outreach emails.

## Core Features

### 1. Google Places API Lead Discovery ✅ ACTIVE
- **Real-time discovery** of medical clinics from Google Maps
- Searches across 50+ Spanish cities
- Covers 15+ medical specialties (dental, medical, physio, etc.)
- Automatic filtering of large corporations/hospitals
- Extracts: name, address, phone, website, Google rating

### 2. 24/7 Automated Scheduling ✅ ACTIVE
- Lead discovery runs every **60 minutes** for **20 minutes**
- Email sending every **120 seconds** (2 accounts rotating)
- WhatsApp queue ready (API-based or link-based)
- Fully autonomous - works while you sleep!

### 3. AI Lead Scoring ✅ ACTIVE - NOW POWERED BY GOOGLE GEMINI
- Uses **Google Gemini 1.5 Flash** for intelligent scoring (1-10)
- Fallback to Emergent LLM/OpenAI if Gemini not configured
- Filters out large chains: Quironsalud, Sanitas, Vithas, HM, etc.
- Prioritizes small private clinics
- Bonus for personal emails (gmail, hotmail)
- Score ≥5 = auto-queued for outreach
- **NEW**: AI-powered personalized email generation

### 4. Multi-Channel Outreach ✅ ACTIVE
- **Email**: Automated sending with personalization
- **WhatsApp**: Link-based (API integration ready)
- Contact history tracking (date, time, method, status)

### 5. PDF Lead Import ✅ ACTIVE
- Import leads from PDF medical directories
- Automatic deduplication
- Corporation filtering applies

### 6. Notion CRM Integration ⚠️ NEEDS CONFIGURATION
- Requires valid Notion database ID (32-char UUID)
- Current ID is placeholder text
- Once configured, syncs all leads to Notion

## Technical Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Scheduler**: APScheduler
- **APIs**: Google Places, Emergent LLM, SMTP

## API Endpoints

### Discovery
- `POST /api/discovery/trigger` - Manual trigger
- `POST /api/discovery/google-places` - Google Places only
- `GET /api/discovery/status` - Check status

### Automation
- `GET /api/automation/status` - Full 24/7 status
- `GET /api/notion/status` - Notion integration status

### Leads
- `GET /api/clinics` - List all leads
- `POST /api/clinics` - Add single lead
- `POST /api/clinics/bulk` - Bulk import
- `POST /api/leads/import-pdf` - PDF import

### Email
- `GET /api/email/stats` - Email statistics
- `GET /api/email/queue` - View queue

### Contacts
- `GET /api/contacts/summary` - Contact overview
- `GET /api/contacts/recent` - Recent contacts
- `GET /api/contacts/history/{clinic_id}` - Per-clinic history

## Current Status (2026-03-23)

### What's Working
- ✅ Google Places API discovering REAL leads (133+ and growing)
- ✅ 24/7 automation active
- ✅ 33+ emails sent
- ✅ AI scoring filtering corporations
- ✅ Dashboard showing real-time stats
- ✅ Login page cleaned up (no credentials shown)

### What Needs User Action
- ⚠️ Notion: Need valid database ID from Notion URL
- ⚠️ WhatsApp API: Optional - works via links currently

## Environment Variables
```
MONGO_URL=mongodb://localhost:27017/
DB_NAME=gdc_database
NOTION_API_KEY=ntn_xxx (set, needs valid DB ID)
NOTION_DATABASE_ID=(needs 32-char UUID from Notion URL)
EMAIL_1_USERNAME=info@gestiondigitalclinica.com
EMAIL_1_PASSWORD=xxx
EMAIL_2_USERNAME=info@gestiondigitalclinica.eu
EMAIL_2_PASSWORD=xxx
EMERGENT_LLM_KEY=sk-emergent-xxx (fallback AI)
GOOGLE_GEMINI_API_KEY=AIza... (PRIMARY AI - NEW!)
GEMINI_MODEL=gemini-1.5-flash
GOOGLE_API_KEY=AIzaSyxxx (for Places API)
```

## Changelog

### 2026-04-18
- **MAJOR**: Integrated Google Gemini AI as primary AI engine
- Added `gemini_ai_service.py` with Gemini 1.5 Flash model
- AI-powered lead scoring (0-3 scale, more precise filtering)
- AI-powered personalized email generation for each clinic
- Fallback system: Gemini → OpenAI/Emergent → Template
- Updated requirements.txt with google-generativeai SDK
- Added `test_gemini.py` for testing AI integration
- Updated documentation with Gemini configuration

### 2026-03-23
- Added Google Places API integration for REAL lead discovery
- Removed default credentials from login page
- Enhanced AI filtering with expanded corporation list
- Updated 24/7 scheduler with Google Places integration
- Created Google Places discovery service
- Added `/api/discovery/google-places` endpoint
- Enhanced automation status to show Google API status
