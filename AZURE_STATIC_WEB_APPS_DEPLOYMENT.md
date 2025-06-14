# 🌐 Despliegue Frontend - Azure Static Web Apps

Guía completa para desplegar el frontend del **Advanced AI Agent** en Azure Static Web Apps.

## 📋 **Prerrequisitos**

- ✅ Cuenta de Azure con Microsoft for Startups
- ✅ Repositorio GitHub configurado
- ✅ Backend funcionando en Azure App Services
- ✅ Azure CLI instalado

## 🚀 **Pasos de Despliegue**

### **1. Crear Azure Static Web App**

#### **Opción A: Azure Portal (Recomendado)**

1. **Ir al Azure Portal**: https://portal.azure.com
2. **Crear recurso** → **Static Web App**
3. **Configuración**:
   ```
   Subscription: Microsoft for Startups
   Resource Group: startup_id_group
   Name: advanced-ai-agent-frontend
   Plan: Free
   Region: West US 2
   ```

4. **Source**:
   ```
   Source: GitHub
   Organization: OsvaldoVegaOses
   Repository: advanced-ai-agent
   Branch: main
   ```

5. **Build Details**:
   ```
   Build Presets: Next.js
   App location: /frontend
   Api location: (empty)
   Output location: out
   ```

#### **Opción B: Azure CLI**

```bash
# Crear Static Web App
az staticwebapp create \
  --name "advanced-ai-agent-frontend" \
  --resource-group "startup_id_group" \
  --source "https://github.com/OsvaldoVegaOses/advanced-ai-agent" \
  --location "West US 2" \
  --branch "main" \
  --app-location "frontend" \
  --output-location "out"
```

### **2. Configurar Variables de Entorno**

En el Azure Portal, ir a **Configuration** y agregar:

```env
NEXT_PUBLIC_API_URL=https://advanced-ai-agent-0003.azurewebsites.net
NEXT_PUBLIC_APP_NAME=Advanced AI Agent
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=production
```

### **3. Configurar GitHub Secrets**

Después de crear la Static Web App, Azure generará un token. Agregarlo a GitHub:

1. **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**:
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: [Token generado por Azure]

### **4. Verificar Despliegue**

1. **Push cambios** al repositorio GitHub
2. **GitHub Actions** se ejecutará automáticamente
3. **Verificar build** en la pestaña Actions
4. **Probar aplicación** en la URL proporcionada

## 📁 **Estructura de Archivos**

```
advanced-ai-agent/
├── .github/workflows/
│   └── azure-static-web-apps.yml    # CI/CD workflow
├── frontend/
│   ├── src/                         # Código fuente
│   ├── package.json                 # Dependencias
│   ├── next.config.js              # Configuración Next.js
│   ├── staticwebapp.config.json    # Configuración Azure SWA
│   └── .env.production             # Variables de producción
```

## ⚙️ **Configuración Avanzada**

### **Routing y Fallbacks**

`staticwebapp.config.json`:
```json
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/api/*", "/_next/*"]
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html",
      "statusCode": 200
    }
  }
}
```

### **Headers de Seguridad**

```json
{
  "globalHeaders": {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block"
  }
}
```

### **Performance**

`next.config.js`:
```javascript
{
  output: 'export',
  images: { unoptimized: true },
  compiler: { removeConsole: true }
}
```

## 🔧 **Comandos Útiles**

```bash
# Desarrollo local
cd frontend
npm run dev

# Build para Azure
npm run build:azure

# Verificar tipos
npm run type-check

# Linting
npm run lint

# Analizar bundle
npm run analyze
```

## 🌍 **URLs del Proyecto**

Una vez desplegado, tendrás:

- **Frontend**: https://[app-name].azurestaticapps.net
- **Backend**: https://advanced-ai-agent-0003.azurewebsites.net
- **GitHub**: https://github.com/OsvaldoVegaOses/advanced-ai-agent

## 🐛 **Troubleshooting**

### **Error: Build Failed**

```bash
# Verificar localmente
npm run build:azure

# Revisar logs en GitHub Actions
# Verificar variables de entorno
```

### **Error: API Connection**

```bash
# Verificar NEXT_PUBLIC_API_URL
# Probar backend directamente
curl https://advanced-ai-agent-0003.azurewebsites.net/health
```

### **Error: 404 en Rutas**

Verificar `staticwebapp.config.json`:
```json
{
  "navigationFallback": {
    "rewrite": "/index.html"
  }
}
```

## 📊 **Monitoreo**

### **Azure Application Insights**

1. **Habilitar** Application Insights en Static Web App
2. **Configurar** métricas personalizadas
3. **Crear** dashboards de monitoreo

### **GitHub Actions**

- **Build status**: Badge en README
- **Deployment history**: Actions tab
- **Performance metrics**: Build time tracking

## 🔒 **Seguridad**

- ✅ **HTTPS** por defecto
- ✅ **Headers de seguridad** configurados
- ✅ **Variables de entorno** seguras
- ✅ **GitHub secrets** protegidos

## 📈 **Optimizaciones**

### **Performance**

- ✅ **Static export** para máxima velocidad
- ✅ **Image optimization** deshabilitada para SWA
- ✅ **Bundle analysis** disponible
- ✅ **Code splitting** automático

### **SEO**

- ✅ **Meta tags** configurados
- ✅ **Sitemap** generado
- ✅ **OpenGraph** tags

## 🚀 **Escalabilidad**

- **Global CDN** incluido
- **Auto-scaling** automático
- **99.95% SLA** garantizado
- **Unlimited bandwidth** en plan gratuito

---

## 🎯 **Resultado Final**

¡Tu **Advanced AI Agent** estará disponible mundialmente con:

- 🌐 **Frontend**: Interfaz moderna en Azure Static Web Apps
- 🚀 **Backend**: API robusta en Azure App Services  
- 🔄 **CI/CD**: Despliegue automático con GitHub Actions
- 💰 **Gratis**: Aprovechando Microsoft for Startups

**¡Aplicación completa funcionando en la nube!** ✨