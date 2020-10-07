import environ
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env_file_path = '/server/.env'
if os.path.isfile(env_file_path):
    env.read_env(env_file_path)

SECRET_KEY = env.str('SECRET_KEY', default='secret-key')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'admin_ordering',
    'ckeditor',
    'tags',
    'resources',
    'patients'
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

ROOT_URLCONF = 'app.urls'

template_directories = [
    'templates'
]
if os.path.isdir('/take-on-transplant/compiled-templates'):
    template_directories.insert(0,'/take-on-transplant/compiled-templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': template_directories,
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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': env.db(),
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tempdb',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Media settings from django-storages & Amazon S3
# https://github.com/jschneier/django-storages
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
aws_bucket_name = os.environ.get('AWS_BUCKET_NAME', False)
aws_access_key = os.environ.get('AWS_ACCESS_KEY', default=False)
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', default=False)
if aws_bucket_name and aws_access_key and aws_secret_access_key:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = aws_bucket_name
    AWS_ACCESS_KEY_ID = aws_access_key
    AWS_SECRET_ACCESS_KEY = aws_secret_access_key
    # FOR CKEDITOR https://django-ckeditor.readthedocs.io/en/latest/#using-s3
    AWS_QUERYSTRING_AUTH = False
MEDIA_URL = '/media/'
MEDIA_ROOT = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static'

if os.path.isdir('/take-on-transplant/dist'):
    STATICFILES_DIRS = [
        '/take-on-transplant/dist'
    ]

# Email Settings
if 'SENDGRID_API_KEY' in os.environ:
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_API_KEY']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

LOGIN_REDIRECT_URL = '/login/'
