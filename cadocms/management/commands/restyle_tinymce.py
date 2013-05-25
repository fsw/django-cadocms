import fileinput, os, sys

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
from django.conf import settings as django_settings
from django.contrib.staticfiles import finders

from cadocms.filters.sass import SassFilter

class Command(BaseCommand):

    def handle(self, *args, **options):
        path = finders.find('css/content.scss')
        print 'Generating CSS out of ' + path
        content = open(path, 'r').read()
        output_css = SassFilter(content, {'href' : '/css/content.scss'}, 'css', filename=path).input()
        output_path = os.path.abspath(django_settings.STATIC_ROOT + '/css/tinymce.css') 
        print 'Saving %d bytes to %s' % (len(output_css), output_path)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        f = open(output_path, 'w')
        f.write(output_css)
        f.close()
        print 'DONE'