# Comandos para Diagnosticar Azure App Service

## 1. Verificar logs de Azure App Service

### Usando Azure CLI:
```bash
# Instalar Azure CLI si no está instalado
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Ver logs de la aplicación
az webapp log tail --name advanced-ai-agent-0003 --resource-group <your-resource-group>

# Descargar logs de streaming
az webapp log download --name advanced-ai-agent-0003 --resource-group <your-resource-group>

# Ver configuración de la app
az webapp config show --name advanced-ai-agent-0003 --resource-group <your-resource-group>
```

### Usando Portal de Azure:
1. Ir a Azure Portal → App Services → advanced-ai-agent-0003
2. En el menú izquierdo: Monitoring → Log stream
3. También: Development Tools → Advanced Tools (Kudu)

## 2. Verificar estado actual del backend

### Verificar endpoints disponibles:
```bash
# Verificar root endpoint
curl -v https://advanced-ai-agent-0003.azurewebsites.net/

# Verificar health endpoint
curl -v https://advanced-ai-agent-0003.azurewebsites.net/health

# Verificar si /chat está disponible
curl -v -X POST https://advanced-ai-agent-0003.azurewebsites.net/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test","conversation_id":"test"}'

# Verificar OpenAPI schema
curl -s https://advanced-ai-agent-0003.azurewebsites.net/openapi.json | python3 -m json.tool
```

## 3. Usar Kudu para diagnosticar directamente

### Acceder a Kudu Console:
URL: `https://advanced-ai-agent-0003.scm.azurewebsites.net/`

### Comandos en Kudu Console:
```bash
# Verificar archivos deployados
ls -la /home/site/wwwroot/

# Verificar requirements.txt
cat /home/site/wwwroot/requirements.txt

# Verificar qué paquetes están instalados
pip list

# Ejecutar el script de diagnóstico
cd /home/site/wwwroot
python diagnose.py

# Verificar logs de aplicación
ls -la /home/LogFiles/
cat /home/LogFiles/2024_*/docker.log
```

## 4. Verificar variables de entorno

### En Kudu Console:
```bash
# Ver todas las variables de entorno
env | grep AZURE

# Verificar configuración específica
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_API_KEY
echo $AZURE_CHAT_DEPLOYMENT
echo $PORT
```

### En Azure Portal:
1. App Services → advanced-ai-agent-0003
2. Settings → Configuration
3. Verificar Application settings

## 5. Re-deploy con nuevos cambios

### Opción 1: GitHub Actions (Recomendado)
```bash
# Hacer commit de los cambios
git add requirements.txt startup.sh diagnose.py
git commit -m "Fix: Update requirements.txt and startup script for /chat endpoint"
git push origin main
```

### Opción 2: Deploy directo con Azure CLI
```bash
az webapp deploy --name advanced-ai-agent-0003 \
  --resource-group <your-resource-group> \
  --src-path ./ --type zip
```

## 6. Verificar después del deploy

```bash
# Esperar unos minutos y verificar
curl -v https://advanced-ai-agent-0003.azurewebsites.net/health

# Probar el endpoint /chat
curl -X POST https://advanced-ai-agent-0003.azurewebsites.net/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hola, ¿funciona el chat?","conversation_id":"test"}' \
  | python3 -m json.tool

# Verificar que el endpoint aparece en OpenAPI
curl -s https://advanced-ai-agent-0003.azurewebsites.net/openapi.json | grep -A 5 -B 5 chat
```

## 7. Solución inmediata si el problema persiste

### Crear app.py simplificado temporalmente:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Advanced AI Agent", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"

@app.get("/")
async def root():
    return {"message": "Advanced AI Agent is running!", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Advanced AI Agent", "version": "1.0.0"}

@app.post("/chat")
async def chat(request: ChatRequest):
    return {
        "response": f"Echo: {request.message}",
        "conversation_id": request.conversation_id,
        "timestamp": "2024-12-15T10:00:00Z"
    }
```

## Información del Resource Group

Para obtener el resource group:
```bash
# Listar todos los resource groups
az group list --output table

# Buscar por nombre de la app
az resource list --name advanced-ai-agent-0003 --output table
```