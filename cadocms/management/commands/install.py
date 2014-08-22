import os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings
from fabric import colors
from django.utils.importlib import import_module
from cadocms.settings import get_management_command
from django.core.exceptions import ImproperlyConfigured

env.use_ssh_config = True

class Command(BaseCommand):
    help = 'Installs required stuff'
    
    def handle(self, *args, **options):
        print colors.green("cadocms installation script");
        for site_settings in settings.SITES_SETTINGS:
            print 'project code: %s' % site_settings.CADO_PROJECT
            print 'project name: %s' % site_settings.CADO_NAME
            print colors.green("checking for required folders...");
            print 'application data root: %s' % site_settings.HOST.APPROOT
            if not os.path.isdir(site_settings.HOST.APPROOT):
                raise Exception('data root folder must exists')
        
            print 'MEDIA_ROOT: %s' % site_settings.MEDIA_ROOT
            if not os.path.isdir(site_settings.MEDIA_ROOT + '/uploads/'):
                print 'creating %s' % site_settings.MEDIA_ROOT
                os.makedirs(site_settings.MEDIA_ROOT + '/uploads/')
            
            print 'STATIC_ROOT: %s' % site_settings.STATIC_ROOT
            if not os.path.isdir(site_settings.STATIC_ROOT):
                print 'creating %s' % site_settings.STATIC_ROOT
                os.makedirs(site_settings.STATIC_ROOT)
                        
            print colors.green("creating database");
            
            local(get_management_command(site_settings, 'sql auth') + ' | ' + get_management_command(site_settings, 'dbshell'))
            local(get_management_command(site_settings, 'sql admin') + ' | ' + get_management_command(site_settings, 'dbshell'))
            
            local(get_management_command(site_settings, 'syncdb') + ' --noinput')
            local(get_management_command(site_settings, 'migrate'))
            print colors.green("installing install_* fixtures");
            
            fixtures = []
            for app in site_settings.INSTALLED_APPS:
                try:
                    mod = import_module(app)
                except ImportError, e:
                    raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
                fixtures_dir = os.path.join(os.path.dirname(mod.__file__), 'fixtures')
                if os.path.isdir(fixtures_dir):
                    fixtures += [ f for f in os.listdir(fixtures_dir) if os.path.isfile(os.path.join(fixtures_dir,f)) ]
                
            for fixture in fixtures:
                if fixture.startswith('install_'):
                    local("%s %s" % (get_management_command(site_settings, 'loaddata'), fixture))

        print colors.green("creating superuser");
        local(get_management_command(settings, 'createsuperuser'))
        print colors.green("DONE");
        

        