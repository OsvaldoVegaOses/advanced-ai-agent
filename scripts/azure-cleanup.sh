#!/bin/bash

# Azure Resource Cleanup Script for Advanced AI Agent
# This script removes all Azure resources created for the application
# USE WITH CAUTION - This will delete all data!

set -e

# Configuration variables
RESOURCE_GROUP="startup_id_group"
SUBSCRIPTION_ID="0fbf8e45-6f68-43bb-acbc-36747f267122"
APP_NAME="advanced-ai-agent"

# Resource names
DB_SERVER_NAME="ai-agent-db"
REDIS_NAME="ai-agent-cache"
APP_SERVICE_PLAN="ai-agent-plan"
KEY_VAULT_NAME="ai-agent-vault"

echo "🚨 WARNING: This will delete ALL Azure resources for Advanced AI Agent!"
echo "This action cannot be undone and will result in data loss."
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi

echo "🗑️ Starting Azure resource cleanup..."

# Login to Azure (if not already logged in)
echo "🔐 Logging in to Azure..."
az login --tenant osvaldovegahotmail.onmicrosoft.com || echo "Already logged in"

# Set subscription
echo "📋 Setting subscription..."
az account set --subscription $SUBSCRIPTION_ID

# Delete App Service and slots
echo "🌐 Deleting App Service..."
az webapp delete \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --keep-empty-plan || echo "App Service not found or already deleted"

# Delete App Service Plan
echo "📋 Deleting App Service Plan..."
az appservice plan delete \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --yes || echo "App Service Plan not found or already deleted"

# Delete PostgreSQL Database
echo "🗃️ Deleting PostgreSQL database..."
az postgres server delete \
    --name $DB_SERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --yes || echo "Database server not found or already deleted"

# Delete Redis Cache
echo "🔄 Deleting Redis cache..."
az redis delete \
    --name $REDIS_NAME \
    --resource-group $RESOURCE_GROUP \
    --yes || echo "Redis cache not found or already deleted"

# Delete Key Vault (soft delete)
echo "🔑 Deleting Key Vault..."
az keyvault delete \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP || echo "Key Vault not found or already deleted"

# Purge Key Vault (permanent delete)
echo "🔥 Purging Key Vault (permanent delete)..."
az keyvault purge \
    --name $KEY_VAULT_NAME || echo "Key Vault not found in soft-delete state"

# Delete Application Insights
echo "📊 Deleting Application Insights..."
az monitor app-insights component delete \
    --app $APP_NAME \
    --resource-group $RESOURCE_GROUP || echo "Application Insights not found or already deleted"

echo "✅ Azure resource cleanup completed!"
echo ""
echo "📋 Cleanup Summary:"
echo "==================="
echo "✅ App Service deleted"
echo "✅ App Service Plan deleted"
echo "✅ PostgreSQL database deleted"
echo "✅ Redis cache deleted"
echo "✅ Key Vault deleted and purged"
echo "✅ Application Insights deleted"
echo ""
echo "ℹ️ Note: Resource group '$RESOURCE_GROUP' was not deleted as it may contain other resources."
echo "If you want to delete the entire resource group, run:"
echo "az group delete --name $RESOURCE_GROUP --yes"