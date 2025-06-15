#!/bin/bash

# Script para identificar recursos Azure existentes
# Para usuarios con patrocinio Microsoft Startups

echo "🔍 IDENTIFICANDO RECURSOS AZURE"
echo "================================"
echo ""

# Verificar login en Azure
echo "1️⃣ Verificando sesión de Azure..."
if ! az account show > /dev/null 2>&1; then
    echo "❌ No estás logueado en Azure."
    echo ""
    echo "Para loguearte:"
    echo "   az login"
    echo ""
    echo "Si no tienes Azure CLI:"
    echo "   # Windows:"
    echo "   winget install Microsoft.AzureCLI"
    echo "   # macOS:"
    echo "   brew install azure-cli"
    echo "   # Linux:"
    echo "   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

echo "✅ Azure session activa"
echo ""

# Mostrar información de la cuenta
echo "2️⃣ Información de la cuenta:"
az account show --query "{name: name, id: id, tenantId: tenantId}" --output table
echo ""

# Verificar créditos Microsoft Startups
echo "3️⃣ Verificando créditos:"
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
if [[ $SUBSCRIPTION_NAME == *"Startups"* ]] || [[ $SUBSCRIPTION_NAME == *"Visual Studio"* ]] || [[ $SUBSCRIPTION_NAME == *"Microsoft"* ]]; then
    echo "✅ Detectada suscripción con créditos: $SUBSCRIPTION_NAME"
else
    echo "⚠️ Suscripción: $SUBSCRIPTION_NAME"
    echo "   Verifica que tengas acceso a los créditos Microsoft Startups"
fi
echo ""

# Listar Resource Groups
echo "4️⃣ Resource Groups disponibles:"
az group list --query "[].{Name:name, Location:location}" --output table
echo ""

# Buscar Static Web Apps
echo "5️⃣ Buscando Azure Static Web Apps..."
STATIC_APPS=$(az staticwebapp list --query "[].{Name:name, ResourceGroup:resourceGroup, DefaultHostname:defaultHostname, Sku:sku.name}" --output table)

if [ -z "$STATIC_APPS" ] || [ "$STATIC_APPS" = "Name    ResourceGroup    DefaultHostname    Sku" ]; then
    echo "❌ No se encontraron Azure Static Web Apps"
    echo ""
    echo "Si ya tienes una Static Web App, verifica:"
    echo "   1. Que tengas permisos en la suscripción correcta"
    echo "   2. Que la app esté en la suscripción actual"
    echo "   3. Ejecuta: az account set --subscription 'nombre-de-tu-suscripcion'"
else
    echo "$STATIC_APPS"
    echo ""
    
    # Verificar si alguna es la que estamos buscando
    SWA_COUNT=$(az staticwebapp list --query "length([])" --output tsv)
    if [ "$SWA_COUNT" -eq 1 ]; then
        SWA_NAME=$(az staticwebapp list --query "[0].name" --output tsv)
        SWA_RG=$(az staticwebapp list --query "[0].resourceGroup" --output tsv)
        SWA_SKU=$(az staticwebapp list --query "[0].sku.name" --output tsv)
        SWA_HOSTNAME=$(az staticwebapp list --query "[0].defaultHostname" --output tsv)
        
        echo "🎯 Static Web App detectada:"
        echo "   • Nombre: $SWA_NAME"
        echo "   • Resource Group: $SWA_RG"
        echo "   • Plan: $SWA_SKU"
        echo "   • URL: https://$SWA_HOSTNAME"
        
        if [ "$SWA_HOSTNAME" = "delightful-coast-07a54bc1e.1.azurestaticapps.net" ]; then
            echo "   ✅ Esta es tu aplicación Advanced AI Agent!"
        fi
    fi
fi
echo ""

# Buscar App Services
echo "6️⃣ Buscando Azure App Services..."
APP_SERVICES=$(az webapp list --query "[].{Name:name, ResourceGroup:resourceGroup, DefaultHostName:defaultHostName, Sku:appServicePlanId}" --output table)

if [ -z "$APP_SERVICES" ] || [ "$APP_SERVICES" = "Name    ResourceGroup    DefaultHostName    Sku" ]; then
    echo "❌ No se encontraron Azure App Services"
else
    echo "$APP_SERVICES"
    echo ""
    
    # Verificar si encontramos el backend
    BACKEND_COUNT=$(az webapp list --query "length([?contains(defaultHostName, 'advanced-ai-agent')])" --output tsv)
    if [ "$BACKEND_COUNT" -gt 0 ]; then
        BACKEND_NAME=$(az webapp list --query "[?contains(defaultHostName, 'advanced-ai-agent')].name" --output tsv)
        BACKEND_RG=$(az webapp list --query "[?contains(defaultHostName, 'advanced-ai-agent')].resourceGroup" --output tsv)
        BACKEND_HOSTNAME=$(az webapp list --query "[?contains(defaultHostName, 'advanced-ai-agent')].defaultHostName" --output tsv)
        
        echo "🎯 Backend detectado:"
        echo "   • Nombre: $BACKEND_NAME"
        echo "   • Resource Group: $BACKEND_RG"
        echo "   • URL: https://$BACKEND_HOSTNAME"
        echo "   ✅ Este es tu backend Advanced AI Agent!"
    fi
fi
echo ""

# Generar script personalizado
echo "7️⃣ Generando script personalizado..."

if [ ! -z "$SWA_NAME" ] && [ ! -z "$SWA_RG" ]; then
    cat > /mnt/c/Users/osval/advanced-ai-agent/scripts/upgrade-my-resources.sh << EOF
