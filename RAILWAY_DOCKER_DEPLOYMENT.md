# 🐳 Railway Docker Deployment Guide

Complete guide for deploying GDC LeadMachine to Railway using Docker.

## 📋 Overview

This project is configured to deploy on Railway using a **multi-stage Dockerfile** for optimal performance and security.

### Architecture

```
┌─────────────────────────────────────┐
│  Stage 1: Frontend Builder          │
│  - Node.js 18 slim                  │
│  - Build React app                  │
│  - Output: /app/frontend/build      │
└─────────────────────────────────────┘
              ⬇️
┌─────────────────────────────────────┐
│  Stage 2: Production Image          │
│  - Python 3.11 slim                 │
│  - FastAPI backend                  │
│  - Copy frontend build from Stage 1 │
│  - Non-root user (appuser)          │
│  - Health check enabled             │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Deploy via Railway Dashboard

1. **Create New Project**
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `josephnicholasgestiondigitalclinica/GDCLeadMachine-v1-go`

2. **Verify Docker Detection**
   - Railway will automatically detect the `Dockerfile`
   - The `railway.json` specifies Docker as the builder

3. **Configure Environment Variables**
   - Go to your project → Variables tab
   - Add all variables from `.env.example` (see section below)
   - **Critical**: Set `REACT_APP_BACKEND_URL` to your Railway app URL

4. **Deploy**
   - Railway will automatically build and deploy
   - First build takes ~5-10 minutes
   - Subsequent builds are faster due to layer caching

### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project (or create new)
railway link

# Set environment variables (one by one or via file)
railway variables set KEY=value

# Deploy
railway up
```

## 🔧 Required Environment Variables

### MongoDB (REQUIRED)
```bash
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/
DB_NAME=gdc_database
```

### Frontend (REQUIRED)
```bash
# IMPORTANT: Must match your Railway deployment URL
REACT_APP_BACKEND_URL=https://your-app-name.up.railway.app
```

### Email Configuration (REQUIRED)
```bash
EMAIL_1_USERNAME=info@yourdomain.com
EMAIL_1_PASSWORD=your_password
EMAIL_2_USERNAME=info2@yourdomain.com
EMAIL_2_PASSWORD=your_password

SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=465
IMAP_HOST=imap.yourdomain.com
IMAP_PORT=993
```

### AI Services (RECOMMENDED)
```bash
# Google Gemini (Primary AI)
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# Emergent LLM (Fallback)
EMERGENT_LLM_KEY=your_emergent_key

# Google Places (Lead Discovery)
GOOGLE_API_KEY=your_google_places_api_key
```

### Business Information (REQUIRED)
```bash
BUSINESS_NAME=Your Business Name
BUSINESS_OWNER=Owner Name
BUSINESS_EMAIL=contact@yourbusiness.com
BUSINESS_WEBSITE=www.yourbusiness.com
BUSINESS_PHONE=+34 XXX XXX XXX
BUSINESS_LOGO_URL=https://your-logo-url.com/logo.jpg
```

### Optional Services
```bash
# Notion Integration
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id

# WhatsApp Integration
WHATSAPP_API_KEY=your_whatsapp_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

## 🐳 Docker Build Details

### Multi-Stage Build Benefits

1. **Smaller Final Image** (~200MB vs ~800MB single-stage)
   - Frontend builder stage discarded after build
   - Only production dependencies in final image

2. **Better Layer Caching**
   - Dependencies installed before code copy
   - Faster rebuilds when only code changes

3. **Security**
   - Runs as non-root user (`appuser`)
   - Minimal attack surface
   - No build tools in production image

### Dockerfile Structure

```dockerfile
# Stage 1: Build frontend
FROM node:18-slim AS frontend-builder
# ... build React app ...

