import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings
from fabric import colors

from cadocms.settings import HostSettings
env.use_ssh_config = True

class Command(BaseCommand):
    args = '<host>'
    help = 'Installs on specified host'
    
    def handle(self, *args, **options):
        
        host = None
        hostname = 'dev'
        hosts = []
        if len(args):
            hostname = args[0]
            
        for HostSettingsClass in HostSettings.__subclasses__():
            name = HostSettingsClass.__name__.replace('HostSettings', '').lower()
            hosts.append(name)
            if hostname == name:
                host = HostSettingsClass
                
        if host is None:
            print 'host should be one of:', hosts
            raise Exception("Unknown host %s" % (hostname,))
        #if 
        env.host_string = host.HOST_STRING
        if (host.HOST_STRING == 'localhost'):
            runner = local
        else:
            runner = run
        
        runner("ls")
        return
        #run("source virtualenv/bin/activate");
        virtpath = host.PYTHON_PREFIX
        
        run("%spip install -r application/requirements.txt" % virtpath)
        
        #print args, hosts, sites
        
        with cd('application'):
            run("%spython manage.py regenerate_config" % virtpath)
            run("%spython manage.py build_solr_schema > config/solr_schema.xml" % virtpath)
            for site in django_settings.SITES:
                print "INSTALLING %s" % site.CADO_PROJECT
                arguments = ''
                if django_settings.MULTISITE:
                    arguments = site.CADO_PROJECT
                #run("git submodule init")
                #run("git submodule update")
                run("%spython manage.py syncdb %s" % (virtpath, arguments))
                run("%spython manage.py migrate %s" % (virtpath, arguments))
                run("%spython manage.py collectstatic %s --noinput" % (virtpath, arguments))
                run("%spython manage.py restyle_tinymce %s" % (virtpath, arguments))
                
                with settings(warn_only=True): 
                    run("kill -9 `cat ~/%s.pid`" % site.CADO_PROJECT)
                
                run("%spython manage.py runfcgi %s method=prefork socket=~/%s.sock pidfile=~/%s.pid" % (virtpath, site.CADO_PROJECT, site.CADO_PROJECT, site.CADO_PROJECT) )
                run("sleep 5")
                run("chmod 766 ~/%s.sock" % site.CADO_PROJECT)
