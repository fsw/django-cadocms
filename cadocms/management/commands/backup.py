from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os, datetime
from optparse import make_option


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        if len(args):
            label = '_' + args[0]
        else:
            label = ''
            
        backup_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M");
        host_label = settings.CADO_FULL_DOMAIN.replace('.','_').replace(':','_');
        
        outfile = getattr(settings, 'BACKUP_DIR', 'backup') + host_label + '_' + backup_date + label + '.sql.gz'
        outfile_tar = getattr(settings, 'BACKUP_DIR', 'backup') + host_label + '_' + backup_date + label + '_media.tar.gz'

        print 'dumping DB to: %s' % outfile
        
        #if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
        #    raise CommandError('Unknown DB backend: %s' % settings.DATABASES['default']['ENGINE'])
    
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
        command = 'mysqldump %s | gzip -c > %s' % (' '.join(args), outfile)
        print command
        os.system(command)
        
        print 'dumping MEDIA to: %s' % outfile_tar
        command = 'tar -cf %s %s' % (outfile_tar, settings.MEDIA_ROOT)
        print command
        os.system(command)
