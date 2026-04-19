# Google Gemini AI Integration Setup Guide

## Overview

GDC LeadMachine now uses **Google Gemini AI** as the primary AI engine for intelligent lead scoring and personalized email generation. This upgrade provides:

- ✅ **More accurate lead scoring** (filters out large corporations automatically)
- ✅ **Personalized email generation** for each clinic
- ✅ **Better cost-performance ratio** (Gemini 1.5 Flash is efficient)
- ✅ **Automatic fallback** to OpenAI/Emergent if needed
- ✅ **24/7 autonomous operation** powered by AI

## Getting Your Gemini API Key

### Step 1: Go to Google AI Studio
1. Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account

### Step 2: Create API Key
1. Click **"Create API Key"**
2. Select a project or create a new one
3. Copy your API key (starts with `AIza...`)

### Step 3: Configure in Railway
1. Go to your Railway project dashboard
2. Navigate to **Variables** tab
3. Add new variable:
   - Name: `GOOGLE_GEMINI_API_KEY`
   - Value: Your API key from Step 2

### Step 4: (Optional) Choose Model
By default, the system uses `gemini-1.5-flash` (recommended for speed and cost).

To use a different model, add:
- Name: `GEMINI_MODEL`
- Value: `gemini-1.5-pro` (more powerful but slower)

### Step 5: Redeploy
Railway will automatically redeploy with the new configuration.

## How It Works

### 1. Lead Scoring (AI-Powered)
When a new clinic is discovered:
1. Gemini AI analyzes the clinic data
2. Scores 0-3 based on:
   - Size (small/medium preferred)
   - Email type (personal domains = bonus)
   - Website quality (simple = good prospect)
   - Corporation detection (auto-reject)
3. Score is multiplied by additional factors (email validation, etc.)
4. Final score 1-10, only ≥5 proceed to email queue

### 2. Email Generation (AI-Powered)
When sending an email:
1. Gemini AI generates personalized content for each clinic
2. Customizes based on:
   - Clinic name and location
   - Whether they have a website
   - Type of clinic (dental, physio, etc.)
3. Falls back to template if AI unavailable
4. Email includes "✨ Personalizado con Google Gemini AI" badge

### 3. Fallback System
The system has 3 levels:
1. **Primary**: Google Gemini AI (if configured)
2. **Secondary**: OpenAI/Emergent LLM (if configured)
3. **Tertiary**: Static templates (always available)

## Testing the Integration

### Option 1: Using the Test Script
```bash
# From repository root
python test_gemini.py
```

This will:
- Check if Gemini is configured
- Test lead scoring with sample data
- Test email generation
- Display results

### Option 2: Check Logs
After deployment, check Railway logs for:
```
🤖 Google Gemini AI Service initialized with model: gemini-1.5-flash
```

### Option 3: Trigger Manual Discovery
1. Login to the dashboard
2. Go to Discovery tab
3. Click "Trigger Discovery"
4. Check logs for "Gemini AI scored..."

## Pricing & Usage

### Gemini 1.5 Flash (Recommended)
- **Free tier**: 15 requests/minute, 1M tokens/day
- **Paid**: $0.075 per 1M input tokens
- **Perfect for**: 24/7 automated operation

### Gemini 1.5 Pro (Optional)
- **Free tier**: 2 requests/minute
- **Paid**: $1.25 per 1M input tokens
- **Use when**: Need highest quality analysis

For current pricing: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)

## Troubleshooting

### Error: "Gemini not configured"
**Solution**: Add `GOOGLE_GEMINI_API_KEY` to Railway variables

### Error: "API key not valid"
**Solution**:
1. Check the API key is correct (starts with `AIza`)
2. Ensure the API is enabled in Google Cloud Console
3. Check quota limits aren't exceeded

### Emails using template instead of AI
**Possible causes**:
1. Gemini not configured → Add API key
2. API quota exceeded → Wait or upgrade plan
3. API error → Check Railway logs for details

**Note**: The system will work fine with templates if AI is unavailable

### "Import error: google.generativeai"
**Solution**: Redeploy to install dependencies
```bash
railway up
```

## Advanced Configuration

### Environment Variables
```bash
# Required
GOOGLE_GEMINI_API_KEY=AIza...

# Optional
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
```

### Disabling AI Email Generation
If you want to use AI only for scoring but not email generation:

Edit `backend/services/email_queue_service.py`:
```python
success = await email_service.send_email(
    to_email=clinic_data["email"],
    clinic_name=clinic_data["clinica"],
    from_email=account["username"],
    from_password=account["password"],
    personalization=clinic_data,
    use_ai=False  # Add this parameter
)
```

## Benefits of Gemini Integration

### Before (OpenAI only)
- ❌ Dependent on single AI provider
- ❌ Higher cost per request
- ❌ Static email templates
- ❌ Basic lead filtering

### After (Gemini Primary)
- ✅ **Multi-provider fallback** (Gemini → OpenAI → Template)
- ✅ **Lower cost** (Gemini Flash is efficient)
- ✅ **Personalized emails** for each clinic
- ✅ **Smarter filtering** with Gemini's understanding
- ✅ **24/7 autonomous** with generous free tier

## Need Help?

1. **Check logs** in Railway dashboard
2. **Run test script**: `python test_gemini.py`
3. **Verify API key** is set correctly
4. **Check quotas** at [https://aistudio.google.com](https://aistudio.google.com)

## Summary

With Google Gemini integrated, your GDC LeadMachine is now:
- 🤖 **Smarter**: Better lead qualification
- 💬 **Personalized**: Unique emails for each prospect
- 💰 **Cost-effective**: Generous free tier
- 🔄 **Reliable**: Automatic fallback system
- 🚀 **Autonomous**: Works 24/7 without intervention

The system is **production-ready** and will continue working even if Gemini API is not configured (falls back to templates).
