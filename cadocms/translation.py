from modeltranslation.translator import translator, TranslationOptions
from cadocms.models import Translatable
from django.db.models.loading import get_models, get_apps
from django.conf import settings

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]


if 'cadoshop' in settings.INSTALLED_APPS:
    from cadoshop.models import StaticPage

#for app in get_apps():
#    print app
    
#make sure all models are loaded
for model in get_models():
    #print model.__module__, model.__name__
    pass

for TranslatableClass in all_subclasses(Translatable):
    #print '2'
    if not TranslatableClass._meta.abstract:
        TranslatableClassTranslationOptions = type(
                "TranslatableClassTranslationOptions", 
                (TranslationOptions,), 
                {'fields':TranslatableClass.translatable_fields})
        #print TranslatableClass.translatable_fields
        translator.register(TranslatableClass, TranslatableClassTranslationOptions)
            
"""
class ChunkTranslationOptions(TranslationOptions):
    fields = ('body',)

class StaticPageTranslationOptions(TranslationOptions):
    fields = ('url', 'title', 'content', 'seo_title', 'seo_keywords', 'seo_description',)
"""
#translator.register(Chunk, ChunkTranslationOptions)
#translator.register(StaticPage, StaticPageTranslationOptions)
                    