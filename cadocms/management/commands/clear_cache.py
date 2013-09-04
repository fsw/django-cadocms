from django.core.management.base import NoArgsCommand
from django.core.cache import cache

class Command(NoArgsCommand):
    help = "clears django cache"

    def handle_noargs(self, **options):
        cache.clear()
