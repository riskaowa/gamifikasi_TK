import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # SECRET_KEY MUST be set in environment for security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Fallback untuk development - WARNING untuk production
        import warnings
        warnings.warn(
            "SECRET_KEY not set in environment. Using default development key. "
            "Set SECRET_KEY environment variable for production!",
            RuntimeWarning
        )
        SECRET_KEY = 'dev-key-change-in-production'
    
    # DEBUG should be explicitly set in environment (defaults to False for security)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Application timezone used for access-time checks. Change if server is in different TZ.
    APP_TZ = os.environ.get('APP_TZ') or 'Asia/Jakarta'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
