# 🚀 DEPLOYMENT CHECKLIST

## Pre-Deploy

- [ ] MongoDB Atlas cluster creado
- [ ] Usuario MongoDB creado
- [ ] Network Access: 0.0.0.0/0 configurado  
- [ ] Connection string copiado
- [ ] Repositorio en GitHub
- [ ] Emergent LLM Key disponible
- [ ] Email SMTP credentials disponibles

## Railway Setup

- [ ] Proyecto creado en Railway
- [ ] Repositorio conectado
- [ ] Variables de entorno añadidas:
  - [ ] MONGO_URL
  - [ ] DB_NAME
  - [ ] EMAIL_1_USERNAME
  - [ ] EMAIL_1_PASSWORD
  - [ ] EMAIL_2_USERNAME
  - [ ] EMAIL_2_PASSWORD
  - [ ] SMTP_HOST
  - [ ] SMTP_PORT
  - [ ] IMAP_HOST
  - [ ] IMAP_PORT
  - [ ] EMERGENT_LLM_KEY
  - [ ] BUSINESS_NAME
  - [ ] BUSINESS_OWNER
  - [ ] BUSINESS_EMAIL
  - [ ] BUSINESS_WEBSITE
  - [ ] BUSINESS_PHONE
  - [ ] BUSINESS_LOGO_URL
  - [ ] REACT_APP_BACKEND_URL (tu URL de Railway)

## Post-Deploy Verification

- [ ] Backend API responde: https://tu-url/api/
- [ ] Frontend carga: https://tu-url/
- [ ] Login funciona: admin / Admin
- [ ] Dashboard muestra 0 leads inicialmente
- [ ] Config muestra email accounts
- [ ] No hay errores en Railway logs

## Data Import

- [ ] CSV template descargado
- [ ] Archivo CSV con leads REALES creado
- [ ] CSV importado exitosamente
- [ ] Leads aparecen en Dashboard
- [ ] Leads con score ≥7 en email queue
- [ ] Emails comienzan a enviarse

## Final Checks

- [ ] Email sending funcionando
- [ ] Outreach muestra emails enviados
- [ ] WhatsApp buttons funcionan
- [ ] Mobile responsive verificado
- [ ] Todas las páginas cargan correctamente

---

## URLs

**Frontend:** https://_________________.railway.app  
**Backend:** https://_________________.railway.app/api  
**Login:** admin / Admin

## Notas

- 🚫 Auto-discovery está DESACTIVADO
- ✅ Solo importa leads REALES via CSV
- 📧 Rate limit: 1 email cada 120s por cuenta
- 🔐 Cambia password de admin después de deploy

## Soporte

Ver DEPLOYMENT.md para troubleshooting completo.
