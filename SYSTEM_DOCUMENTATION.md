# GDC Lead Management System - Technical Documentation

## Overview
Comprehensive lead management system with:
- Automated AI scoring
- Notion integration
- Email automation (1 email per 120 seconds per account)
- 24/7 operation

## Features Implemented

### 1. Notion Integration
- **API Key**: Configured and working
- **Database**: DIRECTORY 1 MAD SEG
- **Auto-sync**: All clinics automatically saved to Notion
- **Fields**: Nombre, Ciudad, Email, Teléfono, Score, Estado, Website, Fuente

### 2. AI Scoring System (Automated)
- **Triggers**: Automatically on every new clinic added
- **Criteria**:
  - Email authenticity (validates format & deliverability)
  - Excludes big corporations (Quironsalud, Sanitas, etc.)
  - BETTER scores for:
    - Gmail/Hotmail emails (+3 points)
    - No website or poor website (+2 points)
    - Small/medium clinics
  - Score range: 1-10
  - Only clinics with score ≥5 are added to email queue

### 3. Email Automation
- **Configured Accounts**:
  - info@gestiondigitalclinica.com
  - info@gestiondigitalclinica.eu
- **Rate Limiting**: 1 email every 120 seconds per account
- **Template**: Personalized with clinic name
- **Content**: Full service description (as per your template)
- **Signature**: Includes logo, contact info, José Cabrejas details
- **Attachments**: PDF support available
- **24/7 Operation**: Runs continuously via scheduler

### 4. Automation Pipeline
```
New Clinic → AI Scoring → Save to Notion → Queue Email → Send (respecting 120s interval)
```

### 5. Email Management UI
- Add/remove email accounts
- View queue status
- Real-time statistics
- Monitor sent/pending/failed emails

### 6. Anti-Spam Measures
- 120-second interval between emails per account
- Retry logic (max 3 attempts)
- Professional email template
- Proper SMTP authentication
- Rate limiting per account

## API Endpoints

### Clinics
- `POST /api/clinics` - Add new clinic (triggers automation)
- `POST /api/clinics/bulk` - Bulk import
- `GET /api/clinics` - Get clinics
- `POST /api/clinics/{id}/score` - Manual scoring

### Email Management
- `POST /api/email-accounts` - Add email account
- `GET /api/email-accounts` - List accounts
- `GET /api/email/stats` - Email statistics
- `GET /api/email/queue` - View queue
- `POST /api/email/attachments` - Upload PDF

### Dashboard
- `GET /api/stats/dashboard` - Real-time statistics

## Configuration Files

### Backend Environment (`.env`)
```
NOTION_API_KEY=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
EMAIL_1_USERNAME=info@gestiondigitalclinica.com
EMAIL_1_PASSWORD=Leads2026@!!
EMAIL_2_USERNAME=info@gestiondigitalclinica.eu
EMAIL_2_PASSWORD=Leads2026@!!
SMTP_HOST=smtp.serviciodecorreo.es
SMTP_PORT=465
EMAIL_INTERVAL_SECONDS=120
MAX_LEADS=50000
```

## Email Template
- **Subject**: Sistema integral para centralizar la operativa de {Clinic Name}
- **From**: José Cabrejas
- **Content**: Full service description with HTML formatting
- **Logo**: Embedded in header and signature
- **Contact**: contacto@gestiondigitalclinica.es, 637 971 233
- **Website**: www.gestiondigitalclinica.es

## How It Works

1. **Add Clinic** (Manual or Bulk):
   - User adds clinic data
   - System validates email
   - AI scores the clinic immediately

2. **AI Scoring**:
   - Checks if big corporation (auto-reject)
   - Validates email authenticity
   - Scans website (if exists)
   - Assigns score 1-10

3. **If Score ≥5**:
   - Save to Notion database
   - Add to email queue
   - Mark as "pending"

4. **Email Queue Processor** (runs every 10 seconds):
   - Checks if any account can send (120s passed since last)
   - Gets next pending email
   - Sends personalized email
   - Updates Notion status
   - Marks last_sent timestamp

5. **Dashboard Updates** (every 30 seconds):
   - Total leads
   - Emails sent
   - Response rate
   - Queue status

## Capacity
- **Storage**: 50,000 leads (configurable)
- **Email Accounts**: Unlimited (add via UI)
- **Sending Rate**: 1 email per 120 seconds per account
- **Example**: 2 accounts = 60 emails/hour, 1,440 emails/day

## Monitoring
- Real-time dashboard
- Email queue visibility
- Account status
- Success/failure tracking
- Auto-retry on failure (max 3 attempts)

## Next Steps for User
1. Test with sample clinic
2. Monitor email sending
3. Add more email accounts as needed
4. Track responses in Notion
5. Adjust AI scoring criteria if needed
