# 🚀 Azure App Service Deployment Guide

## Implementación de Advanced AI Agent en Azure

Esta guía te ayudará a implementar tu aplicación Advanced AI Agent en Azure App Service aprovechando tu patrocinio de Microsoft for Startups.

## 📋 Prerrequisitos

- ✅ Suscripción de Azure activa (Patrocinio Microsoft for Startups)
- ✅ Azure CLI instalado
- ✅ Cuenta de GitHub con el repositorio
- ✅ Recurso de Azure OpenAI configurado

## 🏗️ Arquitectura de Implementación

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │   Azure App      │    │   Azure OpenAI  │
│   Repository    │────│   Service        │────│   (nubeweb)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ├── Azure Database for PostgreSQL
                              ├── Azure Cache for Redis
                              ├── Azure Key Vault
                              └── Application Insights
```

## 🚀 Paso 1: Configuración Inicial de Azure

### 1.1 Ejecutar el script de configuración

```bash
cd advanced-ai-agent
chmod +x scripts/azure-setup.sh
./scripts/azure-setup.sh
```

Este script creará:
- ✅ App Service y Plan de servicio
- ✅ Base de datos PostgreSQL
- ✅ Cache Redis
- ✅ Key Vault para secretos
- ✅ Application Insights
- ✅ Managed Identity

### 1.2 Verificar recursos creados

```bash
az resource list --resource-group startup_id_group --output table
```

## 🔐 Paso 2: Configuración de Secretos de GitHub

Agrega los siguientes secretos en tu repositorio de GitHub:

### 2.1 Ir a GitHub Secrets
1. Ve a tu repositorio: `https://github.com/OsvaldoVegaOses/advanced-ai-agent`
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**

### 2.2 Agregar secretos necesarios

```bash
# Azure Credentials (para autenticación)
AZURE_CREDENTIALS = {
  "clientId": "tu-client-id",
  "clientSecret": "tu-client-secret",
  "subscriptionId": "0fbf8e45-6f68-43bb-acbc-36747f267122",
  "tenantId": "tu-tenant-id"
}

# Docker Hub (ya configurado previamente)
DOCKER_ACCESS_TOKEN = "your-docker-access-token"

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = "https://nubeweb.openai.azure.com/"
AZURE_OPENAI_VERSION = "2024-10-21"
```

### 2.3 Obtener Azure Credentials

```bash
# Crear Service Principal para GitHub Actions
az ad sp create-for-rbac \
  --name "github-actions-ai-agent" \
  --role contributor \
  --scopes /subscriptions/0fbf8e45-6f68-43bb-acbc-36747f267122/resourceGroups/startup_id_group \
  --sdk-auth
```

## 🔧 Paso 3: Configuración de Variables de Entorno en Azure

### 3.1 Configurar App Settings en Azure Portal

Ve a Azure Portal → App Services → advanced-ai-agent → Configuration:

```bash
# Configuración de aplicación
ENVIRONMENT = "production"
DEBUG = "False"
PYTHONPATH = "/home/site/wwwroot"

# Base de datos
DATABASE_URL = "@Microsoft.KeyVault(SecretUri=https://ai-agent-vault.vault.azure.net/secrets/database-url/)"

# Redis
REDIS_URL = "redis://ai-agent-cache.redis.cache.windows.net:6380,password=PASSWORD,ssl=True"

# Azure OpenAI
USE_MANAGED_IDENTITY = "True"
AZURE_OPENAI_ENDPOINT = "https://nubeweb.openai.azure.com/"
AZURE_OPENAI_VERSION = "2024-10-21"

# Modelos
AZURE_CHAT_DEPLOYMENT = "gpt-4o-mini"
AZURE_VISION_DEPLOYMENT = "gpt-4o-mini"
AZURE_REASONING_DEPLOYMENT = "o1"
AZURE_EMBEDDINGS_DEPLOYMENT = "text-embedding-3-small"

# Hosts permitidos
ALLOWED_HOSTS = "advanced-ai-agent.azurewebsites.net,*.azurewebsites.net"
```

### 3.2 Configurar Managed Identity para Azure OpenAI

```bash
# Obtener el Principal ID del App Service
PRINCIPAL_ID=$(az webapp identity show \
  --name advanced-ai-agent \
  --resource-group startup_id_group \
  --query principalId \
  --output tsv)

# Dar acceso al recurso de Azure OpenAI
az cognitiveservices account create \
  --name nubeweb \
  --resource-group startup_id_group \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --assign-identity $PRINCIPAL_ID
```

## 📦 Paso 4: Implementación

