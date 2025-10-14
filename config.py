import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.local", override=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")

    MONGO_URI = (
        os.environ.get("MONGO_URI")
        or os.environ.get("MONGODB_URI")
        or "mongodb://localhost:27017/client_manager"
    )

    PORT = int(os.environ.get("PORT", 5000))

    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "true").lower() not in ["false", "0", "no"]
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI") or os.environ.get("RATELIMIT_STORAGE_URL", "memory://")

    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    HELEKET_PROJECT_URL = os.environ.get("HELEKET_PROJECT_URL")
    HELEKET_MERCHANT_ID = os.environ.get("HELEKET_MERCHANT_ID")
    HELEKET_API_KEY = os.environ.get("HELEKET_API_KEY")
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}