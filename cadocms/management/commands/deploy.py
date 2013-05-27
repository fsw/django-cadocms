import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings
from fabric import colors

env.use_ssh_config = True
env.host_string = django_settings.CADO_PROJECT_GROUP

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'
    
    def handle(self, *args, **options):
        run("ls")
        #run("source virtualenv/bin/activate");
        virtpath = "~/virtualenv/bin/"
        with cd('application'):
            run("git pull origin master")
        
        run("%spip install -r application/requirements.txt" % virtpath)
        
        with cd('application'):
            #run("git submodule init")
            #run("git submodule update")
            run("%spython manage.py syncdb" % virtpath)
            run("%spython manage.py migrate" % virtpath)
            run("%spython manage.py collectstatic --noinput" % virtpath)
            run("%spython manage.py config_gen" % virtpath)
            run("%spython manage.py build_solr_schema > config/solr_schema.xml" % virtpath)
            
            with settings(warn_only=True): 
                run("kill -9 `cat ~/application.pid`")
            
            run("%spython manage.py runfcgi method=prefork socket=~/application.sock pidfile=~/application.pid" % virtpath)
            run("sleep 5")
            run("chmod 766 ~/application.sock")
