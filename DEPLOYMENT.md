# 🚂 Railway Deployment - Step by Step

## Pre-requisitos

Antes de deployar, necesitas:

1. ✅ Cuenta de [Railway](https://railway.app)
2. ✅ Cuenta de [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (gratis)
3. ✅ Emergent LLM Key
4. ✅ Cuentas de email SMTP configuradas
5. ✅ Este repositorio en GitHub

## ⚡ Railway (Nixpacks) - TL;DR

- Ya está incluido `nixpacks.toml` + `Procfile` + `railway.json`. Railway instalará los requisitos de Python, compilará el frontend y lanzará `uvicorn`.
- Añade las variables de `.env.example` en la pestaña **Variables** antes de desplegar (incluye `REACT_APP_BACKEND_URL=https://<tu-app>.up.railway.app`).
- Dashboard: New Project → Deploy from GitHub → selecciona repo → Deploy.
- CLI: `npm i -g @railway/cli && railway login && railway up`.

---

## Paso 1: Configurar MongoDB Atlas (5 minutos)

### 1.1 Crear Cluster
```
1. Ve a mongodb.com/cloud/atlas
2. Sign Up / Log In
3. "Create" → "Shared" (gratis)
4. Región: Europe (Ireland) o más cercana
5. Cluster Name: gdc-cluster
6. Create Cluster
```

### 1.2 Crear Usuario
```
1. Security → Database Access
2. Add New Database User
3. Username: gdcadmin
4. Password: [guarda este password]
5. Database User Privileges: Read and write to any database
6. Add User
```

### 1.3 Permitir Acceso desde Railway
```
1. Security → Network Access
2. Add IP Address
3. Allow Access from Anywhere: 0.0.0.0/0
4. Confirm
```

### 1.4 Obtener Connection String
```
1. Database → Connect
2. Drivers → Node.js
3. Copy connection string:
   mongodb+srv://gdcadmin:<password>@cluster.mongodb.net/
4. Reemplaza <password> con tu password real
5. Guarda este string
```

---

## Paso 2: Push a GitHub

```bash
# Si no está en GitHub aún
cd /app
git init
git add .
git commit -m "GDC LeadMachine - Production Ready"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/gdc-leadmachine.git
git push -u origin main
```

---

## Paso 3: Deploy en Railway

### 3.1 Crear Proyecto
```
1. Ve a railway.app
2. Log in con GitHub
3. "New Project"
4. "Deploy from GitHub repo"
5. Selecciona tu repositorio gdc-leadmachine
6. "Deploy Now"
```

### 3.2 Railway detectará automáticamente:
- ✅ `railway.json` - Configuración
- ✅ `Procfile` - Start command  
- ✅ `requirements.txt` - Dependencies
- ✅ Backend FastAPI

### 3.3 Espera el build inicial
```
Duración: 2-3 minutos
Verás logs del build process
```

---

## Paso 4: Configurar Variables de Entorno

### 4.1 En Railway Dashboard
```
1. Click en tu proyecto
2. Variables tab
3. Add todas las siguientes variables:
```

### 4.2 Variables OBLIGATORIAS

```bash
# MongoDB
MONGO_URL=mongodb+srv://gdcadmin:TU_PASSWORD@cluster.mongodb.net/
DB_NAME=gdc_database

# Email Account 1
EMAIL_1_USERNAME=info@gestiondigitalclinica.eu
EMAIL_1_PASSWORD=tu_password_email_1

# Email Account 2  
EMAIL_2_USERNAME=info2@gestiondigitalclinica.eu
EMAIL_2_PASSWORD=tu_password_email_2

# SMTP Settings
SMTP_HOST=smtp.serviciodecorreo.es
SMTP_PORT=465
IMAP_HOST=imap.serviciodecorreo.es
IMAP_PORT=993

# AI
EMERGENT_LLM_KEY=sk-emergent-XXXXXXXXXX

# Business Info
BUSINESS_NAME=Gestión Digital Clínica
BUSINESS_OWNER=José Cabrejas
BUSINESS_EMAIL=contacto@gestiondigitalclinica.es
BUSINESS_WEBSITE=www.gestiondigitalclinica.es
BUSINESS_PHONE=637 971 233
BUSINESS_LOGO_URL=https://customer-assets.emergentagent.com/job_ecstatic-knuth-2/artifacts/u25di08h_GDC%20LOGO.jpg

# Email Settings
EMAIL_INTERVAL_SECONDS=120
MAX_LEADS=50000
```

### 4.3 Variables OPCIONALES

```bash
# Notion (si lo usas)
NOTION_API_KEY=ntn_XXXXXXXXXX
NOTION_DATABASE_ID=XXXXXXXXXX

# WhatsApp Business API (si lo usas)
WHATSAPP_API_KEY=XXXXXXXXXX
WHATSAPP_PHONE_NUMBER_ID=XXXXXXXXXX
```

### 4.4 Después de añadir variables
```
1. Click "Add" para cada variable
2. Railway auto-redeploy con nuevas variables
3. Espera 1-2 minutos
```

---

## Paso 5: Verificar Deployment

### 5.1 Check Logs
```
1. Railway Dashboard → Deployments tab
2. Click en el último deployment
3. View Logs
4. Busca: "System ready: Automated lead discovery"
```

### 5.2 Test Backend API
```
1. Railway te da una URL: https://gdc-leadmachine-production.up.railway.app
2. Abre en navegador: https://TU_URL/api/
3. Deberías ver: {"message":"GDC Lead Management System API","status":"running"}
```

### 5.3 Test Frontend
```
1. Abre: https://TU_URL/
2. Deberías ver login page
3. Login: admin / Admin
4. Deberías ver Dashboard
```

---

## Paso 6: Configurar Frontend (Importante)

### 6.1 Actualizar REACT_APP_BACKEND_URL

El frontend necesita saber dónde está el backend:

```bash
# En Railway Variables, añadir:
REACT_APP_BACKEND_URL=https://TU_URL_DE_RAILWAY

# Ejemplo:
REACT_APP_BACKEND_URL=https://gdc-leadmachine-production.up.railway.app
```

### 6.2 Rebuild Frontend
```
1. Settings → Redeploy
2. Espera 2-3 minutos
3. Frontend ahora conectará al backend correcto
```

---

## Paso 7: Post-Deployment Setup

### 7.1 Verifica Email Accounts
```
1. Login: admin / Admin
2. Ve a "Config" tab
3. Verifica que hay 2 cuentas activas
4. Si no, añade manualmente
```

### 7.2 Importa Leads Reales
```
1. Ve a "Importar" tab
2. Descarga template CSV
3. Rellena con clínicas REALES
4. Upload CSV
5. Sistema auto-score y queues emails
```

### 7.3 Monitor Email Sending
```
1. "Config" → Email Queue
2. Verás emails en "Pending"
3. Se envían 1 cada 120s por cuenta
4. Check "Outreach" para emails enviados
```

---

## 🎯 URLs Finales

```
Frontend: https://TU_URL_RAILWAY/
Backend API: https://TU_URL_RAILWAY/api/
Login: admin / Admin
```

---

## ⚠️ Troubleshooting

### "Cannot connect to MongoDB"
```
✓ Verifica MONGO_URL es correcto
✓ Check password no tiene caracteres especiales sin escapar
✓ Verifica Network Access: 0.0.0.0/0
✓ Prueba connection string con MongoDB Compass
```

### "Email sending not working"
```
✓ Verifica EMAIL_X_USERNAME y PASSWORD
✓ Check SMTP_HOST y SMTP_PORT
✓ Ve a Config → Email Accounts → Verifica status "Activa"
✓ Check logs: "Email queue processor started"
```

### "Frontend can't reach backend"
```
✓ Verifica REACT_APP_BACKEND_URL está configurado
✓ URL debe ser: https://tu-app.railway.app (sin /api)
✓ Rebuild frontend después de cambiar variable
✓ Check CORS está habilitado en backend (ya está)
```

### "Build fails"
```
✓ Check requirements.txt tiene todas las dependencies
✓ Verifica Python version (3.11)
✓ Check logs para error específico
✓ Railway auto-detecta Procfile y railway.json
```

---

## 🔒 Seguridad

### Cambiar Password de Admin
```javascript
// Edita: frontend/src/context/AuthContext.js
if (email.toLowerCase() === 'TUNUEVOUSUARIO' && password === 'TUNUEVAPASSWORD')
```

### Variables Sensibles
```
✓ NUNCA hagas commit de .env
✓ Usa Railway Variables (encriptadas)
✓ Rota passwords cada 90 días
✓ Usa passwords fuertes (16+ chars)
```

---

## 📊 Monitoring

### Railway Dashboard
```
✓ CPU/Memory usage
✓ Deployment logs  
✓ Request metrics
✓ Error tracking
```

### App Monitoring
```
✓ Dashboard → Stats en tiempo real
✓ Config → Email queue status
✓ Outreach → Tasa de envío
```

---

## 💰 Costos

### Railway Free Tier
```
✓ $5 de crédito mensual gratis
✓ Suficiente para testing
✓ Para producción: $5-20/mes
```

### MongoDB Atlas
```
✓ M0 Free tier: 512MB
✓ Suficiente para 10k+ leads
✓ Upgrade si necesitas más
```

---

## ✅ Checklist Final

Antes de usar en producción:

- [ ] MongoDB Atlas configurado y accesible
- [ ] Todas las variables de entorno añadidas
- [ ] Backend responde en /api/
- [ ] Frontend carga correctamente
- [ ] Login funciona (admin/Admin)
- [ ] Email accounts verificadas en Config
- [ ] Primer CSV de leads reales importado
- [ ] Email sending funcionando
- [ ] Dashboard mostrando stats
- [ ] WhatsApp buttons funcionan (si aplica)

---

## 🎉 ¡Deployment Completo!

Tu GDC LeadMachine está ahora en producción y listo para usar.

**Next steps:**
1. Importa más leads reales
2. Monitorea email sending
3. Ajusta rate limiting si necesario
4. Añade más cuentas de email si necesario

**URL:** https://tu-app.railway.app  
**Admin:** admin / Admin
