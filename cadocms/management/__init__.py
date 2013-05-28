import os, sys

#from configurations import importer
#importer.install()

#from configurations import importer
#importer.installed = True
#_temp = __import__(os.environ["DJANGO_SETTINGS_MODULE"], globals(), locals(), [os.environ["DJANGO_CONFIGURATION"],], -1)
#settingsClass = getattr(_temp, os.environ["DJANGO_CONFIGURATION"])
#from cadocms.settings import MultiAppSettings

#if issubclass(settingsClass, MultiAppSettings):
if os.environ.get("CADO_SITES", "").split(";"):
    sites = []
    for name in os.listdir(os.getcwd()):
        if os.path.isdir(os.path.join(os.getcwd(), name)):
            if os.path.isfile(os.path.join(os.getcwd(), name, 'settings.py')):
                if not name + '.settings' == os.environ["DJANGO_SETTINGS_MODULE"]:
                    sites.append(name)

    scriptname = sys.argv.pop(0);
    command = sys.argv.pop(0);
            
    commands_requiring_site = ['runserver', 'restyle_tinymce', 'syncdb', 'schemamigration', 'migrate', 'collectstatic', 'runfcgi', 'loaddata', 'dumpdata']
    
    
    if command in commands_requiring_site:
        if not 'CADO_APP' in os.environ:
            site = 'unknown'
            if len(sys.argv):
                site = sys.argv.pop(0);
            if not site in sites:
                raise Exception("Command '%s' requires site parameter. Unknown site '%s'" % (command, site))
            os.environ['CADO_APP'] = site
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ['CADO_APP'] + '.settings'
        os.environ["DJANGO_CONFIGURATION"] = 'Settings'
    
    sys.argv.insert(0, command)
    sys.argv.insert(0, scriptname)

#importer.installed = False
#importer.installed = False
#importer.install()

from configurations.management import execute_from_command_line  # noqa

#print settings.CADO_PROJECT

"""
sites = [name for name in os.listdir(os.path.dirname(__file__)) if os.path.isdir(os.path.join(os.path.dirname(__file__), name))]
sites.append('cadocms')
if not 'L3KSITE' in os.environ:
        scriptname = sys.argv.pop(0);
        sitename = sys.argv.pop(0);
        #if sitename in no_site_commands:
        #    os.environ['L3KSITE'] = 'cadocms'
        #    sys.argv.insert(0, sitename)
        #else:
        os.environ['L3KSITE'] = sitename
        sys.argv.insert(0, scriptname)

    if os.environ['L3KSITE'] in sites:
        #print 'running manage.py for %s' % os.environ['L3KSITE']
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ['L3KSITE'] + ".settings")
        os.environ.setdefault('DJANGO_CONFIGURATION', 'Settings')        
        from configurations.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    else:
        print 'unknown site ' + os.environ['L3KSITE']
        print scriptname
        print sites
    """
    