### 4.1 Configurar GitHub Workflow

Copia el archivo de workflow:

```bash
mkdir -p .github/workflows
cp azure-ci-cd-workflow.yml .github/workflows/
```

### 4.2 Hacer commit y push

```bash
git add .
git commit -m "Add Azure App Service deployment configuration"
git push origin main
```

### 4.3 Monitorear el deployment

1. Ve a GitHub → Actions tab
2. Observa el progreso del workflow
3. El deployment incluye:
   - ✅ Tests automatizados
   - ✅ Build del paquete
   - ✅ Deploy a staging
   - ✅ Deploy a producción
   - ✅ Health checks

## 🔍 Paso 5: Verificación y Testing

### 5.1 Verificar que la aplicación esté funcionando

```bash
# Health check
curl https://advanced-ai-agent.azurewebsites.net/health/live

# Endpoint principal
curl https://advanced-ai-agent.azurewebsites.net/

# Documentación API (si DEBUG=True)
# https://advanced-ai-agent.azurewebsites.net/docs
```

### 5.2 Verificar logs

```bash
# Ver logs en tiempo real
az webapp log tail \
  --name advanced-ai-agent \
  --resource-group startup_id_group

# Descargar logs
az webapp log download \
  --name advanced-ai-agent \
  --resource-group startup_id_group
```

## 📊 Paso 6: Monitoreo y Optimización

### 6.1 Application Insights

- Dashboard: Azure Portal → Application Insights → advanced-ai-agent
- Métricas automáticas de performance
- Alertas configurables
- Tracking de errores

### 6.2 Escalamiento automático

```bash
# Configurar auto-scaling
az monitor autoscale create \
  --resource-group startup_id_group \
  --resource advanced-ai-agent \
  --resource-type Microsoft.Web/sites \
  --name ai-agent-autoscale \
  --min-count 1 \
  --max-count 3 \
  --count 1

# Regla de escalamiento por CPU
az monitor autoscale rule create \
  --resource-group startup_id_group \
  --autoscale-name ai-agent-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

## 🛠️ Comandos Útiles

### Deployment slots

```bash
# Swap staging to production
az webapp deployment slot swap \
  --name advanced-ai-agent \
  --resource-group startup_id_group \
  --slot staging \
  --target-slot production

# Rollback
az webapp deployment slot swap \
  --name advanced-ai-agent \
  --resource-group startup_id_group \
  --slot production \
  --target-slot staging
```

### Base de datos

```bash
# Conectar a la base de datos
psql "host=ai-agent-db.postgres.database.azure.com port=5432 dbname=ai_agent_db user=aiagent sslmode=require"

# Ejecutar migraciones
az webapp ssh \
  --name advanced-ai-agent \
  --resource-group startup_id_group
```

## 🚨 Troubleshooting

### Problemas comunes

1. **Error de dependencias Python**
   ```bash
   # Verificar requirements-azure.txt
   # Asegurar que spaCy models están disponibles
   ```

2. **Error de conexión a base de datos**
   ```bash
   # Verificar firewall rules
   # Verificar connection string en Key Vault
   ```

3. **Error de Azure OpenAI**
   ```bash
   # Verificar Managed Identity permissions
   # Verificar deployment names
   ```

### Logs y debugging

```bash
# Application logs
az webapp log tail --name advanced-ai-agent --resource-group startup_id_group

# Deployment logs
az webapp deployment log --name advanced-ai-agent --resource-group startup_id_group

# SSH access
az webapp ssh --name advanced-ai-agent --resource-group startup_id_group
```

## 💰 Optimización de Costos

Con el patrocinio de Microsoft for Startups:

- **App Service B2**: ~$35/mes
- **PostgreSQL Basic**: ~$25/mes  
- **Redis Basic**: ~$15/mes
- **Azure OpenAI**: Pay-per-use (incluido en créditos)

**Total estimado**: ~$75/mes (cubierto por créditos del patrocinio)

## 🎯 URLs de la Aplicación

- **Producción**: https://advanced-ai-agent.azurewebsites.net
- **Staging**: https://advanced-ai-agent-staging.azurewebsites.net
- **Logs**: Azure Portal → App Services → advanced-ai-agent → Log stream

## 📞 Soporte

Para problemas de implementación:
1. Revisar logs de GitHub Actions
2. Revisar logs de Azure App Service
3. Verificar configuración de variables de entorno
4. Revisar documentación de Azure OpenAI

¡Tu aplicación Advanced AI Agent está lista para revolucionar la experiencia del cliente en Azure! 🚀