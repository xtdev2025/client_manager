#!/usr/bin/env python3
"""
Automated AWS EC2 Deployment Script for Client Manager
Converted from aws_ec2_deploy.sh to Python
Usage: python scripts/aws_ec2_deploy.py
"""

import os
import sys
import json
import time
import socket
import subprocess
import shutil
from pathlib import Path


class AWSEC2Deployer:
    """AWS EC2 deployment handler"""
    
    def __init__(self):
        self.key_name = "clientmanager-key"
        self.security_group_name = "clientmanager-sg"
        self.instance_name = "ClientManager"
        self.instance_type = "t2.micro"  # Free tier eligible
        self.region = "us-east-1"
        self.ami_id = "ami-0e001c9271cf7f3b9"  # Ubuntu 22.04 LTS in us-east-1
    
    def print_header(self):
        """Print deployment header"""
        print("🚀 AWS EC2 Deployment Script - Client Manager")
        print("=" * 46)
        print("")
    
    def check_aws_cli(self) -> bool:
        """Check if AWS CLI is installed"""
        if shutil.which("aws"):
            print("✅ AWS CLI found")
            return True
        
        print("❌ AWS CLI not found. Installing...")
        try:
            subprocess.run([
                "curl", "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip",
                "-o", "awscliv2.zip"
            ], check=True)
            
            subprocess.run(["unzip", "awscliv2.zip"], check=True)
            subprocess.run(["sudo", "./aws/install"], check=True)
            
            # Cleanup
            os.remove("awscliv2.zip")
            shutil.rmtree("aws")
            
            print("✅ AWS CLI installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install AWS CLI: {e}")
            return False
    
    def check_credentials(self) -> bool:
        """Check AWS credentials"""
        print("🔐 Checking AWS credentials...")
        
        try:
            result = subprocess.run([
                "aws", "sts", "get-caller-identity"
            ], capture_output=True, text=True, check=True)
            
            print("✅ AWS credentials configured")
            
            # Show account info
            identity = json.loads(result.stdout)
            print(f"📋 AWS Account: {identity.get('Account')}")
            print(f"📋 User: {identity.get('Arn')}")
            
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️  Not logged in. Running 'aws configure'...")
            try:
                subprocess.run(["aws", "configure"], check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to configure AWS credentials")
                return False
    
    def confirm_deployment(self) -> bool:
        """Ask for deployment confirmation"""
        print("")
        response = input(f"Continue with EC2 deployment in {self.region}? (y/n) ")
        return response.lower().startswith('y')
    
    def setup_ssh_key(self) -> bool:
        """Create SSH key pair if not exists"""
        print("")
        print("🔑 Setting up SSH key pair...")
        
        key_file = Path(f"{self.key_name}.pem")
        if key_file.exists():
            print(f"✅ SSH key already exists: {self.key_name}.pem")
            return True
        
        try:
            result = subprocess.run([
                "aws", "ec2", "create-key-pair",
                "--key-name", self.key_name,
                "--region", self.region,
                "--query", "KeyMaterial",
                "--output", "text"
            ], capture_output=True, text=True, check=True)
            
            key_file.write_text(result.stdout)
            key_file.chmod(0o400)
            
            print(f"✅ SSH key created: {self.key_name}.pem")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create SSH key: {e}")
            return False
    
    def setup_security_group(self) -> str:
        """Create security group if not exists"""
        print("")
        print("🔒 Setting up security group...")
        
        try:
            # Check if security group exists
            result = subprocess.run([
                "aws", "ec2", "describe-security-groups",
                "--group-names", self.security_group_name,
                "--region", self.region,
                "--query", "SecurityGroups[0].GroupId",
                "--output", "text"
            ], capture_output=True, text=True, check=True)
            
            sg_id = result.stdout.strip()
            print("✅ Security group already exists")
            return sg_id
            
        except subprocess.CalledProcessError:
            # Create security group
            try:
                result = subprocess.run([
                    "aws", "ec2", "create-security-group",
                    "--group-name", self.security_group_name,
                    "--description", "Client Manager Security Group",
                    "--region", self.region,
                    "--query", "GroupId",
                    "--output", "text"
                ], capture_output=True, text=True, check=True)
                
                sg_id = result.stdout.strip()
                
                # Add ingress rules
                rules = [
                    ("22", "SSH access"),
                    ("80", "HTTP access"),
                    ("443", "HTTPS access")
                ]
                
                for port, description in rules:
                    subprocess.run([
                        "aws", "ec2", "authorize-security-group-ingress",
                        "--group-id", sg_id,
                        "--protocol", "tcp",
                        "--port", port,
                        "--cidr", "0.0.0.0/0",
                        "--region", self.region
                    ], check=True)
                
                print(f"✅ Security group created: {sg_id}")
                return sg_id
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create security group: {e}")
                return ""
    
    def get_or_create_instance(self, sg_id: str) -> str:
        """Get existing instance or create new one"""
        print("")
        print("🖥️  Checking for existing instances...")
        
        try:
            # Check for existing instance
            result = subprocess.run([
                "aws", "ec2", "describe-instances",
                "--filters", f"Name=tag:Name,Values={self.instance_name}",
                "Name=instance-state-name,Values=running,pending,stopping,stopped",
                "--region", self.region,
                "--query", "Reservations[0].Instances[0].InstanceId",
                "--output", "text"
            ], capture_output=True, text=True, check=True)
            
            instance_id = result.stdout.strip()
            
            if instance_id != "None" and instance_id:
                print(f"⚠️  Instance already exists: {instance_id}")
                
                # Get instance state
                state_result = subprocess.run([
                    "aws", "ec2", "describe-instances",
                    "--instance-ids", instance_id,
                    "--region", self.region,
                    "--query", "Reservations[0].Instances[0].State.Name",
                    "--output", "text"
                ], capture_output=True, text=True, check=True)
                
                state = state_result.stdout.strip()
                print(f"   State: {state}")
                
                if state != "running":
                    print("   Starting instance...")
                    subprocess.run([
                        "aws", "ec2", "start-instances",
                        "--instance-ids", instance_id,
                        "--region", self.region
                    ], check=True)
                    
                    subprocess.run([
                        "aws", "ec2", "wait", "instance-running",
                        "--instance-ids", instance_id,
                        "--region", self.region
                    ], check=True)
                
                return instance_id
            
        except subprocess.CalledProcessError:
            pass
        
        # Create new instance
        print("🖥️  Creating EC2 instance...")
        try:
            result = subprocess.run([
                "aws", "ec2", "run-instances",
                "--image-id", self.ami_id,
                "--instance-type", self.instance_type,
                "--key-name", self.key_name,
                "--security-group-ids", sg_id,
                "--region", self.region,
                "--tag-specifications", f"ResourceType=instance,Tags=[{{Key=Name,Value={self.instance_name}}}]",
                "--query", "Instances[0].InstanceId",
                "--output", "text"
            ], capture_output=True, text=True, check=True)
            
            instance_id = result.stdout.strip()
            print(f"✅ Instance created: {instance_id}")
            
            print("⏳ Waiting for instance to be running...")
            subprocess.run([
                "aws", "ec2", "wait", "instance-running",
                "--instance-ids", instance_id,
                "--region", self.region
            ], check=True)
            
            return instance_id
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create instance: {e}")
            return ""
    
    def get_public_ip(self, instance_id: str) -> str:
        """Get public IP of instance"""
        try:
            result = subprocess.run([
                "aws", "ec2", "describe-instances",
                "--instance-ids", instance_id,
                "--region", self.region,
                "--query", "Reservations[0].Instances[0].PublicIpAddress",
                "--output", "text"
            ], capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            return ""
    
    def wait_for_ssh(self, public_ip: str) -> bool:
        """Wait for SSH to be available"""
        print("")
        print("⏳ Waiting for SSH to be available (this may take 2-3 minutes)...")
        
        max_attempts = 30
        for attempt in range(1, max_attempts + 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((public_ip, 22))
                sock.close()
                
                if result == 0:
                    print("✅ SSH is available")
                    return True
                    
            except Exception:
                pass
            
            time.sleep(10)
            print(f"   Attempt {attempt}/{max_attempts}...")
        
        print("❌ Timeout waiting for SSH. Please check instance status.")
        return False
    
    def create_setup_script(self) -> str:
        """Create server setup script"""
        print("")
        print("📝 Creating server setup script...")
        
        setup_script = """#!/bin/bash
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
ExecStart=/home/ubuntu/client_manager/venv/bin/gunicorn \\
    --workers 4 \\
    --bind unix:clientmanager.sock \\
    --timeout 600 \\
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
"""
        
        script_path = "/tmp/setup_server.sh"
        with open(script_path, 'w') as f:
            f.write(setup_script)
        
        return script_path
    
    def deploy_to_server(self, public_ip: str, script_path: str) -> bool:
        """Deploy application to server"""
        print("📤 Uploading setup script to server...")
        
        try:
            # Upload setup script
            subprocess.run([
                "scp", "-i", f"{self.key_name}.pem",
                "-o", "StrictHostKeyChecking=no",
                script_path, f"ubuntu@{public_ip}:/tmp/"
            ], check=True)
            
            print("")
            print("🚀 Executing setup on server...")
            
            # Execute setup script
            subprocess.run([
                "ssh", "-i", f"{self.key_name}.pem",
                "-o", "StrictHostKeyChecking=no",
                f"ubuntu@{public_ip}",
                "bash /tmp/setup_server.sh"
            ], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy to server: {e}")
            return False
    
    def show_completion_info(self, instance_id: str, public_ip: str):
        """Show deployment completion information"""
        print("")
        print("=" * 44)
        print("✅ Deployment complete!")
        print("=" * 44)
        print("")
        print("📋 Instance Details:")
        print(f"   Instance ID: {instance_id}")
        print(f"   Public IP:   {public_ip}")
        print(f"   SSH Key:     {self.key_name}.pem")
        print("")
        print("🔗 Access your application:")
        print(f"   http://{public_ip}")
        print("")
        print("📋 Next Steps:")
        print("")
        print("1️⃣  Configure environment variables:")
        print(f"   ssh -i {self.key_name}.pem ubuntu@{public_ip}")
        print("   cd /home/ubuntu/client_manager")
        print("   nano .env")
        print("")
        print("   Add:")
        print("   SECRET_KEY=sua-chave-secreta")
        print("   MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/clientmanager")
        print("   FLASK_CONFIG=production")
        print("")
        print("2️⃣  Start the application:")
        print("   sudo systemctl start clientmanager")
        print("   sudo systemctl status clientmanager")
        print("")
        print("3️⃣  Create super admin:")
        print("   cd /home/ubuntu/client_manager")
        print("   source venv/bin/activate")
        print("   python scripts/create_superadmin.py rootkit 13rafael")
        print("")
        print("📊 Useful commands:")
        print(f"   SSH:          ssh -i {self.key_name}.pem ubuntu@{public_ip}")
        print("   View logs:    sudo journalctl -u clientmanager -f")
        print("   Restart app:  sudo systemctl restart clientmanager")
        print("   Restart nginx: sudo systemctl restart nginx")
        print("")
        print("🗑️  To delete everything:")
        print(f"   aws ec2 terminate-instances --instance-ids {instance_id} --region {self.region}")
        print(f"   aws ec2 delete-key-pair --key-name {self.key_name} --region {self.region}")
        print(f"   rm {self.key_name}.pem")
        print("")
    
    def run(self):
        """Run the deployment process"""
        self.print_header()
        
        # Check prerequisites
        if not self.check_aws_cli():
            sys.exit(1)
        
        if not self.check_credentials():
            sys.exit(1)
        
        if not self.confirm_deployment():
            print("❌ Deployment cancelled")
            sys.exit(1)
        
        # Setup infrastructure
        if not self.setup_ssh_key():
            sys.exit(1)
        
        sg_id = self.setup_security_group()
        if not sg_id:
            sys.exit(1)
        
        instance_id = self.get_or_create_instance(sg_id)
        if not instance_id:
            sys.exit(1)
        
        public_ip = self.get_public_ip(instance_id)
        if not public_ip:
            print("❌ Failed to get public IP")
            sys.exit(1)
        
        print(f"✅ Instance running at: {public_ip}")
        
        # Wait for SSH and deploy
        if not self.wait_for_ssh(public_ip):
            sys.exit(1)
        
        script_path = self.create_setup_script()
        
        if not self.deploy_to_server(public_ip, script_path):
            sys.exit(1)
        
        self.show_completion_info(instance_id, public_ip)


def main():
    """Main function"""
    deployer = AWSEC2Deployer()
    deployer.run()


if __name__ == "__main__":
    main()