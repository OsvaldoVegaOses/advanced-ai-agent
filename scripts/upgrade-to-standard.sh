#!/bin/bash

# Script para upgrade Azure Static Web Apps a Standard
# Aprovechando créditos Microsoft Startups

echo "🚀 Upgrading Azure Static Web Apps to Standard Plan"
echo "📊 Using Microsoft Startups credits"
echo ""

# Variables - REEMPLAZAR CON TUS VALORES
RESOURCE_GROUP="your-resource-group"  # Encontrar en Azure Portal
STATIC_WEB_APP_NAME="your-swa-name"   # Nombre de tu Static Web App
BACKEND_APP_SERVICE="advanced-ai-agent-0003"  # Tu Azure App Service

# Verificar login en Azure
echo "🔍 Verificando sesión de Azure..."
if ! az account show > /dev/null 2>&1; then
    echo "❌ No estás logueado en Azure. Ejecuta: az login"
    exit 1
fi

echo "✅ Azure session activa"

# Mostrar información actual
echo ""
echo "📋 Información actual:"
az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{name: name, sku: sku.name, location: location}" \
  --output table

# Confirmar upgrade
echo ""
read -p "¿Continuar con el upgrade a Standard? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "❌ Upgrade cancelado"
    exit 0
fi

# Upgrade a Standard
echo ""
echo "⬆️ Upgrading to Standard plan..."
az staticwebapp update \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku Standard

if [ $? -eq 0 ]; then
    echo "✅ Upgrade to Standard completed!"
else
    echo "❌ Upgrade failed. Check Azure portal for details."
    exit 1
fi

# Verificar el upgrade
echo ""
echo "🔍 Verificando upgrade..."
az staticwebapp show \
  --name $STATIC_WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{name: name, sku: sku.name, location: location}" \
  --output table

# Configurar Linked Backend (opcional)
echo ""
read -p "¿Configurar Linked Backend automáticamente? (y/N): " configure_backend
if [[ $configure_backend == [yY] ]]; then
    echo "🔗 Configurando Linked Backend..."
    
    # Obtener resource ID del App Service
    BACKEND_RESOURCE_ID=$(az webapp show \
      --name $BACKEND_APP_SERVICE \
      --resource-group $RESOURCE_GROUP \
      --query "id" \
      --output tsv)
    
    if [ -n "$BACKEND_RESOURCE_ID" ]; then
        # Vincular backend
        az staticwebapp backends link \
          --name $STATIC_WEB_APP_NAME \
          --resource-group $RESOURCE_GROUP \
          --backend-resource-id $BACKEND_RESOURCE_ID
        
        echo "✅ Linked Backend configurado!"
    else
        echo "⚠️ No se pudo encontrar el App Service. Configurar manualmente en el portal."
    fi
fi

# Información final
echo ""
echo "🎉 UPGRADE COMPLETADO!"
echo ""
echo "📊 Resumen:"
echo "   • Plan: Standard (with SLA 99.95%)"
echo "   • Costo estimado: ~$9-15 USD/mes"
echo "   • Linked Backend: Disponible"
echo ""
echo "🔗 Enlaces útiles:"
echo "   • Azure Portal: https://portal.azure.com"
echo "   • Static Web App: https://$STATIC_WEB_APP_NAME.azurestaticapps.net"
echo "   • Monitoring: Azure Portal > Static Web Apps > $STATIC_WEB_APP_NAME > Monitoring"
echo ""
echo "⏰ Los cambios pueden tardar 5-10 minutos en propagarse"

# Monitorear costos
echo ""
echo "💰 Para monitorear costos:"
echo "   1. Ve a Azure Portal > Cost Management + Billing"
echo "   2. Revisa 'Cost Analysis' para ver el uso de créditos"
echo "   3. Configura alertas de presupuesto si es necesario"

echo ""
echo "✅ Script completado. ¡Tu aplicación ahora tiene capacidades empresariales!"