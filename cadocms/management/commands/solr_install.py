import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings
from fabric import colors

env.use_ssh_config = True


class Command(BaseCommand):
    help = 'Installs Solr Core'

    def handle(self, *args, **options):
        print colors.red('trying to install solr core to %s' % django_settings.SOLR_CORE_PATH)
                
        #run("%spython manage.py regenerate_config" % virtpath)
        #run("%spython manage.py build_solr_schema > config/solr/schema.xml" % virtpath)
        print colors.yellow('copying configs')
        if not os.path.isdir(django_settings.SOLR_CORE_PATH + "/conf/"):
            os.makedirs(django_settings.SOLR_CORE_PATH + "/conf/")
        local("cp -r config/solr/* " + django_settings.SOLR_CORE_PATH + "/conf/")
        
        print colors.yellow('creating core via solr admin')
        local("curl -v '%sadmin/cores?action=CREATE&name=%s&instanceDir=%s&config=solrconfig.xml&schema=schema.xml&dataDir=data'"
              % (django_settings.SOLR_URL, django_settings.SOLR_CORE_NAME, django_settings.SOLR_CORE_NAME )
              )
        
                
        
        #local("sudo /etc/init.d/tomcat6 restart")
        