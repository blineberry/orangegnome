"""
Django settings for orangegnome project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import environ
import os

env = environ.Env(
    DEBUG=(bool, False),
    SECURE_SSL_REDIRECT=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool,False),
    SECURE_HSTS_SECONDS=(int,0),
)

environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
#DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition

INSTALLED_APPS = [
    'bookmarks.apps.BookmarksConfig',
    'photos.apps.PhotosConfig',
    'exercises.apps.ExercisesConfig',
    'notes.apps.NotesConfig',
    'syndications.apps.SyndicationsConfig',
    'base.apps.BaseConfig',
    'feed.apps.FeedConfig',
    'pages.apps.PagesConfig',
    'profiles.apps.ProfilesConfig',
    'posts.apps.PostsConfig',
    'webmentions.apps.WebmentionsConfig',
    'likes.apps.LikesConfig',
    'reposts.apps.RepostsConfig',
    'django_sass',
    'django.contrib.admin',
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

ROOT_URLCONF = 'orangegnome.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'profiles.context_processors.owner',
                'base.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'orangegnome.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = True

SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
CSRF_TRUSTED_ORIGINS = ["https://orangegnome.com"]
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

#STATIC_URL = '/static/'
STATIC_URL = 'https://assets.orangegnome.com/orangegnome.com/static/'
#MEDIA_URL = '/media/'
MEDIA_URL = 'https://assets.orangegnome.com/orangegnome.com/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, env('MEDIA_ROOT_PATH'))
STATIC_ROOT = os.path.join(BASE_DIR, env('STATIC_ROOT_PATH'))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, env('MEDIA_ROOT_PATH')),
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Twitter Settings
TWITTER_CONSUMER_KEY = env('TWITTER_API_KEY')
TWITTER_CONSUMER_SECRET = env('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN_KEY = env('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = env('TWITTER_V2_ACCESS_TOKEN_SECRET')
TWITTER_ID_STR = env('TWITTER_ID_STR')
TWITTER_NAME = env('TWITTER_NAME')
TWITTER_SCREEN_NAME = env('TWITTER_SCREEN_NAME')

# Mastodon Settings
MASTODON_INSTANCE = env('MASTODON_INSTANCE')
MASTODON_ACCESS_TOKEN = env('MASTODON_ACCESS_TOKEN')

# Azure Blob Storage Settings
AZURE_PUBLIC_ACCOUNT_NAME = env("AZURE_PUBLIC_ACCOUNT_NAME")
AZURE_PUBLIC_ACCOUNT_KEY = env("AZURE_PUBLIC_ACCOUNT_KEY")
AZURE_PUBLIC_CONTAINER = env("AZURE_PUBLIC_CONTAINER")

# Site Settings
SITE_NAME = "Orange Gnome"
SITE_URL = env('SITE_URL')

DEFAULT_AUTO_FIELD='django.db.models.AutoField'
