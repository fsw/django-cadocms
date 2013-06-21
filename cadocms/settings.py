import socket, sys, pkgutil, os
from configurations import Settings as BaseSettings

import djcelery
djcelery.setup_loader()

class Settings(BaseSettings):
    
    @property
    def CADO_PROJECT(self):
        return os.path.basename(os.getcwd())
        #return os.path.basename((os.path.dirname(os.path.realpath(__file__))))
    
    CADO_NAME = 'Cado CMS'
    SECRET_KEY = 'OVERWRITE ME'
    
    SITE_ID = 1
    MULTISITE = False

    ADMINS = (
              ('Franciszek Szczepan Wawrzak', 'frank.wawrzak@cadosolutions.com'),
    )

    MANAGERS = ADMINS
    
    @property
    def DATABASES(self):
        #print 'XXXX'
        databases = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            }
        }
        
        databases['default'].update(self.HOST.DATABASE)
         
        #TODO                      
        #if 'test' in sys.argv:
        #    databases['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
        #print databases
        return databases
    
    
    CADO_DOMAIN = 'localhost' 
    
    @property
    def CADO_FULL_DOMAIN(self):
        if (self.HOST.CLASS == 'DEV'):
            return 'localhost:8000'
        else:
            return self.HOST.DOMAIN
        """
        elif (self.HOST.CLASS == 'TEST'):
            return self.HOST.CLASS.lower() + '.' + self.CADO_DOMAIN
        else:
            return self.CADO_DOMAIN
        """
    
    @property
    def CADO_PROJECT_GROUP(self):
        return self.CADO_PROJECT
     
    CADO_FLAVOURS = [
        ('desktop', 'Desktop Version', ''),
        ('mobile', 'Mobile Version', 'm.'),
        ('accessible', 'Accessible Version', 'ac.'),
    ]
    
    CRON_TASKS = []
    """
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake'
        }
    }
    """
    
    @property
    def DEBUG(self):
        return self.HOST.DEBUG
        
    @property
    def TEMPLATE_DEBUG(self):
        return self.DEBUG
    
    @property
    def EMAIL_BACKEND(self):
        if (self.HOST.CLASS == 'DEV'):
            return 'django.core.mail.backends.console.EmailBackend'
        return super(Settings, self).EMAIL_BACKEND
    
    TIME_ZONE = 'America/Chicago'
    
    LANGUAGE_CODE = 'en'
    
    LANGUAGES = (
        ('en', 'English'),
    )
    
    CADO_DEFAULT_LANGUAGE = 'en'
    CADO_LANGUAGES = ('en')
    
    USE_I18N = True
    USE_L10N = True
    
    USE_TZ = True
    
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'
    ADMIN_URL = '/admin/'
    
    
    @property
    def MEDIA_ROOT(self):
        if self.MULTISITE:
            return self.HOST.APPROOT + 'media/' + self.CADO_PROJECT + '/'
        else:
            return self.HOST.APPROOT + 'media/'
    
    @property
    def STATIC_ROOT(self):
        if self.MULTISITE:
            return self.HOST.APPROOT + 'static/' + self.CADO_PROJECT + '/'
        else:
            return self.HOST.APPROOT + 'static/'

    @property   
    def TEMPLATE_CONTEXT_PROCESSORS(self):
        return ("django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.request",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.core.context_processors.tz",
            "django.contrib.messages.context_processors.messages")

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
    )
    
    TEMPLATE_LOADERS = (
        'cadocms.loaders.flavour.Loader',
        'hamlpy.template.loaders.HamlPyFilesystemLoader',
        'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',  
    )

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'cadocms.middleware.Middleware',
        #'cadocms.middleware.Profiler',
        #'versioning.middleware.VersioningMiddleware',
    )
    
    @property
    def ROOT_URLCONF(self):
        return self.CADO_PROJECT +'.urls'
    
    @property
    def WSGI_APPLICATION(self):
        return 'cadocms.wsgi.application'
    
    @property
    def INSTALLED_APPS(self):
        #print 'INSTALLED_APPS cadocms'
        return (
            #'cadocms.db_prefix',
            self.CADO_PROJECT,
            'cadocms',
            'grappelli.dashboard',
            'grappelli',
            'filebrowser',
        ) + super(Settings, self).INSTALLED_APPS + (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admin',
            'reversion',
            'haystack',
            'south',
            'compressor',
            'mptt',
            'debug_toolbar',
            #'versioning',
            'captcha',
            'geoposition',
            'imagekit',
            'rosetta',
            'modeltranslation',
            'djcelery',
            'celery_haystack',
            #'kombu.transport.django', ## DEV ONLY
        )
        
    #BROKER_URL = 'django://'
    BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    
    CAPTCHA_FONT_SIZE = 25
    CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
    CAPTCHA_FILTER_FUNCTIONS = ('captcha.helpers.post_smooth',)
    CAPTCHA_LETTER_ROTATION = (-10,10)
    CAPTCHA_LENGTH = 6
    
    CONFIG_TEMPLATES_DIR = 'config'
    
    GRAPPELLI_INDEX_DASHBOARD = 'cadocms.dashboard.CustomIndexDashboard'

    INTERNAL_IPS = ('127.0.0.1',)
    
    
    HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
    
    @property
    def SOLR_CORE_NAME(self):
        return self.HOST.SOLR_CORE_NAME
        
    @property
    def SOLR_URL(self):
        return self.HOST.SOLR_URL
    
    @property
    def SOLR_PATH(self):
        return self.HOST.SOLR_PATH
    
    @property
    def SOLR_CORE_URL(self):
        return self.SOLR_URL + self.SOLR_CORE_NAME
        
    @property
    def SOLR_CORE_PATH(self):
        return self.SOLR_PATH + self.SOLR_CORE_NAME
    
    @property
    def HAYSTACK_CONNECTIONS(self):
        if self.HOST.CLASS != 'DEV':
            return {
                'default': {
                            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
                            'URL': self.SOLR_CORE_URL,
                            },
                }
        else:
            return {
                'default': {
                            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
                    },
                }
        
    
    @property
    def GRAPPELLI_ADMIN_TITLE(self):
        return self.CADO_NAME + ' Admin'
    
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', 'coffee --compile --stdio'),
        #('text/less', 'lessc {infile} {outfile}'),
        #('text/x-sass', 'sass {infile} {outfile}'),
        #('text/x-scss', 'sass --scss {infile} {outfile}'),
        #('text/stylus', 'stylus < {infile} > {outfile}'),
        ('text/x-scss', 'cadocms.filters.SassFilter'),
    )

    COMPRESS_PARSER = 'compressor.parser.HtmlParser' 
    
    @property
    def COMPRESS_ENABLED(self):
        return (self.HOST.CLASS != 'DEV')
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS' : False
    }
    """
    DEBUG_TOOLBAR_PANELS = (
      'debug_toolbar.panels.version.VersionDebugPanel',
      'debug_toolbar.panels.timer.TimerDebugPanel',
      'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    )
    TINYMCE_DEFAULT_CONFIG = {
            'plugins': "table,paste,searchreplace,preview",
            'theme': "advanced",
            'cleanup_on_startup': True,
            'custom_undo_redo_levels': 10,
            'theme_advanced_resizing': True,
            'content_css': STATIC_URL + 'content.css',
            'body_class': 'content',
            'height': 400,
    }
    """

    @property
    def HOST(self):
        if not hasattr(self, '_HOST'):
            host_name = socket.gethostname()
            host_srcroot = os.getcwd() + '/'
            #package = pkgutil.get_loader(self.__class__.__module__)
            #srcroot = os.path.dirname(os.path.dirname(package.filename))
            CurrentHostSettingsClass = DevHostSettings
            found = False
            for HostSettingsClass in HostSettings.__subclasses__():
                if HostSettingsClass.NAME == host_name and HostSettingsClass.SRCROOT == host_srcroot:
                    CurrentHostSettingsClass = HostSettingsClass
                    found = True
            #if not found:
                #print 'THIS SEEMS LIKE A DEV SERVER'
            self._HOST = CurrentHostSettingsClass(self)
            
        return self._HOST
    
    @property
    def SITES(self):
        return [self]

