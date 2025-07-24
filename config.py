"""
Configuration loader for Tableau Analytics Extensions Job Scraper
Securely loads API credentials and configuration from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class that loads settings from environment variables"""
    
    # API Credentials (REQUIRED)
    JOB_API_KEY = os.getenv('JOB_API_KEY')
    JOB_API_SECRET = os.getenv('JOB_API_SECRET', '')  # Optional, some APIs don't need secret
    JOB_API_BASE_URL = os.getenv('JOB_API_BASE_URL', 'https://api.adzuna.com/v1/api')
    
    # Alternative API keys (optional)
    INDEED_API_KEY = os.getenv('INDEED_API_KEY')
    LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY')
    
    # Database or other service credentials (optional)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Default search parameters (fallback values if not specified)
    DEFAULT_SEARCH_LOCATION = os.getenv('DEFAULT_SEARCH_LOCATION', 'us')
    DEFAULT_TARGET_JOBS = int(os.getenv('DEFAULT_TARGET_JOBS', '120'))
    DEFAULT_MAX_PAGES = int(os.getenv('DEFAULT_MAX_PAGES', '4'))
    
    @classmethod
    def validate_required_credentials(cls):
        """
        Validate that required API credentials are present
        Returns True if valid, raises ValueError if missing required credentials
        """
        missing = []
        
        if not cls.JOB_API_KEY:
            missing.append('JOB_API_KEY')
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def get_api_headers(cls):
        """Return headers for API requests"""
        return {
            'User-Agent': 'Tableau-Analytics-Extension-Job-Scraper/1.0',
            'Accept': 'application/json'
        }
    
    @classmethod
    def get_api_auth(cls):
        """Return authentication parameters for API requests (Jooble format)"""
        return {
            'key': cls.JOB_API_KEY
        }

# For backward compatibility and easy imports
API_KEY = Config.JOB_API_KEY
API_SECRET = Config.JOB_API_SECRET
API_BASE_URL = Config.JOB_API_BASE_URL