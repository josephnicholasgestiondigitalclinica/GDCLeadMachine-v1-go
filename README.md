# GDC LeadMachine - Gestión Digital Clínica

Sistema automatizado de gestión de leads para clínicas veterinarias en España.

## 🚀 Características

### Lead Discovery Automatizado
- Búsqueda automática de clínicas veterinarias por regiones
- Extracción de datos de Google Maps
- Scoring inteligente con AI (GPT-4o-mini)
- Filtrado automático de grandes corporaciones

### Email Outreach Automatizado
- Sistema de cola de emails con múltiples cuentas
- Rate limiting (1 email cada 120 segundos por cuenta)
- Plantilla personalizada de email HTML
- Seguimiento de estado de envío
- Reintento automático en caso de fallo

### Scoring Inteligente AI
- Validación de emails (formato básico, sin deliverability check estricto)
- Análisis de sitio web
- Bonus para emails genéricos (info@, contacto@, etc.)
- Bonus para emails personales (gmail, hotmail, etc.)
- Puntuación de 1-10 automática

### Dashboard Completo
- Métricas en tiempo real
- Lista de leads recientes
- Filtrado por región (Comunidad Autónoma)
- Gestión de cuentas de email
- Cola de emails pendientes

## 📋 Requisitos

- Python 3.11+
- Node.js 18+
- MongoDB
- Yarn

## 🔧 Configuración

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017/
DB_NAME=gdc_database

# Notion
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id

# Email Accounts
EMAIL_1_USERNAME=info@yourdomain.com
EMAIL_1_PASSWORD=your_password
EMAIL_2_USERNAME=info2@yourdomain.com
EMAIL_2_PASSWORD=your_password

# SMTP/IMAP Settings
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=465
IMAP_HOST=imap.yourdomain.com
IMAP_PORT=993

# AI Settings
EMERGENT_LLM_KEY=your_emergent_llm_key

# Business Info
BUSINESS_NAME=Gestión Digital Clínica
BUSINESS_OWNER=Your Name
BUSINESS_EMAIL=contact@yourdomain.com
BUSINESS_WEBSITE=www.yourdomain.com
BUSINESS_PHONE=+34 XXX XXX XXX
BUSINESS_LOGO_URL=your_logo_url

# Email Settings
EMAIL_INTERVAL_SECONDS=120
MAX_LEADS=50000
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🏃 Ejecución

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

## 🔐 Autenticación

**Usuario:** admin  
**Contraseña:** Admin

## 📊 Endpoints API

### Clinics
- `GET /api/clinics` - Lista de clínicas con proyecciones optimizadas
- `POST /api/clinics` - Crear clínica (trigger scoring y queue)
- `POST /api/clinics/bulk` - Importación masiva
- `POST /api/clinics/{id}/score` - Scoring manual

### Email
- `GET /api/email/stats` - Estadísticas de emails
- `GET /api/email/queue` - Cola de emails
- `POST /api/email-accounts` - Añadir cuenta de email
- `GET /api/email-accounts` - Lista de cuentas

### Discovery
- `POST /api/discovery/trigger` - Trigger manual de discovery
- `GET /api/discovery/status` - Estado del scheduler

### Dashboard
- `GET /api/stats/dashboard` - Estadísticas completas

## 🎨 Diseño

- Tema blanco moderno y limpio
- Completamente responsive (mobile-first)
- Tailwind CSS + shadcn/ui components
- Logo optimizado para fondos blancos

## 🔒 Seguridad

- ✅ Sin secretos hardcodeados
- ✅ Todas las credenciales desde variables de entorno
- ✅ Validación de emails mejorada (menos falsos positivos)
- ✅ Queries optimizadas con proyecciones
- ✅ Indexes en MongoDB para performance

## 📝 Notas

- El sistema ejecuta discovery automático cada 2 horas
- Emails se envían automáticamente 1 por cada 120 segundos por cuenta
- Score >= 7 = Alto valor
- Score >= 5 = Contactar
- Score < 5 = Rechazar

## 🚀 Deployment

El sistema está listo para deployment en Kubernetes. Todos los blockers han sido resueltos:
- Sin hardcoded secrets
- Queries optimizadas
- Indexes creados
- Environment variables configuradas correctamente