# Stage 2: Production
FROM python:3.11-slim
# ... copy backend + built frontend ...
# ... create non-root user ...
# ... setup health check ...
```

### .dockerignore

The `.dockerignore` file excludes:
- Development files (`.git`, `.env`, `node_modules`)
- Documentation (except README)
- Test files
- Build artifacts (rebuilt during Docker build)
- Railway/Nixpacks configs (not needed in image)

## 🔍 Verification & Testing

### After Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-app.up.railway.app/api/
   # Expected: {"message":"GDC Lead Management System API","status":"running"}
   ```

2. **Verify Frontend**
   - Visit `https://your-app.up.railway.app`
   - Should see login page
   - Login with: `admin` / `Admin`

3. **Check Logs**
   ```bash
   railway logs
   ```
   - Should see: "Application startup complete"
   - No error messages

### Common Issues

#### Issue: Frontend not loading
```bash
# Check REACT_APP_BACKEND_URL is set correctly
railway variables
# Should match your Railway domain
```

#### Issue: MongoDB connection failed
```bash
# Verify MongoDB Atlas IP whitelist
# Should include 0.0.0.0/0 for Railway
# Check connection string format
```

#### Issue: Build timeout
```bash
# Railway free tier has build limits
# First build takes longer (~10 min)
# Subsequent builds use cache (~2-3 min)
```

## 📊 Build Performance

| Build Type | Time | Size | Cache |
|------------|------|------|-------|
| First build | ~8-10 min | ~200MB | None |
| Code change only | ~2-3 min | ~200MB | Full |
| Dependency change | ~5-6 min | ~200MB | Partial |

## 🔒 Security Features

1. **Non-root User**: Container runs as `appuser` (UID 1000)
2. **Health Check**: Automatic health monitoring at `/api/`
3. **Minimal Base**: Uses slim Python image
4. **No Secrets in Image**: All secrets via environment variables

## 🔄 Continuous Deployment

Railway automatically deploys when:
- Pushing to connected branch
- Merging pull requests
- Manual redeploy via dashboard

### Deployment Workflow

```
Push to GitHub
    ↓
Railway webhook triggered
    ↓
Docker build starts
    ↓
Multi-stage build executes
    ↓
Health check passes
    ↓
Traffic switched to new container
    ↓
Old container terminated
```

## 🛠️ Local Docker Testing

Test the Docker build locally before deploying:

```bash
# Build image
docker build -t gdcleadmachine:local .

# Run container
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e MONGO_URL=your_mongo_url \
  -e DB_NAME=gdc_database \
  -e REACT_APP_BACKEND_URL=http://localhost:8080 \
  --env-file .env \
  gdcleadmachine:local

# Test
curl http://localhost:8080/api/
```

## 📝 Railway Configuration Files

### railway.json
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

- Explicitly specifies Docker builder
- Auto-restart on failure (max 10 retries)

### .dockerignore
- Reduces build context size
- Excludes unnecessary files from image
- Improves build performance

## 🎯 Best Practices

1. **Environment Variables**
   - Never commit `.env` file
   - Use Railway's variable management
   - Update `REACT_APP_BACKEND_URL` after deployment

2. **MongoDB Atlas**
   - Use connection string with `retryWrites=true&w=majority`
   - Whitelist `0.0.0.0/0` for Railway's dynamic IPs
   - Use strong passwords

3. **Monitoring**
   - Check Railway logs regularly
   - Monitor health check status
   - Set up uptime monitoring (UptimeRobot, etc.)

4. **Updates**
   - Test locally with Docker first
   - Use feature branches for major changes
   - Monitor first deployment after changes

## 📞 Support

If deployment fails:

1. Check Railway build logs
2. Verify all environment variables are set
3. Ensure MongoDB is accessible
4. Test Docker build locally
5. Review `.dockerignore` for missing files

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ Build completes without errors
- ✅ Health check passes (`/api/` returns 200)
- ✅ Frontend loads at root URL
- ✅ Login works (admin/Admin)
- ✅ No errors in Railway logs
- ✅ MongoDB connection established

---

**Deployment Time**: ~10 minutes first time, ~2-3 minutes subsequent deploys
**Image Size**: ~200MB
**Build Type**: Multi-stage Docker
**Platform**: Railway (Docker builder)
