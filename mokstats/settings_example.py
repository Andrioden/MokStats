""" PART 1: Settings that are unique for each deployment 
------------------------------------------------------------
"""

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

PROJECT_DIR = "/srv/djangoapps/mokstatsapp/"
CACHE_DIR = "/tmp/mokstatscache"
DAILY_BACKUP_DIR = "C:/Filer/Dropbox/mokstats/backup/daily"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#COMPRESS_ENABLED = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mokstatsdb',                      # Or path to database file if using sqlite3.
        'USER': 'mokstats',                      # Not used with sqlite3.
        'PASSWORD': 'mokstats',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'yesitisunquieontheserverfucktard'

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

""" PART 2: General settings 
------------------------------------------------------------
"""

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Oslo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'no-bok'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = PROJECT_DIR+"static/"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/mokstats/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_DIR+"mokstats/static",
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

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware', #Uncomment to Activate Cache
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware', #Uncomment to Activate Cache
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mokstats.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'mokstats.wsgi.application'

# Absolute paths to folders to check for templates
TEMPLATE_DIRS = (
    PROJECT_DIR+"mokstats/templates"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'mokstats',
    'compressor',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_DIR,
        'TIMEOUT': 60*60*24*31 # 1 Month
    }
}
CACHE_MIDDLEWARE_SECONDS = 60*60*24*31 # 1 Month

COMPRESS_CSS_FILTERS = [
     'compressor.filters.css_default.CssAbsoluteFilter',
     'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = [
     'compressor.filters.jsmin.JSMinFilter'
]