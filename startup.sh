#!/bin/bash
# Startup script for Azure App Service

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run database initialization
python -c "from app import create_app; app = create_app(); print('Database initialized')"

# Start application with gunicorn
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 run:app
