# 🚀 GDC LeadMachine - Railway Deployment Guide

Sistema automatizado de gestión de leads para clínicas de salud en España.

**Especialidades:** Clínicas Dentales, Fisioterapia, Oftalmología, Dermatología, Psicología, Centros Médicos, Veterinaria

## 📋 Pre-requisitos

- Cuenta de Railway
- MongoDB Atlas (o cualquier MongoDB cloud)
- Cuentas de email SMTP configuradas
- Notion API key (opcional)
- Emergent LLM Key

---

## 🚂 Deployment en Railway

`railway.json`, `Procfile` y `nixpacks.toml` ya están listos para Nixpacks. Railway hará automáticamente:

- `pip install -r backend/requirements.txt`
- `npm ci && npm run build` dentro de `frontend/`
- Arrancar FastAPI con Uvicorn sirviendo `/api` y la SPA desde `frontend/build`

### Pasos rápidos (Dashboard)
1. Ve a [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo** y selecciona este repositorio.
2. En **Variables**, añade todas las claves de `.env.example`. Asegúrate de fijar `REACT_APP_BACKEND_URL=https://<tu-app>.up.railway.app`.
3. Railway construirá con Nixpacks y usará el `Procfile` para arrancar.
4. Verifica: `/api/` debe devolver `{"status":"running"}` y `/` debe cargar el login.

### Pasos rápidos (CLI)
```bash
npm i -g @railway/cli
railway login
railway up   # usa nixpacks.toml y Procfile automáticamente
```

---

## 🔧 Variables de Entorno Requeridas

### MongoDB (OBLIGATORIO)
```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=gdc_database
```

### Frontend (OBLIGATORIO)
```bash
REACT_APP_BACKEND_URL=https://tu-app.up.railway.app
```

### Email Accounts (OBLIGATORIO)
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

### AI Configuration (OBLIGATORIO)
```bash
EMERGENT_LLM_KEY=your_emergent_llm_key
```

### Business Info (OBLIGATORIO)
```bash
BUSINESS_NAME=Gestión Digital Clínica
BUSINESS_OWNER=José Cabrejas
BUSINESS_EMAIL=contacto@gestiondigitalclinica.es
BUSINESS_WEBSITE=www.gestiondigitalclinica.es
BUSINESS_PHONE=637 971 233
BUSINESS_LOGO_URL=your_logo_url
```

### Notion (OPCIONAL)
```bash
NOTION_API_KEY=your_key
NOTION_DATABASE_ID=your_id
```

### WhatsApp (OPCIONAL)
```bash
WHATSAPP_API_KEY=your_key
WHATSAPP_PHONE_NUMBER_ID=your_id
```

---

## 📊 MongoDB Atlas Setup

1. **Crea cluster gratuito**
   - Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Crea cuenta gratuita
   - Crea cluster (M0 Free)

2. **Configura acceso**
   - Database Access → Add User
   - Network Access → Add IP (0.0.0.0/0 para Railway)

3. **Obtén connection string**
   - Connect → Drivers → Copy connection string
   - Reemplaza `<password>` con tu password
   - Usa en `MONGO_URL`

---

## 🎯 Estructura del Proyecto

```
/app
├── backend/              # FastAPI Backend
│   ├── server.py        # Main server
│   ├── requirements.txt # Python dependencies
│   ├── services/        # Business logic
│   └── scripts/         # Utility scripts
├── frontend/            # React Frontend  
│   ├── src/
│   ├── package.json
│   └── build/          # Production build
├── railway.json        # Railway config
├── Procfile           # Start command
├── nixpacks.toml      # Build config
└── .env.example       # Environment template
```

---

## 🔐 Autenticación

**Usuario:** admin  
**Contraseña:** Admin

Para cambiar credenciales, modifica:
```javascript
// frontend/src/context/AuthContext.js
if (email.toLowerCase() === 'admin' && password === 'Admin')
```

---

## 📧 Configuración de Email

### Proveedores compatibles:
- ✅ SMTP genérico (cualquier proveedor)
- ✅ Gmail (requiere App Password)
- ✅ Outlook/Office365
- ✅ Proveedores españoles (Servicio de Correo, etc.)

### Gmail Setup:
1. Activa 2FA en tu cuenta
2. Genera App Password
3. Usa App Password en `EMAIL_X_PASSWORD`

---

## 🚀 Post-Deployment

### 1. Verifica que el backend esté corriendo:
```bash
curl https://your-app.railway.app/api/
# Expected: {"message":"GDC Lead Management System API","status":"running"}
```

### 2. Importa leads reales:
- Login con admin/Admin
- Ve a "Importar" tab
- Descarga template CSV
- Sube archivo con clínicas reales

### 3. Verifica email sending:
- Ve a "Config" tab
- Check email accounts status
- Revisa cola de emails

---

## 🛠️ Troubleshooting

### Backend no inicia:
```bash
# Check logs en Railway dashboard
# Verifica variables de entorno
# Asegúrate MONGO_URL es correcto
```

### Emails no se envían:
```bash
# Verifica SMTP credentials
# Check email accounts en Config page
# Revisa logs: "Email queue processor started"
```

### MongoDB connection error:
```bash
# Verifica IP whitelist (0.0.0.0/0)
# Check MONGO_URL format
# Prueba connection string localmente
```

---

## 📝 Características

✅ **Lead Management** - Gestión completa de clínicas  
✅ **AI Scoring** - Puntuación automática con GPT-4o-mini  
✅ **Email Automation** - Envío automático con rate limiting  
✅ **WhatsApp Integration** - Mensajes manuales o API  
✅ **CSV Import** - Importación masiva de leads  
✅ **Real-time Dashboard** - Métricas en tiempo real  
✅ **Mobile Responsive** - Funciona en todos los dispositivos  

---

## ⚠️ Importante

- 🚫 **Auto-discovery DESACTIVADO** - Solo datos reales
- ✅ **Validación de emails** - Leniente para evitar falsos negativos
- 📧 **Rate limiting** - 1 email cada 120s por cuenta
- 🔐 **Credenciales** - Nunca hagas commit de .env

---

## 📞 Soporte

Si tienes problemas con el deployment:
1. Revisa logs en Railway dashboard
2. Verifica todas las variables de entorno
3. Asegúrate MongoDB esté accesible
4. Check que SMTP credentials son correctos

---

## 🎉 ¡Listo!

Tu GDC LeadMachine está ahora en producción con Railway.

**Frontend:** `https://your-app.railway.app`  
**Backend API:** `https://your-app.railway.app/api`

**Login:** admin / Admin
