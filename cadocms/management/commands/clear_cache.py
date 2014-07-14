from django.core.management.base import NoArgsCommand
from django.core.cache import cache
from cadocms.models import ExtraFieldsUser

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]

class Command(NoArgsCommand):
    help = "clears django cache"

    def handle_noargs(self, **options):
        cache.clear()
        from cadocms.templatetags.cadocms_tags import SETTINGS_CACHE
        SETTINGS_CACHE = {}
        
        #clearing extra fields cache
        for ExtraFieldsUserClass in all_subclasses(ExtraFieldsUser):
            if not ExtraFieldsUserClass._meta.abstract:
                print 'clean extra fields ', ExtraFieldsUserClass
                ExtraFieldsUserClass.clear_cache()
