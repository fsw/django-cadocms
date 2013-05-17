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
        """
        git_sub_modules = 'submodules'
        workspace_dir = '..'
        for submodule in os.listdir(git_sub_modules):
            path = os.path.abspath(os.path.join(git_sub_modules, submodule))
            if os.path.isdir(os.path.abspath(os.path.join(workspace_dir, submodule))):
                path = os.path.abspath(os.path.join(workspace_dir, submodule))
                
            print 'trying to push ' + path
             
            with lcd(path):
                with settings(warn_only=True): 
                    local("git add -A")
                    if message is not None:
                        local("git commit -m '%s'" % message)
                    else:
                        local("git commit")
                    local("git push origin master")
        """
        print 'REBUILDING CONFIGURATION'
        local("./manage.py build_solr_schema > config/solr_schema.xml")
        with settings(warn_only=True):
            #local("git submodule foreach git pull") 
            local("git add -A")
            #if message is not None:
            #local("git commit -m '%s'" % message)
            #else:
            local("git commit")
            local("git push origin master")
