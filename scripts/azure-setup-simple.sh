#!/bin/bash

# Simplified Azure Resource Setup Script for Advanced AI Agent
# Creates only essential resources first

set -e

# Configuration variables
RESOURCE_GROUP="startup_id_group"
LOCATION="westus2"
SUBSCRIPTION_ID="0fbf8e45-6f68-43bb-acbc-36747f267122"
APP_NAME="advanced-ai-agent-$(date +%H%M)"  # Add timestamp to ensure uniqueness

# App Service configuration
APP_SERVICE_PLAN="ai-agent-plan-simple"
APP_SERVICE_SKU="B1"  # Basic tier with slots support

# Key Vault configuration (unique name)
KEY_VAULT_NAME="ai-vault-$(date +%s)"

echo "🚀 Setting up simplified Azure resources for Advanced AI Agent..."

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription $SUBSCRIPTION_ID

# Register required resource providers
echo "📝 Registering essential resource providers..."
az provider register --namespace Microsoft.Web --wait
az provider register --namespace Microsoft.KeyVault --wait
az provider register --namespace Microsoft.Insights --wait

echo "✅ Resource providers registered"

# Create Key Vault first
echo "🔑 Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard

echo "✅ Key Vault created: $KEY_VAULT_NAME"

# Create App Service Plan
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $APP_SERVICE_SKU \
    --is-linux

echo "✅ App Service Plan created"

# Create App Service
echo "🌐 Creating App Service..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON|3.11"

echo "✅ App Service created: $APP_NAME"

# Configure managed identity
echo "🆔 Configuring managed identity..."
PRINCIPAL_ID=$(az webapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query principalId \
    --output tsv)

echo "✅ Managed identity configured with Principal ID: $PRINCIPAL_ID"

# Grant Key Vault access to the managed identity
echo "🔐 Granting Key Vault access..."
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list

echo "✅ Key Vault access granted"

# Store basic secrets in Key Vault
echo "💾 Storing basic secrets in Key Vault..."

# JWT secret
JWT_SECRET=$(openssl rand -base64 64)
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "jwt-secret" \
    --value "$JWT_SECRET"

# App secret
APP_SECRET=$(openssl rand -base64 64)
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "app-secret" \
    --value "$APP_SECRET"

echo "✅ Basic secrets stored in Key Vault"

# Configure basic App Service settings
echo "⚙️ Configuring basic App Service settings..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        ENVIRONMENT="production" \
        DEBUG="False" \
        PYTHONPATH="/home/site/wwwroot" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        ENABLE_ORYX_BUILD="true" \
        POST_BUILD_SCRIPT_PATH="startup.sh" \
        JWT_SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/jwt-secret/)" \
        SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/app-secret/)" \
        USE_MANAGED_IDENTITY="True" \
        AZURE_OPENAI_ENDPOINT="https://nubeweb.openai.azure.com/" \
        AZURE_OPENAI_VERSION="2024-10-21" \
        AZURE_CHAT_DEPLOYMENT="gpt-4o-mini" \
        AZURE_VISION_DEPLOYMENT="gpt-4o-mini" \
        AZURE_REASONING_DEPLOYMENT="o1" \
        AZURE_EMBEDDINGS_DEPLOYMENT="text-embedding-3-small" \
        ALLOWED_HOSTS="${APP_NAME}.azurewebsites.net,*.azurewebsites.net,localhost"

echo "✅ Basic App Service settings configured"

# Enable Application Insights
echo "📊 Enabling Application Insights..."
az monitor app-insights component create \
    --app $APP_NAME \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --kind web \
    --retention-time 30 || echo "⚠️ Application Insights creation skipped"

echo "✅ Application Insights configured"

# Enable HTTPS only
echo "🔐 Enabling HTTPS only..."
az webapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --https-only true

echo "✅ HTTPS only enabled"

echo ""
echo "✅ Basic Azure resources setup completed successfully!"
echo ""
echo "📋 Resource Summary:"
echo "===================="
echo "App Service: https://${APP_NAME}.azurewebsites.net"
echo "Key Vault: https://${KEY_VAULT_NAME}.vault.azure.net"
echo "Principal ID: ${PRINCIPAL_ID}"
echo "App Service Plan: ${APP_SERVICE_PLAN}"
echo ""
echo "🔗 Important URLs:"
echo "=================="
echo "App URL: https://${APP_NAME}.azurewebsites.net"
echo "Health Check: https://${APP_NAME}.azurewebsites.net/health/live"
echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Add database resources separately if needed"
echo "2. Configure GitHub Actions with app name: $APP_NAME"
echo "3. Deploy your application"
echo ""
echo "🚀 Ready for basic deployment!"

# Save important info to file
cat > azure-deployment-info.txt << EOF
# Azure Deployment Information
APP_NAME=$APP_NAME
KEY_VAULT_NAME=$KEY_VAULT_NAME
PRINCIPAL_ID=$PRINCIPAL_ID
APP_SERVICE_PLAN=$APP_SERVICE_PLAN
RESOURCE_GROUP=$RESOURCE_GROUP
LOCATION=$LOCATION

# URLs
APP_URL=https://${APP_NAME}.azurewebsites.net
KEY_VAULT_URL=https://${KEY_VAULT_NAME}.vault.azure.net

# For GitHub Actions
AZURE_WEBAPP_NAME=$APP_NAME
EOF

echo "💾 Deployment info saved to azure-deployment-info.txt"