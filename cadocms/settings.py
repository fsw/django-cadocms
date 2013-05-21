import socket, sys, pkgutil, os
from configurations import Settings as BaseSettings

class Settings(BaseSettings):
    
    CADO_NAME = 'Cado CMS'
    
    @property
    def PROJECT_ROOT(self):
        package = pkgutil.get_loader(self.__class__.__module__)
        return os.path.dirname(os.path.dirname(package.filename))

    @property
    def CONFIG_GEN_GENERATED_DIR(self):
        return os.path.join(self.PROJECT_ROOT, 'config')

    ADMINS = (
              ('Franciszek Szczepan Wawrzak', 'frank.wawrzak@cadosolutions.com'),
    )

    MANAGERS = ADMINS
    
    def getCurrentEnvironment(self):
        name = socket.gethostname().split('.', 1)[0].replace('-', '_')
        package = pkgutil.get_loader(self.__class__.__module__)
        home = os.path.dirname(os.path.dirname(package.filename))
        for key, environments in self.CADO_ENVIRONMENTS.items():
            for environment_name, environment_home, environment_root in environments:
                if (name == environment_name) and (home == environment_home):
                    return {
                        'type' : key,
                        'name' : environment_name,
                        'home' : environment_home,
                        'root' : environment_root,
                    }
        return {
            'type' : 'DEV',
            'name' : name,
            'home' : home,
            'root' : '',
        }
        
    def getCurrentEnvironmentType(self):
        return self.getCurrentEnvironment()['type']

    def getCurrentEnvironmentRoot(self):
        return self.getCurrentEnvironment()['root']
    
    def getCurrentEnvironmentName(self):
        return self.getCurrentEnvironment()['name']
    
    def getCurrentEnvironmentHome(self):
        return self.getCurrentEnvironment()['home']
    
    @property
    def DATABASES(self):
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
        
        databases['default'].update(self.CADO_DATABASES[self.getCurrentEnvironmentType()])
                               
        if 'test' in sys.argv:
            databases['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
        
        return databases
    
    @property
    def DEBUG(self):
        return (self.getCurrentEnvironmentType() == 'DEV') or (self.getCurrentEnvironmentType() == 'TEST') 
        
    @property
    def TEMPLATE_DEBUG(self):
        return self.DEBUG
    
    @property
    def EMAIL_BACKEND(self):
        if (self.getCurrentEnvironmentType() == 'DEV'):
            return 'django.core.mail.backends.console.EmailBackend'
        return super(Settings, self).EMAIL_BACKEND
    
    TIME_ZONE = 'America/Chicago'
    
    LANGUAGE_CODE = 'en-us'
    
    USE_I18N = True
    USE_L10N = True
    
    USE_TZ = True
    
    MEDIA_URL = '/media/'
    STATIC_URL = '/static/'
    ADMIN_URL = '/admin/'
    
    
    @property
    def MEDIA_ROOT(self):
        return self.getCurrentEnvironmentRoot() + 'media/'
    
    @property
    def STATIC_ROOT(self):
        return self.getCurrentEnvironmentRoot() + 'static/'

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
            'django_config_gen',
            'reversion',
            'haystack',
            'south',
            'compressor',
            'mptt',
            'debug_toolbar',
            #'versioning',
            'captcha',
            'geoposition',
        )
    CAPTCHA_FONT_SIZE = 25
    CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
    CAPTCHA_FILTER_FUNCTIONS = ('captcha.helpers.post_smooth',)
    CAPTCHA_LETTER_ROTATION = (-10,10)
    CAPTCHA_LENGTH = 6
    
    GRAPPELLI_INDEX_DASHBOARD = 'cadocms.dashboard.CustomIndexDashboard'

    INTERNAL_IPS = ('127.0.0.1',)
    
    
    @property
    def HAYSTACK_CONNECTIONS(self):
        return {
                'default': {
                            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
                            'URL': 'http://127.0.0.1:8080/solr/' + self.CADO_PROJECT + '/',
                            },
                }
    
    @property
    def GRAPPELLI_ADMIN_TITLE(self):
        return self.CADO_NAME + ' Admin'
    
    
    SOLR_PATH = '/opt/solr/unravelling/'
    
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', 'coffee --compile --stdio'),
        ('text/less', 'lessc {infile} {outfile}'),
        ('text/x-sass', 'sass {infile} {outfile}'),
        ('text/x-scss', 'sass --scss {infile} {outfile}'),
        ('text/stylus', 'stylus < {infile} > {outfile}'),
        ('text/foobar', 'path.to.MyPrecompilerFilter'),
    )

    COMPRESS_PARSER = 'compressor.parser.HtmlParser' 
    
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