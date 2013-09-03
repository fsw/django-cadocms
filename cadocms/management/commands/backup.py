from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        
        outfile = getattr(settings, 'BACKUP_DIR', 'backup') + settings.HOST.DOMAIN.replace('.','_').replace(':','_') + '_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + '.sql'
        
        print 'dumping DB to: %s' % outfile
        
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
            raise CommandError('Unknown DB backend: %s' % settings.DATABASES['default']['ENGINE'])
    
        args = []
        if settings.DATABASES['default']['USER']:
            args += ["--user='%s'" % settings.DATABASES['default']['USER']]
        if settings.DATABASES['default']['PASSWORD']:
            args += ["--password='%s'" % settings.DATABASES['default']['PASSWORD']]
        if settings.DATABASES['default']['HOST']:
            args += ["--host='%s'" % settings.DATABASES['default']['HOST']]
        if settings.DATABASES['default']['PORT']:
            args += ["--port=%s" % settings.DATABASES['default']['PORT']]
            
        args += [settings.DATABASES['default']['NAME']]
        command = 'mysqldump %s > %s' % (' '.join(args), outfile)
        print command
        os.system(command)
