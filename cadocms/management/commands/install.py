import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings
from fabric import colors
from django.utils.importlib import import_module

env.use_ssh_config = True

class Command(BaseCommand):
    help = 'Installs required stuff'
    
    def handle(self, *args, **options):
        print colors.green("cadocms installation script");
        print 'project code: %s' % settings.CADO_PROJECT
        print 'project name: %s' % settings.CADO_NAME
        print colors.green("checking for required folders...");
        print 'application data root: %s' % settings.HOST.APPROOT
        if not os.path.isdir(settings.HOST.APPROOT):
            raise Exception('data root folder must exists')
        
        print 'MEDIA_ROOT: %s' % settings.MEDIA_ROOT
        if not os.path.isdir(settings.MEDIA_ROOT + '/uploads/'):
            print 'creating %s' % settings.MEDIA_ROOT
            os.makedirs(settings.MEDIA_ROOT + '/uploads/')
            
        print 'STATIC_ROOT: %s' % settings.STATIC_ROOT
        if not os.path.isdir(settings.STATIC_ROOT):
            print 'creating %s' % settings.STATIC_ROOT
            os.makedirs(settings.STATIC_ROOT)
            
        
        print colors.green("creating database");
        local("./manage.py syncdb")
        local("./manage.py migrate")
        print colors.green("installing install_* fixtures");
        
        fixtures = []
        for app in settings.INSTALLED_APPS:
            try:
                mod = import_module(app)
            except ImportError, e:
                raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
            fixtures_dir = os.path.join(os.path.dirname(mod.__file__), 'fixtures')
            if os.path.isdir(fixtures_dir):
                fixtures += [ f for f in os.listdir(fixtures_dir) if os.path.isfile(os.path.join(fixtures_dir,f)) ]
            
        for fixture in fixtures:
            if fixture.startswith('install_'):
                local("./manage.py loaddata %s" % fixture)
                
        print colors.green("DONE");
        

        