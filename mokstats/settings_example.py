""" PART 1: Settings that are unique for each deployment 

"""

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = False

PROJECT_DIR = "C:/projects/untitledgame/"
LOG_FILE = "C:/temp/djangolog/untitledgame.log"
# If the site is hosted under www.domain.com/untitledgame/ the prefix has
# to be "/untitledgame", no trailing slash
PROJECT_URL_PREFIX = ''

ALLOWED_HOSTS = ["127.0.0.1"]

ADMINS = (
    ('Andre S. Hansen', 'andresh@tihlde.org'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'untitledgamedb',                      # Or path to database file if using sqlite3.
        'USER': 'untitledgame',                      # Not used with sqlite3.
        'PASSWORD': 'untitledgame',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

MONITOR_VERSION = 0

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@@zdevgog5bk-d-palj726zx)eg=@ll6)^)dwc65c)*46tlu4j'

"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 60*60, # 1 Hour
        'OPTIONS': {
            'MAX_ENTRIES': 2000
        }
    }
}
"""

""" PART 2: General settings 

"""

MANAGERS = ADMINS

LOGIN_URL = PROJECT_URL_PREFIX+'/account/login/'
STATIC_URL = PROJECT_URL_PREFIX+'/static/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Oslo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = PROJECT_DIR+"static/"

#Custom made
STATIC_MEDIA = PROJECT_DIR+'static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_DIR+"account/static",
    PROJECT_DIR+"game/static",
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'monitor.middleware.TimeMonitorMiddleware'
)

ROOT_URLCONF = 'untitledgame.urls'

TEMPLATE_DIRS = (
    PROJECT_DIR+"untitledgame/templates"
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'south',
    "compressor",
    # Self made
    'game',
    'monitor',
    'account',
    'social',
)

APPEND_SLASH = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': []
        },
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILE,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null', 'logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        
        #'myproject.custom': {
        #    'handlers': ['console', 'mail_admins', 'logfile'],
        #    'level': 'INFO',
        #}
    }
}

COMPRESS_CSS_FILTERS = [
     'compressor.filters.css_default.CssAbsoluteFilter',
     'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
     'compressor.filters.jsmin.JSMinFilter'
]