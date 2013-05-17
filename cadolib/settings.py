import socket, sys, pkgutil, os
from configurations import Settings as BaseSettings

class Settings(BaseSettings):
    
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
        return (self.getCurrentEnvironmentType == 'DEV') or (self.getCurrentEnvironmentType == 'TEST') 
        
    @property
    def TEMPLATE_DEBUG(self):
        return self.DEBUG
    
    @property
    def EMAIL_BACKEND(self):
        if (self.getCurrentEnvironmentType == 'DEV'):
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

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
    
    ROOT_URLCONF = 'yardgear.urls'
    
    WSGI_APPLICATION = 'yardgear.wsgi.application'
    
    @property
    def INSTALLED_APPS(self):
        #print 'INSTALLED_APPS CadoLib'
        return (
            self.CADO_PROJECT,
            'cadolib',
        ) + super(Settings, self).INSTALLED_APPS + (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admin',
            'south',
        )
        
    INTERNAL_IPS = ('127.0.0.1',)
    
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://127.0.0.1:8080/solr/yardgear/',
        },
    }
    