class MultiAppSettings(Settings):
    
    MULTISITE = True
    
    @property
    def SITES(self):
        if not hasattr(self, '_SITES'):
            sites = []
            #if os.environ.get("CADO_SITES", "").split(";"):
            for name in os.listdir(os.getcwd()):
                if os.path.isdir(os.path.join(os.getcwd(), name)):
                    if os.path.isfile(os.path.join(os.getcwd(), name, 'settings.py')):
                        if not name + '.settings' == os.environ["DJANGO_SETTINGS_MODULE"]:
                            sites.append(name)
            self._SITES = []
            for site in sites:
                _temp = __import__(site + '.settings', globals(), locals(), ['Settings'], -1) 
                self._SITES.append(_temp.Settings())
                
            #else:
            #    self._SITES = [self]
                
        return self._SITES
    """
    @property
    def DB_PREFIX(self):
        return self.CADO_PROJECT + '_'
    """

class HostSettings(object):
    def __init__(self, parent):
        self.SETTINGS = parent
        
    PYTHON_PREFIX = "~/virtualenv/bin/"
    SOLR_URL = 'http://127.0.0.1:8080/solr/'
    SOLR_PATH = '/opt/solr/'
    @property
    def SOLR_CORE_NAME(self):
        return self.SETTINGS.CADO_PROJECT
    
    @property
    def DEBUG(self):
        return (self.CLASS == 'DEV') or (self.CLASS == 'TEST')

class DevHostSettings(HostSettings):
    """
    SOLR_PATH = ''
    SOLR_URL = ''
    SOLR_CORE_NAME = ''
    """
    CLASS = 'DEV'
    NAME = 'localhost'
    DOMAIN = 'localhost:8000'
    HOST_STRING = 'localhost'
    SRCROOT = os.getcwd() + '/'
    APPROOT = os.getcwd() + '/data/'
    DATABASE = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME' : 'data/local.db3'
                }

