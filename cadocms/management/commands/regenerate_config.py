import fileinput, os, sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template import loader, Context
from django.template.loaders.app_directories import app_template_dirs
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Regenerate configuration files.'
    ctx = None
    
    def handle(self, *args, **options):
        templates = []
        for dir in app_template_dirs:
            #print dir + '/config'
            if os.path.isdir(dir + '/config'):
                templates = templates + os.listdir(dir + '/config')
                
        for config in templates:
            
            output_path = 'config/' + config
            print 'rendering templates/config/%s => %s' % (config, output_path)
            ctx = Context(settings._wrapped.__dict__)    
            open(output_path, "w").write(render_to_string('config/' + config, ctx))
    