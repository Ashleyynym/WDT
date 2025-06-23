import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Database Configuration
    if os.environ.get('DATABASE_URL'):
        # Google Cloud SQL (Production)
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # Local SQLite (Development)
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'wdt_supplychain.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Cloud SQL specific settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': 300,
        'max_overflow': 20
    }
    
    # Babel Configuration
    LANGUAGES = ['en', 'es', 'fr', 'de', 'zh']
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application Settings
    POSTS_PER_PAGE = 25
    ADMINS = ['admin@wdt.com']
    
    # Timezone Configuration
    DEFAULT_TIMEZONE = os.environ.get('DEFAULT_TIMEZONE', 'UTC')
    
    # Audit Logging
    AUDIT_LOG_ENABLED = os.environ.get('AUDIT_LOG_ENABLED', 'true').lower() == 'true'
    
    # Job Scheduler
    SCHEDULER_ENABLED = os.environ.get('SCHEDULER_ENABLED', 'true').lower() == 'true'
    
    # Google Cloud SQL Connection Pool
    if os.environ.get('DATABASE_URL'):
        # Production database settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
            'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 20)),
            'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 300)),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
            'connect_args': {
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30
            }
        }

    # Babel (i18n) settings
    BABEL_SUPPORTED_LOCALES = ["en", "zh"]

    # Session lifetime (example)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
