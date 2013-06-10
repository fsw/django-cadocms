import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings

env.use_ssh_config = True


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Installs Solr'

    def handle(self, *args, **options):
        local("./manage.py build_solr_schema > config/solr_schema.xml")
                
                curl -v 'http://127.0.0.1:8080/solr/admin/cores?action=CREATE&name=yardgear&instanceDir=yardgear&config=solrconfig.xml&schema=schema.xml&dataDir=data'
                
        local("sudo cp config/solr_schema.xml " + django_settings.SOLR_PATH + "/conf/schema.xml")
        local("sudo /etc/init.d/tomcat6 restart")