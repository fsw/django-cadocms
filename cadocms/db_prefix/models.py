"""
from django.conf import settings
from django.db.models.signals import class_prepared
from django.db import models

prefix = getattr(settings, "DB_PREFIX", None)
    
def add_db_prefix(model):
    print 'ADDDBPREFIX', prefix, model._meta.db_table
    global prefix
    if prefix:
        if not model._meta.db_table.startswith(prefix):
            model._meta.db_table = prefix + model._meta.db_table
            print 'NEW:', model._meta.db_table
        
for app in models.get_apps():
    for model in models.get_models(app):
        add_db_prefix(model)

def add_db_prefix_hook(sender, **kwargs):
    print 'ADDDBPREFIXHOOK', prefix, sender._meta.db_table
    add_db_prefix(sender)
        
class_prepared.connect(add_db_prefix_hook)
"""