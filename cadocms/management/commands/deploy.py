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
    help = 'Deploys to specified host'
    
    """
    if HostSettingsClass.NAME == host_name and HostSettingsClass.SRCROOT == host_srcroot:
                CurrentHostSettingsClass = HostSettingsClass
                found = True
        if not found:
            print 'THIS SEEMS LIKE A DEV SERVER'
        self._HOST = CurrentHostSettingsClass
        
    return self._HOST
    """
    
    def handle(self, *args, **options):
        
        host = None
        hostname = 'unknown'
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
        
        run("ls")
        #run("source virtualenv/bin/activate");
        virtpath = host.PYTHON_PREFIX
        
        with cd('application'):
            run("git pull origin master")
        
        run("%spip install -r application/requirements.txt" % virtpath)
        
        #print args, hosts, sites
        
        with cd('application'):
            for site in sites:
                print "INSTALLING %s" % site
                #run("git submodule init")
                #run("git submodule update")
                run("%spython manage.py syncdb %s" % (virtpath, site))
                run("%spython manage.py migrate %s" % (virtpath, site))
                run("%spython manage.py collectstatic %s --noinput" % (virtpath, site))
                run("%spython manage.py config_gen" % virtpath)
                run("%spython manage.py build_solr_schema > config/solr_schema.xml" % virtpath)
                for site in django_settings.SITES:
                    with settings(warn_only=True): 
                        run("kill -9 `cat ~/%s.pid`" % site.CADO_PROJECT)
                
                    run("%spython manage.py runfcgi %s method=prefork socket=~/%s.sock pidfile=~/%s.pid" % (virtpath, site.CADO_PROJECT, site.CADO_PROJECT, site.CADO_PROJECT) )
                    run("sleep 5")
                    run("chmod 766 ~/%s.sock" % site.CADO_PROJECT)
