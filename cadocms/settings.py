import socket, sys, pkgutil, os, inspect
from configurations import Settings as BaseSettings
from cadocms.management import commands_requiring_site

import djcelery
djcelery.setup_loader()

def allways_show_toolbar(request):
    return True

def never_show_toolbar(request):
    return False

class Settings(BaseSettings):
    
    @property
    def CADO_PROJECT(self):
        return os.path.basename(os.path.dirname(os.path.realpath(inspect.getfile(self.__class__))))
        #return os.path.basename(os.getcwd())
        #return os.path.basename((os.path.dirname(os.path.realpath(__file__))))
    
    CADO_NAME = 'Cado CMS'
    SECRET_KEY = 'OVERWRITE ME'
    
    REBOOT_TIME = '10 3' 
    
    SPAM_EMAIL = '' 
    SITE_ID = 1
    MULTISITE = False

    MODELTRANSLATION_ENABLE_REGISTRATIONS = True

    BOOTSTRAP_THEME = 'bootstrap' 
    
    CADO_EXTRA_ADMIN_LINKS = []

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
            if self.MULTISITE:
                if (self.HOST.CLASS == 'TEST'):
                    return 'test.' + self.CADO_DOMAIN
                else:
                    return self.CADO_DOMAIN
            else:
                return self.HOST.DOMAIN
        """
        elif (self.HOST.CLASS == 'TEST'):
            return self.HOST.CLASS.lower() + '.' + self.CADO_DOMAIN
        else:
            return self.CADO_DOMAIN
        """
    
    @property
    def CADO_FULL_URL(self):
        return 'http://' + self.CADO_FULL_DOMAIN;
    
    
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
    def CACHES(self):
        if (self.HOST.CLASS == 'DEV'):
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
                    'LOCATION': '/tmp/django_cache',
                }
            }
        else:
            return {
                'default': {
                    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                    'LOCATION': 'unix:/tmp/memcached.sock',
                    'PREFIX': self.HOST.DEPLOY_HASH + self.HOST.DATABASE['NAME'],
                }
            }
    
    @property
    def CACHE_PREFIX(self):
        return self.HOST.DEPLOY_HASH + self.HOST.DATABASE['NAME']
        
    
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    
    @property
    def DEBUG(self):
        return self.HOST.DEBUG
    
    @property
    def CAPTCHA_TEST_MODE(self):
        return self.DEBUG
    
    @property
    def TEMPLATE_DEBUG(self):
        return self.DEBUG
    
    @property
    def EMAIL_BACKEND(self):
        if (self.HOST.CLASS == 'DEV'):
            return 'django.core.mail.backends.console.EmailBackend'
        return super(Settings, self).EMAIL_BACKEND
    
    TIME_ZONE = 'America/Chicago'
    
    CADO_DEFAULT_LANGUAGE = 'en'
    CADO_LANGUAGES = (
        ('en', 'English'),
    )
    CADO_L10NURLS = False
    
    @property
    def LANGUAGE_CODE(self):
        return self.CADO_DEFAULT_LANGUAGE
    
    #@property
    #def LANGUAGES(self):
    #    return self.CADO_LANGUAGES
    
    @property
    def LANGUAGES(self):
        ret = dict()
        for site in self.SITES_SETTINGS:
            for c,n in site.CADO_LANGUAGES:
                ret[c] = n
        #print 'LANG', ret
        return ret.items()
    
    @property
    def USE_I18N(self):
        return len(self.LANGUAGES) > 1

    USE_L10N = True
    
    USE_TZ = True
    
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'
    ADMIN_URL = '/admin/'
    
    STATICPAGE_TEMPLATES = (
        ('base.html', 'Default')
    )
    
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

    @property   
    def MIDDLEWARE_CLASSES(self):
        ret = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'cadocms.middleware.Middleware',
                'cadocms.middleware.StaticPagesFallback',
                #'cadocms.middleware.Profiler',
                #'versioning.middleware.VersioningMiddleware',
                )
        if (self.HOST.CLASS != 'PROD'):
            ret = ret + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
        return ret;
    
    #@property
    #def ROOT_URLCONF(self):
    #    return self.CADO_PROJECT +'.urls'
    
    @property
    def WSGI_APPLICATION(self):
        return 'cadocms.wsgi.application'
    
    @property
    def INSTALLED_APPS(self):
        #print 'INSTALLED_APPS cadocms'
        ret = (
            #'cadocms.db_prefix',
            self.CADO_PROJECT,
            'cadocms',
            'grappelli.dashboard',
            'grappelli',
            'filebrowser',
        #) + super(Settings, self).INSTALLED_APPS + (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admin',
            'django.contrib.humanize',
            'reversion',
            'haystack',
            'south',
            'compressor',
            'mptt',
            #'versioning',
            'captcha',
            'geoposition',
            'imagekit',
            'rosetta',
            'modeltranslation',
            'djcelery',
            'celery_haystack',
            'django_extensions',
            'ajax_upload',
            #'kombu.transport.django', ## DEV ONLY
        )
        if (self.HOST.CLASS != 'PROD'):
            ret = ret + ('debug_toolbar',)
            
        return ret;
        
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

    #COMPRESSOR SETTINGS
        
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

    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter'    
        ]

    COMPRESS_DEBUG_TOGGLE = None
    
    COMPRESS_CACHE_KEY_FUNCTION = 'cadocms.compressor.cado_cachekey'
    
    @property
    def LOGGING(self):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s %(message)s'
                },
            },
            'filters': {
                'require_debug_false': {
                    '()': 'django.utils.log.RequireDebugFalse'
                }
            },
            'handlers': {
                'mail_admins': {
                    'level': 'ERROR',
                    'filters': [],#'require_debug_false'],
                    'class': 'django.utils.log.AdminEmailHandler'
                },
                'logfile': {
                    'level':'DEBUG',
                    'class':'logging.handlers.RotatingFileHandler',
                    'filename': self.HOST.APPROOT + "django.log",
                    'maxBytes': 50000,
                    'backupCount': 5,
                    'formatter': 'verbose'
                },
            },
            'loggers': {
                'django.request': {
                    'handlers': ['mail_admins'],
                    'level': 'ERROR',
                    'propagate': True,
                },
                'logfile': {
                    'handlers': ['logfile'],
                    'level': 'DEBUG',
                },
                'pysolr': {
                    'handlers': ['logfile'],
                    'level': 'DEBUG',
                },
            }
        }
    
    @property
    def DEBUG_TOOLBAR_CONFIG(self):
        return {
                'INTERCEPT_REDIRECTS' : False,
                'SHOW_TOOLBAR_CALLBACK': 'cadocms.settings.allways_show_toolbar' if self.DEBUG else 'cadocms.settings.never_show_toolbar',
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
    
    @property
    def ALLOWED_HOSTS(self):
        return [self.CADO_FULL_DOMAIN]
    
    @property
    def BACKUP_DIR(self):
        return self.HOST.BACKUP_DIR
    
    EXTRA_URLCONFS = []
    EXTRA_URLS = []
    ROOT_URLCONF = 'cadocms.urls'

    @property
    def SITES_SETTINGS(self):
        yield self
        
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
    
    @property
    def SITES_SETTINGS(self):
        for settings in self.SITES:
            yield settings
        #for SettingsClass in MultiAppSettings.__subclasses__():
        #    yield SettingsClass()
        
    """
    @property
    def DB_PREFIX(self):
        return self.CADO_PROJECT + '_'
    
"""

def get_management_command(settings, command):
    if settings.MULTISITE and command in commands_requiring_site:
        return "%spython manage.py %s %s" % (settings.HOST.PYTHON_PREFIX, command, settings.CADO_PROJECT)
    else:
        return "%spython manage.py %s" % (settings.HOST.PYTHON_PREFIX, command)
        
    
class HostSettings(object):
    def __init__(self, parent):
        self.SETTINGS = parent
    
    #this should be overwritten durring deploy to random string.copy this to project settings!
    DEPLOY_HASH = "XXAUTODEPLOYHASHXX";

    PYTHON_PREFIX = "~/virtualenv/bin/"
    SOLR_URL = 'http://127.0.0.1:8080/solr/'
    SOLR_PATH = '/opt/solr/'
    SRCROOT = None
    APPROOT = None
    
    HTTPS_ON = False
    
    @property
    def SOLR_CORE_NAME(self):
        return self.SETTINGS.CADO_PROJECT
    
    @property
    def BACKUP_DIR(self): 
        return self.APPROOT + "backup/"
    
    @property
    def DEBUG(self):
        return (self.CLASS == 'DEV') or (self.CLASS == 'TEST')

class DevHostSettings(HostSettings):
    """
    SOLR_PATH = ''
    SOLR_URL = ''
    SOLR_CORE_NAME = ''
    """
    PYTHON_PREFIX = ''
    CLASS = 'DEV'
    NAME = 'localhost'
    DOMAIN = 'localhost:8000'
    HOST_STRING = 'localhost'
    SRCROOT = os.getcwd() + '/'
    APPROOT = os.getcwd() + '/data/'
    @property
    def DATABASE(self):
        if 'django.contrib.gis' in self.SETTINGS.INSTALLED_APPS:
            return {
                    'ENGINE': 'django.contrib.gis.db.backends.spatialite',
                    'NAME' : self.APPROOT + 'local.db3'
                    }
        return {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME' : self.APPROOT + 'local.db3'
                }

