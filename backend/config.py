import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_HOST     = os.getenv('DB_HOST', 'localhost')
    DB_PORT     = int(os.getenv('DB_PORT', 3306))
    DB_NAME     = os.getenv('DB_NAME', 'walkin_platform')
    DB_USER     = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # JWT
    JWT_SECRET       = os.getenv('JWT_SECRET', 'change-me')
    JWT_EXPIRY_HOURS = 24

    # SMTP
    SMTP_HOST     = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT     = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER     = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    # Groq
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL   = os.getenv('GROQ_MODEL', 'llama3-8b-8192')

    # App
    DEBUG        = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT         = int(os.getenv('PORT', 5000))
    FRONTEND_URL = os.getenv('FRONTEND_URL', '*')