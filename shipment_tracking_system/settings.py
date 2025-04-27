from pathlib import Path
import os
import dj_database_url  # ✅ Make sure this is installed

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: Keep secret in environment variables!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-secret-for-dev')

# Debug mode
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allowed Hosts
RENDER_HOST = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'tracking',  # Your app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'shipment_tracking_system.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tracking/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'shipment_tracking_system.wsgi.application'

# Database (Auto-detect: PostgreSQL on Render, SQLite locally)
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600,  # persistent connection
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise static compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication Redirect
LOGIN_URL = '/login/'

# Mailgun Settings
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
MAILGUN_BASE_URL = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}'
FROM_EMAIL = 'Naiyuan Mart <noreply@shipping.naiyuanmart.com>'

# Twilio Settings
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

# 🚀 Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
