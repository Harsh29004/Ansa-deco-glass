import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # ID Card
    IDCARD_VALIDITY_DAYS = int(os.getenv('IDCARD_VALIDITY_DAYS', 365))
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'ANSA Deco Glass')
    COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS', 'Manufacturing Unit, Industrial Area')
    COMPANY_LOGO = os.getenv('COMPANY_LOGO', 'static/images/COMPANY_LOGO.png')

    # Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Login Credentials
    HR_USERNAME = os.getenv('HR_USERNAME', 'hr_admin')
    HR_PASSWORD = os.getenv('HR_PASSWORD', 'hr@123')
    MEDICAL_USERNAME = os.getenv('MEDICAL_USERNAME', 'medical_admin')
    MEDICAL_PASSWORD = os.getenv('MEDICAL_PASSWORD', 'medical@123')
    SAFETY_USERNAME = os.getenv('SAFETY_USERNAME', 'safety_admin')
    SAFETY_PASSWORD = os.getenv('SAFETY_PASSWORD', 'safety@123')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin@123')
    
    # Directories
    CONTRACTOR_SIGNATURES_DIR = os.path.join(UPLOAD_FOLDER, 'contractor_signatures')
    EMPLOYEE_PHOTOS_DIR = os.path.join(UPLOAD_FOLDER, 'employee_photos')
    EMPLOYEE_SIGNATURES_DIR = os.path.join(UPLOAD_FOLDER, 'employee_signatures')
    APPROVAL_SIGNATURES_DIR = os.path.join(UPLOAD_FOLDER, 'approval_signatures')
    IDCARDS_DIR = os.path.join(UPLOAD_FOLDER, 'idcards')
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        directories = [
            Config.UPLOAD_FOLDER,
            Config.CONTRACTOR_SIGNATURES_DIR,
            Config.EMPLOYEE_PHOTOS_DIR,
            Config.EMPLOYEE_SIGNATURES_DIR,
            Config.APPROVAL_SIGNATURES_DIR,
            Config.IDCARDS_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
