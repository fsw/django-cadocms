from django.core.management.base import NoArgsCommand
from django.core.cache import cache
from fabric.api import local, run, env, cd, hosts, prompt, lcd, settings, sudo
from django.conf import settings

class Command(NoArgsCommand):
    help = "clears django cache"

    def handle_noargs(self, **options):
        local("curl -s -D - %s -o /dev/null | grep HTTP" % (settings.CADO_FULL_DOMAIN,))
