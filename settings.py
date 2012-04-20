# Django settings for djwed project.

from socket import gethostname
production = False

# This is the production hostname (as I'd develop on a desktop and then run
# the system on a colo server.)
if 'my-colo-server' == gethostname().split(".")[0]:
    production = True

if not production:
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Ben Bitdiddle', 'benb@example.org'),
)

MANAGERS = (
     ('Ben Bitdiddle', 'benb@example.org'),
     ('Alyssa P Hacker', 'aphacker@example.org'),
)

# Default From email address used by djwed when sending emails, with a display
# name as well
FROM_EMAIL = ('Alyssa & Ben', 'ab@example.org')

# Default From email address used by Django when sending emails
DEFAULT_FROM_EMAIL = FROM_EMAIL[1]

WEDDING_NAMES = 'Alyssa and Ben'

# By keeping the database in a sqlite3 file, I was able to check it into
# subversion and easily make copies to the staging environment.
# The performance of sqlite3 was just fine for a single-wedding environment
# as this was intended for.
DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.

# Path to base of code, as well to database file if using sqlite3.
# Change these file paths as appropriate.
if production:
    WEDDING_BASE = '/www/wedding'       
    DATABASE_NAME = WEDDING_BASE + '/data/weddingdata.sqlite'
else:
    WEDDING_BASE = '/u/media/project/wedding/website/djwed'
    DATABASE_NAME = WEDDING_BASE + '/data/weddingdata-test.sqlite'


DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = 'localhost'
if production:
    SEND_EMAIL = True
    EMAIL_PORT = 25
else:
    SEND_EMAIL = False
    EMAIL_PORT = 1025
    

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Authentication backend classes (as strings) to use when attempting to authenticate a user.
AUTHENTICATION_BACKENDS = (
    'djwed.wedding.auth.InviteeAuthBackend',
    'django.contrib.auth.backends.ModelBackend'
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = WEDDING_BASE + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
if production:
    MEDIA_URL = 'http://wedding.example.org/media/'
else:
    MEDIA_URL = 'http://localhost:8000/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'CHANGE_ME_TO_SOME_OTHER_RANDOM_STRING!!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Needs to be at the end
    'django.contrib.csrf.middleware.CsrfMiddleware',
)

ROOT_URLCONF = 'djwed.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    WEDDING_BASE + '/templates/',
    WEDDING_BASE + '/photologue/templates/photologue/templates/',
    WEDDING_BASE + '/photologue/templates/',
    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    #"django.contrib.messages.context_processors.messages"
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'djwed.wedding',
    'tagging',
    'photologue',
)


