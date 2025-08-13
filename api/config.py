import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the API"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # API Keys
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
    FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
    
    # Data Directories
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    SCRAPED_DIR = os.path.join(DATA_DIR, 'scraped')
    PROMPTS_DIR = os.getenv('PROMPTS_DIR', 'prompts')
    
    # File Paths
    COMPANIES_FILE = os.path.join(DATA_DIR, 'companies.json')
    
    # API Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Perplexity API Configuration
    PERPLEXITY_BASE_URL = 'https://api.perplexity.ai'
    PERPLEXITY_MODEL = 'sonar'
    PERPLEXITY_MAX_TOKENS = 4000
    PERPLEXITY_TEMPERATURE = 0.1
    PERPLEXITY_TOP_P = 0.9

# Validate required configuration
def validate_config():
    """Validate that all required configuration is present"""
    required_keys = ['PERPLEXITY_API_KEY', 'FIRECRAWL_API_KEY']
    missing_keys = [key for key in required_keys if not getattr(Config, key)]
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return True 