#!/bin/bash

# Script personalizado para tus recursos específicos
# Generado automáticamente

# TUS RECURSOS DETECTADOS:
RESOURCE_GROUP="$SWA_RG"
STATIC_WEB_APP_NAME="$SWA_NAME"
CURRENT_SKU="$SWA_SKU"
EOF

    if [ ! -z "$BACKEND_NAME" ]; then
        echo "BACKEND_APP_SERVICE=\"$BACKEND_NAME\"" >> /mnt/c/Users/osval/advanced-ai-agent/scripts/upgrade-my-resources.sh
    else
        echo "BACKEND_APP_SERVICE=\"advanced-ai-agent-0003\"  # Backend name" >> /mnt/c/Users/osval/advanced-ai-agent/scripts/upgrade-my-resources.sh
    fi

    cat >> /mnt/c/Users/osval/advanced-ai-agent/scripts/upgrade-my-resources.sh << 'EOF'

echo "🚀 UPGRADE A AZURE STATIC WEB APPS STANDARD"
echo "==========================================="
echo ""
echo "📊 Recursos a actualizar:"
echo "   • Static Web App: $STATIC_WEB_APP_NAME"
echo "   • Resource Group: $RESOURCE_GROUP"
echo "   • Plan actual: $CURRENT_SKU"
echo "   • Backend: $BACKEND_APP_SERVICE"
echo ""

if [ "$CURRENT_SKU" = "Standard" ]; then
    echo "✅ Ya estás en plan Standard!"
    echo "🔗 Verificando Linked Backend..."
    
    # Verificar si ya está vinculado
    LINKED_BACKEND=$(az staticwebapp backends list --name $STATIC_WEB_APP_NAME --resource-group $RESOURCE_GROUP --query "length([])" --output tsv)
    
    if [ "$LINKED_BACKEND" -gt 0 ]; then
        echo "✅ Linked Backend ya configurado"
        az staticwebapp backends list --name $STATIC_WEB_APP_NAME --resource-group $RESOURCE_GROUP --output table
    else
        echo "🔗 Configurando Linked Backend..."
        BACKEND_RESOURCE_ID=$(az webapp show --name $BACKEND_APP_SERVICE --resource-group $RESOURCE_GROUP --query "id" --output tsv)
        
        if [ ! -z "$BACKEND_RESOURCE_ID" ]; then
            az staticwebapp backends link \
              --name $STATIC_WEB_APP_NAME \
              --resource-group $RESOURCE_GROUP \
              --backend-resource-id $BACKEND_RESOURCE_ID
            echo "✅ Linked Backend configurado!"
        else
            echo "⚠️ No se pudo encontrar el backend. Configurar manualmente."
        fi
    fi
else
    echo "⬆️ Upgrading a Standard..."
    read -p "¿Continuar con el upgrade? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        az staticwebapp update \
          --name $STATIC_WEB_APP_NAME \
          --resource-group $RESOURCE_GROUP \
          --sku Standard
        
        echo "✅ Upgrade completado!"
        echo "🔗 Configurando Linked Backend..."
        
        BACKEND_RESOURCE_ID=$(az webapp show --name $BACKEND_APP_SERVICE --resource-group $RESOURCE_GROUP --query "id" --output tsv)
        
        if [ ! -z "$BACKEND_RESOURCE_ID" ]; then
            sleep 30  # Esperar a que el upgrade se propague
            az staticwebapp backends link \
              --name $STATIC_WEB_APP_NAME \
              --resource-group $RESOURCE_GROUP \
              --backend-resource-id $BACKEND_RESOURCE_ID
            echo "✅ Linked Backend configurado!"
        fi
    fi
fi

echo ""
echo "🎉 PROCESO COMPLETADO!"
echo ""
echo "🔗 Enlaces útiles:"
echo "   • Azure Portal: https://portal.azure.com"
echo "   • Tu aplicación: https://delightful-coast-07a54bc1e.1.azurestaticapps.net"
echo "   • Backend: https://advanced-ai-agent-0003.azurewebsites.net"
echo ""
echo "⏰ Los cambios pueden tardar 5-10 minutos en propagarse"
EOF

    chmod +x /mnt/c/Users/osval/advanced-ai-agent/scripts/upgrade-my-resources.sh
    
    echo "✅ Script personalizado creado: ./scripts/upgrade-my-resources.sh"
    echo ""
    echo "🚀 PARA EJECUTAR EL UPGRADE:"
    echo "   cd /mnt/c/Users/osval/advanced-ai-agent"
    echo "   ./scripts/upgrade-my-resources.sh"
    echo ""
else
    echo "⚠️ No se pudieron detectar todos los recursos automáticamente"
    echo ""
    echo "📝 Para upgrade manual:"
    echo "   1. Ve a https://portal.azure.com"
    echo "   2. Busca 'Static Web Apps'"
    echo "   3. Selecciona tu aplicación"
    echo "   4. Ve a Configuration > Hosting plan"
    echo "   5. Cambia a 'Standard'"
    echo "   6. Ve a APIs > Link > Selecciona tu App Service"
fi

echo ""
echo "💰 RECORDATORIO DE COSTOS:"
echo "   • Standard Plan: ~$9-15 USD/mes"
echo "   • Con créditos Microsoft Startups: ¡Gratis durante años!"
echo "   • Monitor en: Azure Portal > Cost Management"
echo ""
echo "✅ Identificación completada!"