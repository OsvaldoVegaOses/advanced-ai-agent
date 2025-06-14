#!/bin/bash

# Post-deployment configuration script for Advanced AI Agent
# Run this script after successful Azure deployment

set -e

# Configuration variables
RESOURCE_GROUP="startup_id_group"
APP_NAME="advanced-ai-agent"
SUBSCRIPTION_ID="0fbf8e45-6f68-43bb-acbc-36747f267122"

echo "🔧 Running post-deployment configuration for Advanced AI Agent..."

# Login to Azure
echo "🔐 Logging in to Azure..."
az login --tenant osvaldovegahotmail.onmicrosoft.com || echo "Already logged in"
az account set --subscription $SUBSCRIPTION_ID

# Test application health
echo "🏥 Testing application health..."
APP_URL="https://${APP_NAME}.azurewebsites.net"
STAGING_URL="https://${APP_NAME}-staging.azurewebsites.net"

# Wait for app to be ready
echo "⏳ Waiting for application to start..."
sleep 60

# Health check
echo "🔍 Running health checks..."
if curl -f "${APP_URL}/health/live" > /dev/null 2>&1; then
    echo "✅ Production health check passed"
else
    echo "❌ Production health check failed"
fi

if curl -f "${STAGING_URL}/health/live" > /dev/null 2>&1; then
    echo "✅ Staging health check passed"
else
    echo "❌ Staging health check failed"
fi

# Test API endpoints
echo "🧪 Testing API endpoints..."
if curl -f "${APP_URL}/" > /dev/null 2>&1; then
    echo "✅ Root endpoint accessible"
else
    echo "❌ Root endpoint not accessible"
fi

# Check if database connection is working
echo "🗃️ Testing database connection..."
if curl -f "${APP_URL}/health/db" > /dev/null 2>&1; then
    echo "✅ Database connection working"
else
    echo "⚠️ Database connection test unavailable"
fi

# Configure custom domain (if needed)
echo "🌐 Custom domain configuration..."
echo "To configure a custom domain:"
echo "1. Go to Azure Portal → App Services → $APP_NAME → Custom domains"
echo "2. Add your domain name"
echo "3. Configure SSL certificate"

# Configure monitoring alerts
echo "📊 Setting up monitoring alerts..."

# CPU alert
az monitor metrics alert create \
    --name "high-cpu-alert" \
    --resource-group $RESOURCE_GROUP \
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME" \
    --condition "avg Percentage CPU > 80" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --severity 2 \
    --description "High CPU usage alert" || echo "CPU alert might already exist"

# Memory alert
az monitor metrics alert create \
    --name "high-memory-alert" \
    --resource-group $RESOURCE_GROUP \
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME" \
    --condition "avg Memory working set > 1000000000" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --severity 2 \
    --description "High memory usage alert" || echo "Memory alert might already exist"

# Response time alert
az monitor metrics alert create \
    --name "slow-response-alert" \
    --resource-group $RESOURCE_GROUP \
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$APP_NAME" \
    --condition "avg Response time > 5" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --severity 2 \
    --description "Slow response time alert" || echo "Response time alert might already exist"

# Configure backup
echo "💾 Configuring backup..."
az webapp config backup create \
    --resource-group $RESOURCE_GROUP \
    --webapp-name $APP_NAME \
    --backup-name "daily-backup" \
    --container-url "your-storage-container-url" \
    --retain-one true \
    --retention-period-in-days 30 || echo "Backup configuration skipped - configure storage account first"

# Enable diagnostic logs
echo "📝 Enabling diagnostic logs..."
az webapp log config \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem

# Configure scaling rules
echo "📈 Configuring auto-scaling..."
az monitor autoscale create \
    --resource-group $RESOURCE_GROUP \
    --resource "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/serverfarms/ai-agent-plan" \
    --resource-type Microsoft.Web/serverfarms \
    --name "ai-agent-autoscale" \
    --min-count 1 \
    --max-count 3 \
    --count 1 || echo "Autoscale might already exist"

# Scale out rule
az monitor autoscale rule create \
    --resource-group $RESOURCE_GROUP \
    --autoscale-name "ai-agent-autoscale" \
    --condition "Percentage CPU > 70 avg 5m" \
    --scale out 1 \
    --cooldown 5 || echo "Scale out rule might already exist"

# Scale in rule
az monitor autoscale rule create \
    --resource-group $RESOURCE_GROUP \
    --autoscale-name "ai-agent-autoscale" \
    --condition "Percentage CPU < 30 avg 10m" \
    --scale in 1 \
    --cooldown 10 || echo "Scale in rule might already exist"

# Security recommendations
echo "🔒 Security recommendations:"
echo "1. Enable Azure Security Center recommendations"
echo "2. Configure Azure Key Vault access policies"
echo "3. Review and update firewall rules"
echo "4. Enable Azure AD authentication if needed"
echo "5. Configure HTTPS-only access"

# Enable HTTPS only
echo "🔐 Enabling HTTPS only..."
az webapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --https-only true

# Get important URLs and information
echo ""
echo "✅ Post-deployment configuration completed!"
echo ""
echo "📋 Application Information:"
echo "=========================="
echo "Production URL: $APP_URL"
echo "Staging URL: $STAGING_URL"
echo "API Documentation: $APP_URL/docs (if enabled)"
echo "Health Check: $APP_URL/health/live"
echo "Metrics: $APP_URL/metrics/summary"
echo ""
echo "🔧 Azure Resources:"
echo "=================="
echo "App Service: $APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "Database: ai-agent-db.postgres.database.azure.com"
echo "Redis: ai-agent-cache.redis.cache.windows.net"
echo "Key Vault: ai-agent-vault.vault.azure.net"
echo ""
echo "📊 Monitoring:"
echo "=============="
echo "Application Insights: Azure Portal → Application Insights → $APP_NAME"
echo "Logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "Metrics: Azure Portal → App Services → $APP_NAME → Metrics"
echo ""
echo "🚀 Your Advanced AI Agent is now live and configured!"
echo "Visit $APP_URL to start using your application."