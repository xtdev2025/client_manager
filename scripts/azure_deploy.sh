#!/bin/bash
# Automated Azure Deployment Script for Client Manager
# Usage: ./scripts/azure_deploy.sh

set -e  # Exit on error

echo "🚀 Azure Deployment Script - Client Manager"
echo "============================================"
echo ""

# Configuration
RESOURCE_GROUP="rg-clientmanager"
LOCATION="eastus"
APP_NAME="clientmanager-rootkit"
PLAN_NAME="plan-clientmanager"
SKU="B1"  # Change to F1 for free tier

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

echo "✅ Azure CLI found"

# Check if logged in
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in. Running 'az login'..."
    az login
else
    echo "✅ Already logged in to Azure"
fi

# Show current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "📋 Current subscription: $SUBSCRIPTION"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Create resource group
echo ""
echo "📦 Creating resource group..."
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "✅ Resource group already exists"
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    echo "✅ Resource group created: $RESOURCE_GROUP"
fi

# Create App Service Plan
echo ""
echo "📦 Creating App Service Plan..."
if az appservice plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "✅ App Service Plan already exists"
else
    az appservice plan create \
        --name $PLAN_NAME \
        --resource-group $RESOURCE_GROUP \
        --sku $SKU \
        --is-linux \
        --output none
    echo "✅ App Service Plan created: $PLAN_NAME (SKU: $SKU)"
fi

# Create Web App
echo ""
echo "🌐 Creating Web App..."
if az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "✅ Web App already exists"
else
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $PLAN_NAME \
        --name $APP_NAME \
        --runtime "PYTHON:3.10" \
        --output none
    echo "✅ Web App created: $APP_NAME"
fi

# Configure startup command
echo ""
echo "⚙️  Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.sh" \
    --output none
echo "✅ Startup command configured"

# Configure app settings (default values)
echo ""
echo "⚙️  Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        FLASK_CONFIG="production" \
        WEBSITES_PORT="8000" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    --output none
echo "✅ Default app settings configured"

# Configure deployment from local git
echo ""
echo "📤 Configuring Git deployment..."
GIT_URL=$(az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query url -o tsv 2>/dev/null || echo "")

if [ -n "$GIT_URL" ]; then
    echo "✅ Git deployment configured"
    
    # Add Azure remote if not exists
    if git remote get-url azure &> /dev/null; then
        echo "✅ Azure git remote already exists"
    else
        git remote add azure "$GIT_URL"
        echo "✅ Azure git remote added"
    fi
else
    echo "⚠️  Git deployment already configured or not available"
fi

# Get app URL
APP_URL="https://${APP_NAME}.azurewebsites.net"

echo ""
echo "============================================"
echo "✅ Deployment infrastructure ready!"
echo "============================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Configure environment variables:"
echo "   - Go to: https://portal.azure.com"
echo "   - Navigate to: App Services → $APP_NAME → Configuration"
echo "   - Add settings:"
echo "     • SECRET_KEY=<your-secret-key>"
echo "     • MONGO_URI=<your-mongodb-uri>"
echo ""
echo "2️⃣  Deploy application:"
echo "   git push azure main"
echo ""
echo "3️⃣  Create super admin:"
echo "   az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "   cd /home/site/wwwroot"
echo "   python scripts/create_superadmin.py rootkit 13rafael"
echo ""
echo "4️⃣  Access application:"
echo "   $APP_URL"
echo ""
echo "📊 Useful commands:"
echo "   View logs:    az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "   Restart app:  az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "   SSH to app:   az webapp ssh --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🗑️  To delete everything:"
echo "   az group delete --name $RESOURCE_GROUP --yes"
echo ""
