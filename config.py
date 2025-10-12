import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/client_manager'
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}