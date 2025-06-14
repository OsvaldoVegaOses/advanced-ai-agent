#!/bin/bash

# Azure Resource Setup Script for Advanced AI Agent
# This script creates all necessary Azure resources for the application

set -e

# Configuration variables
RESOURCE_GROUP="startup_id_group"
LOCATION="eastus"
SUBSCRIPTION_ID="0fbf8e45-6f68-43bb-acbc-36747f267122"
APP_NAME="advanced-ai-agent"

# Database configuration
DB_SERVER_NAME="ai-agent-db"
DB_NAME="ai_agent_db"
DB_ADMIN_USER="aiagent"
DB_SKU="B_Gen5_1"  # Basic tier for cost optimization

# Redis configuration
REDIS_NAME="ai-agent-cache"
REDIS_SKU="Basic"
REDIS_VM_SIZE="C0"

# App Service configuration
APP_SERVICE_PLAN="ai-agent-plan"
APP_SERVICE_SKU="B2"  # Basic tier

# Key Vault configuration
KEY_VAULT_NAME="ai-agent-vault"

echo "🚀 Setting up Azure resources for Advanced AI Agent..."

# Login to Azure (if not already logged in)
echo "🔐 Logging in to Azure..."
az login --tenant osvaldovegahotmail.onmicrosoft.com || echo "Already logged in"

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription $SUBSCRIPTION_ID

# Verify resource group exists
echo "📁 Verifying resource group..."
az group show --name $RESOURCE_GROUP --output table || {
    echo "❌ Resource group $RESOURCE_GROUP not found"
    echo "Creating resource group..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
}

echo "✅ Resource group verified"

# Create PostgreSQL Database
echo "🗃️ Creating PostgreSQL database..."
az postgres server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user $DB_ADMIN_USER \
    --admin-password "$(openssl rand -base64 32)" \
    --sku-name $DB_SKU \
    --version 13 \
    --ssl-enforcement Enabled \
    --storage-size 51200 || echo "Database server might already exist"

# Configure database firewall
echo "🔥 Configuring database firewall..."
az postgres server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $DB_SERVER_NAME \
    --name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 || echo "Firewall rule might already exist"

# Create database
echo "📊 Creating application database..."
az postgres db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --name $DB_NAME || echo "Database might already exist"

# Create Redis Cache
echo "🔄 Creating Redis cache..."
az redis create \
    --name $REDIS_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $REDIS_SKU \
    --vm-size $REDIS_VM_SIZE \
    --enable-non-ssl-port || echo "Redis cache might already exist"

# Create Key Vault
echo "🔑 Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard || echo "Key Vault might already exist"

# Create App Service Plan
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $APP_SERVICE_SKU \
    --is-linux || echo "App Service Plan might already exist"

# Create App Service
echo "🌐 Creating App Service..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON|3.11" || echo "App Service might already exist"

# Create staging slot
echo "🎭 Creating staging slot..."
az webapp deployment slot create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot staging || echo "Staging slot might already exist"

# Configure App Service settings
echo "⚙️ Configuring App Service settings..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        ENVIRONMENT="production" \
        DEBUG="False" \
        PYTHONPATH="/home/site/wwwroot" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        ENABLE_ORYX_BUILD="true" \
        POST_BUILD_SCRIPT_PATH="startup.sh"

# Enable Application Insights
echo "📊 Enabling Application Insights..."
az monitor app-insights component create \
    --app $APP_NAME \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --kind web || echo "Application Insights might already exist"

# Configure managed identity
echo "🆔 Configuring managed identity..."
az webapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP

# Get the principal ID for the managed identity
PRINCIPAL_ID=$(az webapp identity show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query principalId \
    --output tsv)

# Grant Key Vault access to the managed identity
echo "🔐 Granting Key Vault access..."
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list

# Store database connection string in Key Vault
echo "💾 Storing secrets in Key Vault..."
DB_PASSWORD=$(openssl rand -base64 32)
CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}?sslmode=require"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "database-url" \
    --value "$CONNECTION_STRING"

# Generate and store JWT secret
JWT_SECRET=$(openssl rand -base64 64)
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "jwt-secret" \
    --value "$JWT_SECRET"

# Generate and store app secret
APP_SECRET=$(openssl rand -base64 64)
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "app-secret" \
    --value "$APP_SECRET"

echo "✅ Azure resources setup completed successfully!"
echo ""
echo "📋 Resource Summary:"
echo "===================="
echo "App Service: https://${APP_NAME}.azurewebsites.net"
echo "Staging URL: https://${APP_NAME}-staging.azurewebsites.net"
echo "Database Server: ${DB_SERVER_NAME}.postgres.database.azure.com"
echo "Redis Cache: ${REDIS_NAME}.redis.cache.windows.net"
echo "Key Vault: https://${KEY_VAULT_NAME}.vault.azure.net"
echo ""
echo "🔑 Next Steps:"
echo "=============="
echo "1. Update your GitHub secrets with Azure credentials"
echo "2. Configure your Azure OpenAI resource connection"
echo "3. Deploy your application using GitHub Actions"
echo "4. Run database migrations"
echo ""
echo "🚀 Ready for deployment!"