#!/bin/bash

# Script para configurar monitoreo y alertas
# Optimizar uso de créditos Microsoft Startups

echo "📊 Configurando monitoreo y optimización de costos"
echo ""

# Variables
RESOURCE_GROUP="your-resource-group"
STATIC_WEB_APP_NAME="your-swa-name"
BACKEND_APP_SERVICE="advanced-ai-agent-0003"
NOTIFICATION_EMAIL="your-email@domain.com"

# Crear Action Group para alertas
echo "🔔 Creando grupo de notificaciones..."
az monitor action-group create \
  --resource-group $RESOURCE_GROUP \
  --name "startup-alerts" \
  --short-name "startup" \
  --action email "$NOTIFICATION_EMAIL" "admin"

# Configurar alerta de presupuesto
echo "💰 Configurando alerta de presupuesto..."
az consumption budget create \
  --resource-group $RESOURCE_GROUP \
  --budget-name "monthly-budget" \
  --amount 100 \
  --category Cost \
  --time-grain Monthly \
  --start-date $(date +%Y-%m-01) \
  --end-date 2024-12-31

# Configurar alertas de disponibilidad
echo "📈 Configurando alertas de disponibilidad..."
az monitor metrics alert create \
  --name "swa-availability-alert" \
  --resource-group $RESOURCE_GROUP \
  --target-resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$STATIC_WEB_APP_NAME" \
  --condition "avg Availability < 99" \
  --description "Static Web App availability below 99%" \
  --evaluation-frequency 5m \
  --window-size 15m \
  --action "startup-alerts"

# Configurar Application Insights (si no existe)
echo "📊 Configurando Application Insights..."
az monitor app-insights component create \
  --app "$STATIC_WEB_APP_NAME-insights" \
  --location "East US" \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Obtener instrumentación key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app "$STATIC_WEB_APP_NAME-insights" \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

echo ""
echo "✅ Monitoreo configurado!"
echo ""
echo "📊 Application Insights Key: $INSTRUMENTATION_KEY"
echo "💡 Agrega esta key a tu frontend para telemetría avanzada"
echo ""
echo "🔗 Enlaces de monitoreo:"
echo "   • Costs: https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/overview"
echo "   • Metrics: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/staticSites/$STATIC_WEB_APP_NAME/metrics"
echo "   • Application Insights: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/components/$STATIC_WEB_APP_NAME-insights/overview"