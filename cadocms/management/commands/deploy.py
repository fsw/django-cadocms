import fileinput, os, sys, hashlib, tempfile

from django.core.management.base import BaseCommand, CommandError
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files, console
from fabric.operations import put
from django.conf import settings as django_settings
from fabric import colors
from difflib import context_diff
from optparse import make_option

from cadocms.settings import HostSettings
env.use_ssh_config = True

class Command(BaseCommand):
    args = '<host>'
    help = 'Deploys to specified host'
    
    option_list = BaseCommand.option_list + (
        make_option('--nobackup',
            action='store_true',
            dest='nobackup',
            default=False,
            help='Do not BACKUP'),
        make_option('--initial1',
            action='store_true',
            dest='initial1',
            default=False,
            help='Initial deploy - step 1'),
        make_option('--initial2',
            action='store_true',
            dest='initial2',
            default=False,
            help='Initial deploy - step 2'),
        make_option('--branch',
            action='store',
            dest='branch',
            default='master',
            help='Branch to pull and checkout'),
        )
    
    def handle(self, *args, **options):

        import os, random, string
        deploy_hash = ''.join(random.choice(string.lowercase) for x in range(32))
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
        
        print colors.red("DEPLOYING TO: %s" % hostname, bold=True)
        print colors.red("DEPLOY HASH = %s" % deploy_hash, bold=True)
        
        #if 
        env.host_string = host.HOST_STRING
        print colors.red("TEST COMMAND:", bold=True)
        run("ls")
        #run("source virtualenv/bin/activate");
        virtpath = host.PYTHON_PREFIX
        if options['initial1'] and not files.exists(host.SRCROOT) and not files.exists(host.APPROOT):
            sql = "CREATE DATABASE %s; GRANT ALL ON %s.* TO %s@localhost IDENTIFIED BY '%s';" % (host.DATABASE['NAME'], host.DATABASE['NAME'], host.DATABASE['USER'], host.DATABASE['PASSWORD'])
            print colors.red("RUN THIS:")
            print colors.red(sql)
            #print sql
            #run('echo "%s" | mysql --batch -u %s -p' % (sql, 'root'))
            return

        if options['initial2'] and not files.exists(host.SRCROOT) and not files.exists(host.APPROOT):
            print colors.red("initial2=true and SRCROOT/APPROOT does not exist. will install now");
            run('mkdir %s' % host.SRCROOT)
            run('mkdir %s' % host.APPROOT)
            run('mkdir %s/logs' % host.APPROOT)
            with cd(host.SRCROOT):
                run("git init")
                run("git remote add origin %s" % host.GIT_REMOTE)
                run("git pull origin master")
                run(host.PYTHON_INSTALL)
                run("%spip install -r requirements.txt" % virtpath)
                run("%spython manage.py install" % virtpath)
            #return
        
        with cd(host.SRCROOT):
            if host.CLASS == 'PROD' and not options['nobackup']:
                print colors.red("PROD BACKUP:", bold=True)
                run("%spython manage.py backup" % (virtpath,))
            
            print colors.red("REVERTING SETTINGS:", bold=True)
            run("git checkout -- %s/settings.py" % (django_settings.CADO_PROJECT))

            print colors.red("UPDATING CODEBASE:", bold=True)
            run("git pull origin %s" % options['branch'])
            run("git checkout %s" % options['branch'])

            print colors.red("INSTALLING REQUIREMENTS:", bold=True)
            run("%spip install -q -r requirements.txt" % virtpath)
            
            print colors.red("INSERTING HASH:", bold=True)
            run("sed 's/XXAUTODEPLOYHASHXX/%s/' %s/settings.py > %s/settings.tmp.py" % (deploy_hash, django_settings.CADO_PROJECT, django_settings.CADO_PROJECT))
            run("mv %s/settings.tmp.py %s/settings.py" % (django_settings.CADO_PROJECT, django_settings.CADO_PROJECT))
            
            #sed 's/foo/bar/' mydump.sql > fixeddump.sql
        
            print colors.red("REGENERATIN CONFIG FILES:", bold=True)
            run("%spython manage.py regenerate_config" % virtpath)
            
            if django_settings.MULTISITE:
                for site in django_settings.SITES:
                    #run("mkdir config/solr/%s" % site.SOLR_CORE_NAME)
                    run("%spython manage.py build_solr_schema %s > config/solr/%s_schema.xml" % (virtpath, site.CADO_PROJECT , site.SOLR_CORE_NAME))
            else:
                run("%spython manage.py build_solr_schema > config/solr/schema.xml" % virtpath)
                            
            for name, getter, setter, combined in host.CONFIGS:
                diff = False
                current = run(getter, quiet = True, warn_only = True).splitlines()
                current =[line+"\n" for line in current]
                new = run("cat config/" + name, quiet = True).splitlines()
                new =[line+"\n" for line in new]
                
                if combined:
                    combined = []
                    hash = hashlib.md5(host.APPROOT).hexdigest()
                    start_line = "##### CHUNK GENERATED BY CADOCMS %s PLEASE DON'T MODIFY #####\n" % hash 
                    end_line = "##### END OF CHUNK GENERATED BY CADOCMS %s #####\n" % hash
                    if start_line not in current:
                        current.append(start_line)
                    if end_line not in current:
                        current.append(end_line)
                    in_chunk = False    
                    for line in current:
                        if line == start_line:
                            in_chunk = True
                            combined.append(start_line)
                            combined = combined + new
                            combined.append(end_line)
                        if not in_chunk:
                            combined.append(line)
                        if line == end_line:
                            in_chunk = False
                    tf = tempfile.NamedTemporaryFile()
                    tfName = tf.name
                    tf.seek(0)
                    #print current, new, combined
                    for line in combined:
                        tf.write(line)
                    tf.flush()
                    put(tfName, 'config/%s.combined' % name)
                    new = combined
                    name = name + '.combined'
                    
                for line in context_diff(current, new, fromfile='CURRENT', tofile='NEW'):
                    diff = True
                choice = 'd'
                if diff:
                    while choice == 'd':    
                        choice = console.prompt('%s config file differs. [d]=show diff, [r]=replace, [i]=ignore' % (name,), default='i', validate='d|r|i')
                        if (choice == 'd'):
                            for line in context_diff(current, new, fromfile='CURRENT', tofile='NEW'):
                                sys.stdout.write(line)
                        if (choice == 'r'):
                            run("cat config/" + name + " " + setter)
                    
            for site in django_settings.SITES:
                print colors.red("INSTALLING SITE %s:" % site.CADO_PROJECT, bold=True)
                arguments = ''
                if django_settings.MULTISITE:
                    arguments = site.CADO_PROJECT
                #run("git submodule init")
                #run("git submodule update")
                run("%spython manage.py syncdb %s" % (virtpath, arguments))
                run("%spython manage.py migrate %s" % (virtpath, arguments)) #--traceback
                run("%spython manage.py collectstatic %s --noinput" % (virtpath, arguments))
                run("%spython manage.py restyle_tinymce %s" % (virtpath, arguments))
                print colors.yellow("FORCING STYLES REBUILD:", bold=True)
                run("%spython manage.py compress %s" % (virtpath, arguments))
                
                print colors.yellow("RESTARTING FASTCGI:", bold=True)
                
                with settings(warn_only=True): 
                    run("kill -9 `cat %s/%s.pid`" % (host.APPROOT, site.CADO_PROJECT))
                
                run("find . -name '*.pyc' -delete")
                
                maxchildren = 3
                if host.CLASS == 'TEST':
                    maxchildren = 1
                    
                run("%spython manage.py runfcgi %s method=threaded maxchildren=%d socket=%s/%s.sock pidfile=%s/%s.pid umask=000" % (virtpath, site.CADO_PROJECT, maxchildren, host.APPROOT, site.CADO_PROJECT, host.APPROOT, site.CADO_PROJECT) )
                #run("sleep 3")
                print colors.yellow("NOT CLEARING CACHE:)", bold=True)
                #run("%spython manage.py clear_cache" % (virtpath,))
                #run("chmod 777 %s/%s.sock" % (host.APPROOT, site.CADO_PROJECT))
                run("%spython manage.py warmup %s" % (virtpath, arguments))
                print colors.green("DONE!", bold=True)
                
                
