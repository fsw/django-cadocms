from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from fabric.contrib import files
import fileinput, os, sys
from django.conf import settings as django_settings

env.use_ssh_config = True
    
def push(message=None):
    repos = ['../django-cadoshop', '../django-cadolib']
    for path in repos:
        with lcd(path):
            with settings(warn_only=True): 
                local("git add -A")
                if message is not None:
                    local("git commit -m '%s'" % message)
                else:
                    local("git commit")
                local("git push origin master")
    
    local("./manage.py build_solr_schema > config/solr_schema.xml")
    
    with settings(warn_only=True):
        local("git submodule foreach git pull") 
        local("git add -A")
        if message is not None:
            local("git commit -m '%s'" % message)
        else:
            local("git commit")
        local("git push origin master")
    
def update_solr():
    local("./manage.py build_solr_schema > config/solr_schema.xml")
    local("sudo cp config/solr_schema.xml " + django_settings.SOLR_PATH + "/conf/schema.xml")
    local("sudo /etc/init.d/tomcat6 restart")
    
@hosts('unravelling')
def deploy():
    run("ls")
    #run("source virtualenv/bin/activate");
    virtpath = "~/virtualenv/bin"
    with cd('application'):
        run("git pull origin master")
    
    run("%s/pip install -r application/requirements.txt" % virtpath)
    
    with cd('application'):
        run("git submodule init")
        run("git submodule update")
        run("%s/python manage.py syncdb" % virtpath)
        run("%s/python manage.py migrate" % virtpath)
        run("%s/python manage.py collectstatic --noinput" % virtpath)
        run("%s/python manage.py config_gen" % virtpath)
        run("%s/python manage.py build_solr_schema > config/solr_schema.xml" % virtpath)
        with settings(warn_only=True): 
            run("kill -9 `cat ~/application.pid`")
        
        run("%s/python manage.py runfcgi method=prefork socket=~/application.sock pidfile=~/application.pid" % virtpath)
        run("sleep 5")
        run("chmod 766 ~/application.sock")
        
        #run("sudo /etc/init.d/apache2 restart")
        #run("touch mysite.wsgi")
