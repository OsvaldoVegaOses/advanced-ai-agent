# 🔐 Configuración de GitHub Secret para Azure Static Web Apps

## 🔧 **Error Solucionado**
✅ **Fixed**: Actualizado workflow para usar `actions/upload-artifact@v4` y `Azure/static-web-apps-deploy@latest`

## ⚡ **Instrucciones Urgentes**

Para completar el despliegue del frontend, necesitas agregar el siguiente secret a GitHub:

### **1. Ir a GitHub Repository**
- URL: https://github.com/OsvaldoVegaOses/advanced-ai-agent
- Settings → Secrets and variables → Actions

### **2. Crear New Repository Secret**
- **Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- **Value**: `134c3a972d98693736f6cef3bf959383484461d46a7e54ea5c5bfa1c1cca6e0701-eabb2bbc-2c98-4fbe-addb-217eed4140b401e180507a54bc1e`

### **3. Save Secret**
- Click "Add secret"

### **4. Trigger Deployment**
Tienes 2 opciones de workflow:

**Opción A - Automático:**
```bash
git commit --allow-empty -m "Trigger Azure Static Web App deployment"
git push origin main
```

**Opción B - Manual (Recomendado):**
1. Ve a: https://github.com/OsvaldoVegaOses/advanced-ai-agent/actions
2. Click en "Azure Static Web Apps CI/CD (Alternative)"
3. Click "Run workflow" → "Run workflow"

## 📱 **URLs de la Aplicación**

Una vez desplegado:

- **Frontend**: https://delightful-coast-07a54bc1e.1.azurestaticapps.net
- **Backend**: https://advanced-ai-agent-0003.azurewebsites.net

## ✅ **Verificar Despliegue**

1. **GitHub Actions**: Verificar que el workflow se ejecute sin errores
2. **Azure Portal**: Verificar el estado del deployment
3. **Frontend URL**: Probar la aplicación en el navegador

## 🐛 **Si hay errores:**

- Usa el workflow alternativo: `azure-static-web-apps-v2.yml` 
- Manual workflow dispatch disponible
- Soporte para Node.js 20 y actions actualizadas

---

**¡Tu Advanced AI Agent estará disponible globalmente en unos minutos!** 🌍✨