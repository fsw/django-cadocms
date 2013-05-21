import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings

env.use_ssh_config = True


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        libs_dir = '../libs'
        workspace_dir = '..'
        for submodule in os.listdir(libs_dir):
            path = os.path.abspath(os.path.join(libs_dir, submodule))
            print 'trying to push ' + path
            with lcd(path):
                with settings(warn_only=True): 
                    local("git add -A")
                    #if message is not None:
                    #    local("git commit -m '%s'" % message)
                    #else:
                    local("git commit")
                    local("git push origin master")

        print 'REBUILDING CONFIGURATION'
        local("./manage.py build_solr_schema > config/solr_schema.xml")
        local("./manage.py config_gen")
        with settings(warn_only=True):
            #local("git submodule foreach git pull") 
            local("git add -A")
            #if message is not None:
            #local("git commit -m '%s'" % message)
            #else:
            local("git commit")
            local("git push origin master")
