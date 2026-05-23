# project/config.py

import os

from core.env import load_dotenv_files
from core.config import _get_bool_env as _get_bool_env_var
from core.config import _normalize_database_url

# Load .env before class-level os.environ reads.
load_dotenv_files()

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, os.pardir))
local_data_dir = os.path.join(project_root, 'local_data')


class BaseConfig(object):
    """Base configuration (values from ``.env.<APP_ENV>``)."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'my_precious')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'my_precious_two')
    DEBUG = _get_bool_env_var('DEBUG', False)
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://:@127.0.0.1:6379/0')
    DAY_FILE_PATH = os.environ.get('DAY_FILE_PATH', os.path.join(local_data_dir, 'day_data'))
    RESULT_PATH = os.environ.get('RESULT_PATH', os.path.join(local_data_dir, 'results'))
    INDEX_FILE_PATH = os.environ.get('INDEX_FILE_PATH', os.path.join(local_data_dir, 'index_data'))
    READ_ANALYSIS_FROM_DB = _get_bool_env_var('READ_ANALYSIS_FROM_DB', True)
    CSV_DEV_FALLBACK = _get_bool_env_var('CSV_DEV_FALLBACK', False)

    MAIL_SERVER = os.environ.get('APP_MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('APP_MAIL_PORT', 465))
    MAIL_USE_TLS = _get_bool_env_var('APP_MAIL_USE_TLS', False)
    MAIL_USE_SSL = _get_bool_env_var('APP_MAIL_USE_SSL', True)
    MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('APP_MAIL_DEFAULT_SENDER', 'from@example.com')
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get('DATABASE_URL'))

    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')


class DevelopmentConfig(BaseConfig):
    """Development configuration (set ``APP_ENV=development`` in ``.env.development``)."""
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True


class LocalConfig(BaseConfig):
    """Local developer configuration (``APP_ENV=local`` → ``.env.local``)."""
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True
    CSV_DEV_FALLBACK = _get_bool_env_var('CSV_DEV_FALLBACK', False)
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI or (
        'sqlite:///' + os.path.join(local_data_dir, 'twelvewin.sqlite')
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    LOGIN_DISABLED = False
    TESTING = True
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(BaseConfig):
    """Production configuration (``APP_ENV=production`` → ``.env.production``)."""
    DEBUG_TB_ENABLED = False
    WTF_CSRF_ENABLED = True
