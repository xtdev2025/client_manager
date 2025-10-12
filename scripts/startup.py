#!/usr/bin/env python3
"""
Startup script for Azure App Service
Converted from startup.sh to Python
"""

import os
import sys
import subprocess
from pathlib import Path


def activate_venv():
    """Activate virtual environment if exists"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment found, activating...")
        # For Python scripts, we don't need to activate venv explicitly
        # The shebang and proper PATH will handle this
        return True
    else:
        print("⚠️  No virtual environment found")
        return False


def initialize_database():
    """Run database initialization"""
    try:
        print("🔧 Initializing database...")
        from app import create_app
        app = create_app()
        with app.app_context():
            print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def start_application():
    """Start application with gunicorn"""
    try:
        print("🚀 Starting application with gunicorn...")
        cmd = [
            "gunicorn",
            "--bind=0.0.0.0:8000",
            "--timeout", "600",
            "--workers", "4",
            "run:app"
        ]
        
        # Execute gunicorn
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)


def main():
    """Main startup function"""
    print("🚀 Azure App Service Startup Script")
    print("=" * 40)
    
    # Activate virtual environment
    activate_venv()
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Start application
    start_application()


if __name__ == "__main__":
    main()