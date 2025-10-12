#!/usr/bin/env python3
"""
Automated Azure Deployment Script for Client Manager
Converted from azure_deploy.sh to Python
Usage: python scripts/azure_deploy.py
"""

import sys
import json
import subprocess
import shutil


class AzureDeployer:
    """Azure deployment handler"""
    
    def __init__(self):
        self.resource_group = "rg-clientmanager"
        self.location = "eastus"
        self.app_name = "clientmanager-rootkit"
        self.plan_name = "plan-clientmanager"
        self.sku = "B1"  # Change to F1 for free tier
    
    def print_header(self):
        """Print deployment header"""
        print("🚀 Azure Deployment Script - Client Manager")
        print("=" * 44)
        print("")
    
    def check_azure_cli(self) -> bool:
        """Check if Azure CLI is installed"""
        if shutil.which("az"):
            print("✅ Azure CLI found")
            return True
        
        print("❌ Azure CLI not found. Please install it first:")
        print("   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash")
        return False
    
    def check_login(self) -> bool:
        """Check if logged in to Azure"""
        print("🔐 Checking Azure login status...")
        
        try:
            result = subprocess.run([
                "az", "account", "show"
            ], capture_output=True, text=True, check=True)
            
            print("✅ Already logged in to Azure")
            
            # Show current subscription
            account_info = json.loads(result.stdout)
            subscription_name = account_info.get("name", "Unknown")
            print(f"📋 Current subscription: {subscription_name}")
            
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️  Not logged in. Running 'az login'...")
            try:
                subprocess.run(["az", "login"], check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to login to Azure")
                return False
    
    def confirm_deployment(self) -> bool:
        """Ask for deployment confirmation"""
        print("")
        response = input("Continue with deployment? (y/n) ")
        return response.lower().startswith('y')
    
    def create_resource_group(self) -> bool:
        """Create resource group"""
        print("")
        print("📦 Creating resource group...")
        
        try:
            # Check if resource group exists
            subprocess.run([
                "az", "group", "show",
                "--name", self.resource_group
            ], capture_output=True, check=True)
            
            print("✅ Resource group already exists")
            return True
            
        except subprocess.CalledProcessError:
            # Create resource group
            try:
                subprocess.run([
                    "az", "group", "create",
                    "--name", self.resource_group,
                    "--location", self.location,
                    "--output", "none"
                ], check=True)
                
                print(f"✅ Resource group created: {self.resource_group}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create resource group: {e}")
                return False
    
    def create_app_service_plan(self) -> bool:
        """Create App Service Plan"""
        print("")
        print("📦 Creating App Service Plan...")
        
        try:
            # Check if plan exists
            subprocess.run([
                "az", "appservice", "plan", "show",
                "--name", self.plan_name,
                "--resource-group", self.resource_group
            ], capture_output=True, check=True)
            
            print("✅ App Service Plan already exists")
            return True
            
        except subprocess.CalledProcessError:
            # Create plan
            try:
                subprocess.run([
                    "az", "appservice", "plan", "create",
                    "--name", self.plan_name,
                    "--resource-group", self.resource_group,
                    "--sku", self.sku,
                    "--is-linux",
                    "--output", "none"
                ], check=True)
                
                print(f"✅ App Service Plan created: {self.plan_name} (SKU: {self.sku})")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create App Service Plan: {e}")
                return False
    
    def create_web_app(self) -> bool:
        """Create Web App"""
        print("")
        print("🌐 Creating Web App...")
        
        try:
            # Check if web app exists
            subprocess.run([
                "az", "webapp", "show",
                "--name", self.app_name,
                "--resource-group", self.resource_group
            ], capture_output=True, check=True)
            
            print("✅ Web App already exists")
            return True
            
        except subprocess.CalledProcessError:
            # Create web app
            try:
                subprocess.run([
                    "az", "webapp", "create",
                    "--resource-group", self.resource_group,
                    "--plan", self.plan_name,
                    "--name", self.app_name,
                    "--runtime", "PYTHON:3.10",
                    "--output", "none"
                ], check=True)
                
                print(f"✅ Web App created: {self.app_name}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create Web App: {e}")
                return False
    
    def configure_startup(self) -> bool:
        """Configure startup command"""
        print("")
        print("⚙️  Configuring startup command...")
        
        try:
            subprocess.run([
                "az", "webapp", "config", "set",
                "--resource-group", self.resource_group,
                "--name", self.app_name,
                "--startup-file", "startup.sh",
                "--output", "none"
            ], check=True)
            
            print("✅ Startup command configured")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to configure startup: {e}")
            return False
    
    def configure_app_settings(self) -> bool:
        """Configure app settings"""
        print("")
        print("⚙️  Configuring app settings...")
        
        try:
            subprocess.run([
                "az", "webapp", "config", "appsettings", "set",
                "--resource-group", self.resource_group,
                "--name", self.app_name,
                "--settings",
                "FLASK_CONFIG=production",
                "WEBSITES_PORT=8000",
                "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
                "--output", "none"
            ], check=True)
            
            print("✅ Default app settings configured")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to configure app settings: {e}")
            return False
    
    def configure_git_deployment(self) -> bool:
        """Configure deployment from local git"""
        print("")
        print("📤 Configuring Git deployment...")
        
        try:
            result = subprocess.run([
                "az", "webapp", "deployment", "source", "config-local-git",
                "--name", self.app_name,
                "--resource-group", self.resource_group,
                "--query", "url",
                "-o", "tsv"
            ], capture_output=True, text=True, check=True)
            
            git_url = result.stdout.strip()
            
            if git_url:
                print("✅ Git deployment configured")
                
                # Check if Azure remote exists
                try:
                    subprocess.run([
                        "git", "remote", "get-url", "azure"
                    ], capture_output=True, check=True)
                    
                    print("✅ Azure git remote already exists")
                    
                except subprocess.CalledProcessError:
                    # Add Azure remote
                    try:
                        subprocess.run([
                            "git", "remote", "add", "azure", git_url
                        ], check=True)
                        
                        print("✅ Azure git remote added")
                        
                    except subprocess.CalledProcessError as e:
                        print(f"⚠️  Failed to add git remote: {e}")
                
                return True
            else:
                print("⚠️  Git deployment already configured or not available")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git deployment configuration failed: {e}")
            return True  # Not critical, continue
    
    def show_completion_info(self):
        """Show deployment completion information"""
        app_url = f"https://{self.app_name}.azurewebsites.net"
        
        print("")
        print("=" * 44)
        print("✅ Deployment infrastructure ready!")
        print("=" * 44)
        print("")
        print("📋 Next Steps:")
        print("")
        print("1️⃣  Configure environment variables:")
        print("   - Go to: https://portal.azure.com")
        print(f"   - Navigate to: App Services → {self.app_name} → Configuration")
        print("   - Add settings:")
        print("     • SECRET_KEY=<your-secret-key>")
        print("     • MONGO_URI=<your-mongodb-uri>")
        print("")
        print("2️⃣  Deploy application:")
        print("   git push azure main")
        print("")
        print("3️⃣  Create super admin:")
        print(f"   az webapp ssh --name {self.app_name} --resource-group {self.resource_group}")
        print("   cd /home/site/wwwroot")
        print("   python scripts/create_superadmin.py rootkit 13rafael")
        print("")
        print("4️⃣  Access application:")
        print(f"   {app_url}")
        print("")
        print("📊 Useful commands:")
        print(f"   View logs:    az webapp log tail --name {self.app_name} --resource-group {self.resource_group}")
        print(f"   Restart app:  az webapp restart --name {self.app_name} --resource-group {self.resource_group}")
        print(f"   SSH to app:   az webapp ssh --name {self.app_name} --resource-group {self.resource_group}")
        print("")
        print("🗑️  To delete everything:")
        print(f"   az group delete --name {self.resource_group} --yes")
        print("")
    
    def run(self):
        """Run the deployment process"""
        self.print_header()
        
        # Check prerequisites
        if not self.check_azure_cli():
            sys.exit(1)
        
        if not self.check_login():
            sys.exit(1)
        
        if not self.confirm_deployment():
            print("❌ Deployment cancelled")
            sys.exit(1)
        
        # Create infrastructure
        if not self.create_resource_group():
            sys.exit(1)
        
        if not self.create_app_service_plan():
            sys.exit(1)
        
        if not self.create_web_app():
            sys.exit(1)
        
        if not self.configure_startup():
            sys.exit(1)
        
        if not self.configure_app_settings():
            sys.exit(1)
        
        self.configure_git_deployment()  # Not critical
        
        self.show_completion_info()


def main():
    """Main function"""
    deployer = AzureDeployer()
    deployer.run()


if __name__ == "__main__":
    main()