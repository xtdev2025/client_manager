#!/bin/bash
# Automated AWS EC2 Deployment Script for Client Manager
# Usage: ./scripts/aws_ec2_deploy.sh

set -e  # Exit on error

echo "🚀 AWS EC2 Deployment Script - Client Manager"
echo "=============================================="
echo ""

# Configuration
KEY_NAME="clientmanager-key"
SECURITY_GROUP_NAME="clientmanager-sg"
INSTANCE_NAME="ClientManager"
INSTANCE_TYPE="t2.micro"  # Free tier eligible
REGION="us-east-1"
AMI_ID="ami-0e001c9271cf7f3b9"  # Ubuntu 22.04 LTS in us-east-1

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

echo "✅ AWS CLI found"

# Check if logged in
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
read -p "Continue with EC2 deployment in $REGION? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Create SSH key pair if not exists
echo ""
echo "🔑 Setting up SSH key pair..."
if [ -f "${KEY_NAME}.pem" ]; then
    echo "✅ SSH key already exists: ${KEY_NAME}.pem"
else
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    
    chmod 400 ${KEY_NAME}.pem
    echo "✅ SSH key created: ${KEY_NAME}.pem"
fi

# Create security group if not exists
echo ""
echo "🔒 Setting up security group..."
if aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --region $REGION &> /dev/null; then
    echo "✅ Security group already exists"
    SG_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP_NAME \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
else
    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Client Manager Security Group" \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "✅ Security group created: $SG_ID"
fi

# Check if instance already exists
echo ""
echo "🖥️  Checking for existing instances..."
EXISTING_INSTANCE=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running,pending,stopping,stopped" \
    --region $REGION \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text 2>/dev/null)

if [ "$EXISTING_INSTANCE" != "None" ] && [ -n "$EXISTING_INSTANCE" ]; then
    echo "⚠️  Instance already exists: $EXISTING_INSTANCE"
    
    # Get instance state
    INSTANCE_STATE=$(aws ec2 describe-instances \
        --instance-ids $EXISTING_INSTANCE \
        --region $REGION \
        --query 'Reservations[0].Instances[0].State.Name' \
        --output text)
    
    echo "   State: $INSTANCE_STATE"
    
    if [ "$INSTANCE_STATE" != "running" ]; then
        echo "   Starting instance..."
        aws ec2 start-instances --instance-ids $EXISTING_INSTANCE --region $REGION
        aws ec2 wait instance-running --instance-ids $EXISTING_INSTANCE --region $REGION
    fi
    
    INSTANCE_ID=$EXISTING_INSTANCE
else
    # Create EC2 instance
    echo "🖥️  Creating EC2 instance..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SG_ID \
        --region $REGION \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "✅ Instance created: $INSTANCE_ID"
    echo "⏳ Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
fi

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Instance running at: $PUBLIC_IP"

# Wait for SSH to be available
echo ""
echo "⏳ Waiting for SSH to be available (this may take 2-3 minutes)..."
MAX_ATTEMPTS=30
ATTEMPT=0
while ! nc -z $PUBLIC_IP 22 2>/dev/null; do
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "❌ Timeout waiting for SSH. Please check instance status."
        exit 1
    fi
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
done

echo "✅ SSH is available"

# Create setup script
echo ""
echo "📝 Creating server setup script..."
cat > /tmp/setup_server.sh << 'SETUP_SCRIPT'
#!/bin/bash
set -e

echo "Updating system packages..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo "Installing Python 3.10 and dependencies..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip nginx git

echo "Cloning repository..."
cd /home/ubuntu
if [ -d "client_manager" ]; then
    echo "Repository already exists, pulling latest..."
    cd client_manager
    git pull origin main
    cd ..
else
    git clone https://github.com/rootkitoriginal/client_manager.git
fi

cd client_manager

echo "Setting up Python virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo "Creating systemd service..."
sudo tee /etc/systemd/system/clientmanager.service > /dev/null << 'EOF'
[Unit]
Description=Client Manager Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/client_manager
Environment="PATH=/home/ubuntu/client_manager/venv/bin"
ExecStart=/home/ubuntu/client_manager/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:clientmanager.sock \
    --timeout 600 \
    run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/clientmanager > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/client_manager/clientmanager.sock;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    location /static {
        alias /home/ubuntu/client_manager/app/static;
        expires 30d;
    }

    client_max_body_size 100M;
}
EOF

sudo ln -sf /etc/nginx/sites-available/clientmanager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Server setup complete!"
SETUP_SCRIPT

# Copy and execute setup script
echo "📤 Uploading setup script to server..."
scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no /tmp/setup_server.sh ubuntu@${PUBLIC_IP}:/tmp/

echo ""
echo "🚀 Executing setup on server..."
ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ubuntu@${PUBLIC_IP} 'bash /tmp/setup_server.sh'

echo ""
echo "============================================"
echo "✅ Deployment complete!"
echo "============================================"
echo ""
echo "📋 Instance Details:"
echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP:   $PUBLIC_IP"
echo "   SSH Key:     ${KEY_NAME}.pem"
echo ""
echo "🔗 Access your application:"
echo "   http://${PUBLIC_IP}"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Configure environment variables:"
echo "   ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo "   cd /home/ubuntu/client_manager"
echo "   nano .env"
echo ""
echo "   Add:"
echo "   SECRET_KEY=sua-chave-secreta"
echo "   MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/clientmanager"
echo "   FLASK_CONFIG=production"
echo ""
echo "2️⃣  Start the application:"
echo "   sudo systemctl start clientmanager"
echo "   sudo systemctl status clientmanager"
echo ""
echo "3️⃣  Create super admin:"
echo "   cd /home/ubuntu/client_manager"
echo "   source venv/bin/activate"
echo "   python scripts/create_superadmin.py rootkit 13rafael"
echo ""
echo "📊 Useful commands:"
echo "   SSH:          ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo "   View logs:    sudo journalctl -u clientmanager -f"
echo "   Restart app:  sudo systemctl restart clientmanager"
echo "   Restart nginx: sudo systemctl restart nginx"
echo ""
echo "🗑️  To delete everything:"
echo "   aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
echo "   aws ec2 delete-security-group --group-id $SG_ID --region $REGION"
echo "   aws ec2 delete-key-pair --key-name $KEY_NAME --region $REGION"
echo "   rm ${KEY_NAME}.pem"
echo ""
