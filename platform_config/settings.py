from pathlib import Path
import os # ponechaj tento import pre staršie nastavenia (STATICFILES_DIRS)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# ... (ostatné nastavenia) ...

SECRET_KEY = 'django-insecure-+dhfx2*iln_b7bhm*l6sy$7==+fbmsr5*52+i9l&-mv+92p-nk'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # 1. Tvoja aplikácia 'core' musí byť prvá, aby prebila Admin šablóny!
    'core', 
    'django.contrib.admin', # Presunuli sme ho dole
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'platform_config.urls'

# --- TEMPLATES (OPRAVENÁ JEDNA SEKCIA) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        
        # ✅ OPRAVA DIRS: Smeruje na hlavný templates/ priečinok
        'DIRS': [BASE_DIR / 'templates'],
        
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # Pridávam debug, pre istotu
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Tvoj custom processor:
                'core.context_processors.notifikacie_processor', 
            ],
        },
    },
]
# --- KONIEC TEMPLATES ---


WSGI_APPLICATION = 'platform_config.wsgi.application'


# Database
# ... (zvyšok databázy) ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# ... (zvyšok password validation) ...

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# ... (zvyšok i18n) ...

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Využívame os.path.join pre kompatibilitu so starším BASE_DIR, ak je to potrebné
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_REDIRECT_URL = '/' 
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# Nastavenia pre e-mail resetu hesla
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'support@tvojaplatforma.sk'