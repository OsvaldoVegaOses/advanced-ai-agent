#!/bin/bash

# Fixed Azure Resource Setup Script for Advanced AI Agent
# This script creates all necessary Azure resources using modern services

set -e

# Configuration variables
RESOURCE_GROUP="startup_id_group"
LOCATION="westus2"
SUBSCRIPTION_ID="0fbf8e45-6f68-43bb-acbc-36747f267122"
APP_NAME="advanced-ai-agent"

# Database configuration (using Flexible Server)
DB_SERVER_NAME="ai-agent-db-flexible"
DB_NAME="ai_agent_db"
DB_ADMIN_USER="aiagent"
DB_ADMIN_PASSWORD="$(openssl rand -base64 32 | tr -d '=' | cut -c1-20)Aa1!"

# Redis configuration
REDIS_NAME="ai-agent-cache-$(date +%s)"
REDIS_SKU="Basic"
REDIS_VM_SIZE="C0"

# App Service configuration
APP_SERVICE_PLAN="ai-agent-plan"
APP_SERVICE_SKU="B1"  # Changed to B1 for slots support

# Key Vault configuration (unique name)
KEY_VAULT_NAME="ai-vault-$(date +%s)"

echo "🚀 Setting up Azure resources for Advanced AI Agent..."

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription $SUBSCRIPTION_ID

# Register required resource providers
echo "📝 Registering resource providers..."
az provider register --namespace Microsoft.DBforPostgreSQL --wait
az provider register --namespace Microsoft.Cache --wait
az provider register --namespace Microsoft.Web --wait
az provider register --namespace Microsoft.KeyVault --wait
az provider register --namespace Microsoft.Insights --wait

echo "✅ Resource providers registered"

# Create PostgreSQL Flexible Server
echo "🗃️ Creating PostgreSQL Flexible Server..."
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user $DB_ADMIN_USER \
    --admin-password $DB_ADMIN_PASSWORD \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 13 \
    --public-access 0.0.0.0 \
    --yes

echo "✅ PostgreSQL Flexible Server created"

# Create database
echo "📊 Creating application database..."
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --database-name $DB_NAME

echo "✅ Database created"

# Create Redis Cache
echo "🔄 Creating Redis cache..."
az redis create \
    --name $REDIS_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $REDIS_SKU \
    --vm-size $REDIS_VM_SIZE \
    --enable-non-ssl-port

echo "✅ Redis cache created"

# Create Key Vault
echo "🔑 Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku standard

echo "✅ Key Vault created"

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

echo "✅ App Service created"

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

# Store secrets in Key Vault
echo "💾 Storing secrets in Key Vault..."

# Database connection string
CONNECTION_STRING="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}?sslmode=require"
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "database-url" \
    --value "$CONNECTION_STRING"

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

echo "✅ Secrets stored in Key Vault"

# Get Redis connection info
REDIS_HOST=$(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query hostName --output tsv)
REDIS_PORT=$(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query port --output tsv)
REDIS_PASSWORD=$(az redis list-keys --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query primaryKey --output tsv)

# Store Redis connection string
REDIS_CONNECTION_STRING="redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0"
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "redis-url" \
    --value "$REDIS_CONNECTION_STRING"

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
        POST_BUILD_SCRIPT_PATH="startup.sh" \
        DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/database-url/)" \
        REDIS_URL="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/redis-url/)" \
        JWT_SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/jwt-secret/)" \
        SECRET_KEY="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/app-secret/)" \
        USE_MANAGED_IDENTITY="True" \
        AZURE_OPENAI_ENDPOINT="https://nubeweb.openai.azure.com/" \
        AZURE_OPENAI_VERSION="2024-10-21" \
        AZURE_CHAT_DEPLOYMENT="gpt-4o-mini" \
        AZURE_VISION_DEPLOYMENT="gpt-4o-mini" \
        AZURE_REASONING_DEPLOYMENT="o1" \
        AZURE_EMBEDDINGS_DEPLOYMENT="text-embedding-3-small" \
        ALLOWED_HOSTS="${APP_NAME}.azurewebsites.net,*.azurewebsites.net"

echo "✅ App Service settings configured"

# Enable Application Insights
echo "📊 Enabling Application Insights..."
az monitor app-insights component create \
    --app $APP_NAME \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --kind web \
    --retention-time 30

echo "✅ Application Insights enabled"

# Enable HTTPS only
echo "🔐 Enabling HTTPS only..."
az webapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --https-only true

echo "✅ HTTPS only enabled"

echo ""
echo "✅ Azure resources setup completed successfully!"
echo ""
echo "📋 Resource Summary:"
echo "===================="
echo "App Service: https://${APP_NAME}.azurewebsites.net"
echo "Database Server: ${DB_SERVER_NAME}.postgres.database.azure.com"
echo "Redis Cache: ${REDIS_HOST}:${REDIS_PORT}"
echo "Key Vault: https://${KEY_VAULT_NAME}.vault.azure.net"
echo "Principal ID: ${PRINCIPAL_ID}"
echo ""
echo "🔑 Connection Details (save these):"
echo "===================================="
echo "Database URL: $CONNECTION_STRING"
echo "Redis URL: $REDIS_CONNECTION_STRING"
echo "Key Vault Name: $KEY_VAULT_NAME"
echo ""
echo "🚀 Ready for deployment!"