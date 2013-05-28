from modeltranslation.translator import translator, TranslationOptions
from cadocms.models import Translatable
from django.db import models

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__() for g in all_subclasses(s)]
#make sure all models are loaded
for model in models.get_models():
    #print model
    pass

for TranslatableClass in all_subclasses(Translatable):
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
                    