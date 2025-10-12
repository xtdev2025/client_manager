#!/usr/bin/env python3
"""
Automated AWS Elastic Beanstalk Deployment Script for Client Manager
Converted from aws_eb_deploy.sh to Python
Usage: python scripts/aws_eb_deploy.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class AWSEBDeployer:
    """AWS Elastic Beanstalk deployment handler"""
    
    def __init__(self):
        self.app_name = "client-manager"
        self.env_name = "client-manager-prod"
        self.region = "us-east-1"
        self.platform = "python-3.10"
    
    def print_header(self):
        """Print deployment header"""
        print("🚀 AWS Elastic Beanstalk Deployment Script")
        print("=" * 43)
        print("")
    
    def check_aws_cli(self) -> bool:
        """Check if AWS CLI is installed"""
        if shutil.which("aws"):
            print("✅ AWS CLI found")
            return True
        
        print("❌ AWS CLI not found. Installing...")
        try:
            # Download and install AWS CLI
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
    
    def check_eb_cli(self) -> bool:
        """Check if EB CLI is installed"""
        if shutil.which("eb"):
            print("✅ EB CLI found")
            return True
        
        print("⚠️  EB CLI not found. Installing...")
        try:
            subprocess.run([
                "pip", "install", "awsebcli", "--upgrade", "--user"
            ], check=True)
            
            # Add to PATH
            home = Path.home()
            local_bin = home / ".local" / "bin"
            current_path = os.environ.get("PATH", "")
            
            if str(local_bin) not in current_path:
                os.environ["PATH"] = f"{current_path}:{local_bin}"
            
            print("✅ EB CLI installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install EB CLI: {e}")
            return False
    
    def check_credentials(self) -> bool:
        """Check AWS credentials"""
        print("")
        print("🔐 Checking AWS credentials...")
        
        try:
            result = subprocess.run([
                "aws", "sts", "get-caller-identity"
            ], capture_output=True, text=True, check=True)
            
            print("✅ AWS credentials configured")
            
            # Show account info
            import json
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
        response = input("Continue with Elastic Beanstalk deployment? (y/n) ")
        return response.lower().startswith('y')
    
    def prepare_files(self):
        """Prepare application files"""
        print("")
        print("📝 Preparing application files...")
        
        # Create Procfile
        procfile = Path("Procfile")
        if not procfile.exists():
            procfile.write_text("web: gunicorn --bind :8000 --workers 4 --timeout 600 run:app\n")
            print("✅ Procfile created")
        else:
            print("✅ Procfile already exists")
        
        # Add Gunicorn to requirements.txt
        requirements = Path("requirements.txt")
        if requirements.exists():
            content = requirements.read_text()
            if "gunicorn" not in content:
                with requirements.open("a") as f:
                    f.write("gunicorn==21.2.0\n")
                print("✅ Added Gunicorn to requirements.txt")
            else:
                print("✅ Gunicorn already in requirements.txt")
        
        # Create .ebextensions
        ebext_dir = Path(".ebextensions")
        ebext_dir.mkdir(exist_ok=True)
        
        python_config = ebext_dir / "python.config"
        if not python_config.exists():
            config_content = """option_settings:
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
"""
            python_config.write_text(config_content)
            print("✅ Created .ebextensions/python.config")
        else:
            print("✅ .ebextensions/python.config already exists")
        
        # Create .ebignore
        ebignore = Path(".ebignore")
        if not ebignore.exists():
            ignore_content = """venv/
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
"""
            ebignore.write_text(ignore_content)
            print("✅ Created .ebignore")
    
    def initialize_eb(self) -> bool:
        """Initialize Elastic Beanstalk"""
        print("")
        print("🔧 Initializing Elastic Beanstalk...")
        
        eb_dir = Path(".elasticbeanstalk")
        if not eb_dir.exists():
            try:
                subprocess.run([
                    "eb", "init", self.app_name,
                    "--platform", self.platform,
                    "--region", self.region
                ], check=True)
                print("✅ Elastic Beanstalk initialized")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to initialize EB: {e}")
                return False
        else:
            print("✅ Elastic Beanstalk already initialized")
            return True
    
    def deploy(self) -> bool:
        """Deploy to Elastic Beanstalk"""
        print("")
        print("🌍 Checking for existing environment...")
        
        try:
            # Check if environment exists
            subprocess.run([
                "eb", "status", self.env_name
            ], capture_output=True, check=True)
            
            print(f"⚠️  Environment '{self.env_name}' already exists")
            response = input("Do you want to deploy to existing environment? (y/n) ")
            
            if response.lower().startswith('y'):
                print("📤 Deploying to existing environment...")
                subprocess.run(["eb", "deploy", self.env_name], check=True)
                return True
            else:
                print("❌ Deployment cancelled")
                return False
                
        except subprocess.CalledProcessError:
            # Environment doesn't exist, create it
            print("🌍 Creating Elastic Beanstalk environment...")
            print("   This may take 5-10 minutes...")
            
            try:
                subprocess.run([
                    "eb", "create", self.env_name,
                    "--region", self.region,
                    "--platform", self.platform,
                    "--instance-type", "t2.small",
                    "--envvars", "FLASK_CONFIG=production"
                ], check=True)
                
                print(f"✅ Environment created: {self.env_name}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create environment: {e}")
                return False
    
    def show_completion_info(self):
        """Show deployment completion information"""
        try:
            # Get environment URL
            result = subprocess.run([
                "eb", "status", self.env_name
            ], capture_output=True, text=True, check=True)
            
            # Extract CNAME from output
            env_url = "N/A"
            for line in result.stdout.split('\n'):
                if "CNAME:" in line:
                    env_url = line.split("CNAME:")[1].strip()
                    break
            
            print("")
            print("=" * 44)
            print("✅ Deployment complete!")
            print("=" * 44)
            print("")
            print("📋 Environment Details:")
            print(f"   Application: {self.app_name}")
            print(f"   Environment: {self.env_name}")
            print(f"   URL:         http://{env_url}")
            print("")
            print("📋 Next Steps:")
            print("")
            print("1️⃣  Configure environment variables:")
            print('   eb setenv SECRET_KEY="sua-chave-secreta-super-segura"')
            print('   eb setenv MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/clientmanager"')
            print("")
            print("2️⃣  Open application in browser:")
            print("   eb open")
            print("")
            print("3️⃣  Create super admin:")
            print("   eb ssh")
            print("   cd /var/app/current")
            print("   python scripts/create_superadmin.py rootkit 13rafael")
            print("   exit")
            print("")
            print("📊 Useful commands:")
            print("   View status:  eb status")
            print("   View logs:    eb logs --stream")
            print("   Deploy:       eb deploy")
            print("   Scale:        eb scale 2")
            print("   SSH:          eb ssh")
            print("   Health:       eb health")
            print("   Open browser: eb open")
            print("")
            print("🗑️  To delete environment:")
            print(f"   eb terminate {self.env_name}")
            print("")
            print("💰 Estimated cost: ~$35/month (t2.small + Load Balancer)")
            print("   Free tier: First year free if eligible")
            print("")
            
        except subprocess.CalledProcessError:
            print("⚠️  Could not retrieve environment information")
    
    def run(self):
        """Run the deployment process"""
        self.print_header()
        
        # Check prerequisites
        if not self.check_aws_cli():
            sys.exit(1)
        
        if not self.check_eb_cli():
            sys.exit(1)
        
        if not self.check_credentials():
            sys.exit(1)
        
        if not self.confirm_deployment():
            print("❌ Deployment cancelled")
            sys.exit(1)
        
        # Prepare and deploy
        self.prepare_files()
        
        if not self.initialize_eb():
            sys.exit(1)
        
        if not self.deploy():
            sys.exit(1)
        
        self.show_completion_info()


def main():
    """Main function"""
    deployer = AWSEBDeployer()
    deployer.run()


if __name__ == "__main__":
    main()