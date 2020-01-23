import os
import sys
from messages.script import FolderScript
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_BASE = os.path.join(BASE_DIR, 'media')

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
FILE_PATH = os.path.join(BASE_DIR, 'SourceNumberSets.txt')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'gns0!4y#pfda5b79yw-3*&qfsvxgrdneghi38(#7b!zk*k^e+b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)
RUNNING_IP = config('RUNNING_IP')
PROJECT_PATH = os.path.abspath(".")

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_swagger',
    'apps.bandwidth.apps.BandwidthConfig',
    'apps.message.apps.MessageConfig',
    'apps.four_authentication.apps.FourAuthenticationConfig',
    'apps.okta.apps.OktaConfig'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.okta.middleware.OktaMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    # ),
    'DEFAULT_PAGINATION_CLASS': 'bandwidth.pagination.oa_pagination.CustomResultsSetPagination'
}

ROOT_URLCONF = 'messages.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'messages.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', cast=str),
        'NAME': config('DATABASE_NAME', cast=str),
        'USER': config('DATABASE_USER', cast=str),
        'PASSWORD': config('DATABASE_PASSWORD', cast=str),
        'HOST': config('DATABASE_HOST', cast=str),
        'PORT': config('DATABASE_PORT', cast=str),
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 'charset': 'utf8mb4'},
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_ROOT = os.path.join(MEDIA_ROOT, 'file')
FILE_URL = '/file/'

FolderScript(MEDIA_ROOT)
FolderScript(FILE_ROOT)

SMS_CALLBACKURL = config('SMS_CALLBACKURL', cast=str)
CUSTOM_SMS_CALLBACKURL = config('CUSTOM_SMS_CALLBACKURL', cast=str)

# START email config
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
# END email config


LOG_ENABLED = True

# =========================== LOGGING CONFIGURATION START ==============================
MESSAGE_APPS = [
    'bandwidth',
    'message'
]

import logging.config

LOG_DIRECTORY = PROJECT_PATH + "/log/"
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

LOGGING_CONFIG = None

app_loggers = {app_name: {
    'handlers': ['console_dev', 'log_file_production_warning', 'log_file_production_error', 'mail_admins'],
    'level': 'INFO',
    'propagate': True,
} for app_name in MESSAGE_APPS}

app_loggers['django'] = {
    'handlers': ['console_dev', 'log_file_production_warning', 'log_file_production_error', 'mail_admins'],
    'propagate': True,
    'level': 'WARNING',
}

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'log_file_dev': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIRECTORY + "dev_log.log",
            'maxBytes': 50000,
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log_file_production_warning': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIRECTORY + "prd_log.log",
            'maxBytes': 50000,
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'log_file_production_error': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIRECTORY + "prd_log.log",
            'maxBytes': 50000,
            'backupCount': 20,
            'formatter': 'verbose',
        },
        'console_dev': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'formatters': {
        'file': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'default': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
        'print_message': {
            'format': '%(message)s'
        }
    },
    'loggers': app_loggers
})

# =========================== LOGGING CONFIGURATION END ==============================


BANDWIDTH_API_TOKEN = config('BANDWIDTH_API_TOKEN', cast=str)
BANDWIDTH_API_SECRETE_KEY = config('BANDWIDTH_API_SECRETE_KEY', cast=str)
BANDWIDTH_AUTHORIZATION = config('BANDWIDTH_AUTHORIZATION', cast=str)

# OKTA Config
OKTA_CLIENT_ID = config('OKTA_CLIENT_ID', cast=str)
REDIRECT_URL = config('REDIRECT_URL', cast=str)
API_TOKEN = config('API_TOKEN', cast=str)
GROUP_ID = config('GROUP_ID', cast=str)
OKTA_BASE_URL = config('OKTA_BASE_URL', cast=str)

OKTA_CLIENT_SECRET = config('OKTA_CLIENT_SECRET', cast=str)
# id.familynet
OKTA_STATE = config('OKTA_STATE', cast=str)

MESSAGE_URL = config('MESSAGE_URL', cast=str)
THUMBNAIL_SIDE_LIMIT = config('THUMBNAIL_SIDE_LIMIT', cast=int)

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', cast=str)
AWS_SECRET_ACCESS_KEY_ID = config('AWS_SECRET_ACCESS_KEY_ID', cast=str)
MESSAGE_BUCKET_NAME = config('MESSAGE_BUCKET_NAME', cast=str)
