#!/bin/bash
# Automated AWS Elastic Beanstalk Deployment Script for Client Manager
# Usage: ./scripts/aws_eb_deploy.sh

set -e  # Exit on error

echo "🚀 AWS Elastic Beanstalk Deployment Script"
echo "==========================================="
echo ""

# Configuration
APP_NAME="client-manager"
ENV_NAME="client-manager-prod"
REGION="us-east-1"
PLATFORM="python-3.10"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    echo "✅ AWS CLI installed"
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "⚠️  EB CLI not found. Installing..."
    pip install awsebcli --upgrade --user
    
    # Add to PATH if needed
    export PATH="$PATH:$HOME/.local/bin"
    echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
    
    echo "✅ EB CLI installed"
fi

echo "✅ AWS CLI found: $(aws --version)"
echo "✅ EB CLI found: $(eb --version)"

# Check if logged in
echo ""
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️  Not logged in. Running 'aws configure'..."
    aws configure
else
    echo "✅ AWS credentials configured"
fi

# Show current account
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ACCOUNT_USER=$(aws sts get-caller-identity --query Arn --output text)
echo "📋 AWS Account: $ACCOUNT_ID"
echo "📋 User: $ACCOUNT_USER"
echo ""

# Ask for confirmation
read -p "Continue with Elastic Beanstalk deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Prepare application files
echo ""
echo "📝 Preparing application files..."

# Create Procfile if not exists
if [ ! -f "Procfile" ]; then
    echo "web: gunicorn --bind :8000 --workers 4 --timeout 600 run:app" > Procfile
    echo "✅ Procfile created"
else
    echo "✅ Procfile already exists"
fi

# Add Gunicorn to requirements.txt if not present
if ! grep -q "gunicorn" requirements.txt; then
    echo "gunicorn==21.2.0" >> requirements.txt
    echo "✅ Added Gunicorn to requirements.txt"
else
    echo "✅ Gunicorn already in requirements.txt"
fi

# Create .ebextensions directory and config
mkdir -p .ebextensions

if [ ! -f ".ebextensions/python.config" ]; then
    cat > .ebextensions/python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: run:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: app/static
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
  aws:elasticbeanstalk:command:
    Timeout: 600
EOF
    echo "✅ Created .ebextensions/python.config"
else
    echo "✅ .ebextensions/python.config already exists"
fi

# Create .ebignore if not exists
if [ ! -f ".ebignore" ]; then
    cat > .ebignore << 'EOF'
venv/
__pycache__/
*.pyc
*.pyo
.env
.git/
.github/
.vscode/
tests/
node_modules/
*.md
docs/
.ebextensions/
EOF
    echo "✅ Created .ebignore"
fi

# Initialize EB if not already initialized
echo ""
echo "🔧 Initializing Elastic Beanstalk..."
if [ ! -d ".elasticbeanstalk" ]; then
    eb init $APP_NAME \
        --platform $PLATFORM \
        --region $REGION
    echo "✅ Elastic Beanstalk initialized"
else
    echo "✅ Elastic Beanstalk already initialized"
fi

# Check if environment already exists
echo ""
echo "🌍 Checking for existing environment..."
if eb status $ENV_NAME &> /dev/null; then
    echo "⚠️  Environment '$ENV_NAME' already exists"
    
    read -p "Do you want to deploy to existing environment? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Deploying to existing environment..."
        eb deploy $ENV_NAME
    else
        echo "❌ Deployment cancelled"
        exit 0
    fi
else
    # Create environment
    echo "🌍 Creating Elastic Beanstalk environment..."
    echo "   This may take 5-10 minutes..."
    
    eb create $ENV_NAME \
        --region $REGION \
        --platform $PLATFORM \
        --instance-type t2.small \
        --envvars FLASK_CONFIG=production
    
    echo "✅ Environment created: $ENV_NAME"
fi

# Get environment URL
ENV_URL=$(eb status $ENV_NAME | grep "CNAME:" | awk '{print $2}')

echo ""
echo "============================================"
echo "✅ Deployment complete!"
echo "============================================"
echo ""
echo "📋 Environment Details:"
echo "   Application: $APP_NAME"
echo "   Environment: $ENV_NAME"
echo "   URL:         http://$ENV_URL"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Configure environment variables:"
echo "   eb setenv SECRET_KEY=\"sua-chave-secreta-super-segura\""
echo "   eb setenv MONGO_URI=\"mongodb+srv://user:pass@cluster.mongodb.net/clientmanager\""
echo ""
echo "2️⃣  Open application in browser:"
echo "   eb open"
echo ""
echo "3️⃣  Create super admin:"
echo "   eb ssh"
echo "   cd /var/app/current"
echo "   python scripts/create_superadmin.py rootkit 13rafael"
echo "   exit"
echo ""
echo "📊 Useful commands:"
echo "   View status:  eb status"
echo "   View logs:    eb logs --stream"
echo "   Deploy:       eb deploy"
echo "   Scale:        eb scale 2"
echo "   SSH:          eb ssh"
echo "   Health:       eb health"
echo "   Open browser: eb open"
echo ""
echo "🗑️  To delete environment:"
echo "   eb terminate $ENV_NAME"
echo ""
echo "💰 Estimated cost: ~\$35/month (t2.small + Load Balancer)"
echo "   Free tier: First year free if eligible"
echo ""
