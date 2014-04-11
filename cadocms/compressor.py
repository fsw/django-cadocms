from django.utils.encoding import force_text
from django.conf import settings

def cado_cachekey(key):
    return '%s.django_compressor.%s' % (settings.CACHE_PREFIX, force_text(key))
