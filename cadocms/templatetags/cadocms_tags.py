from django import template
import urllib
register = template.Library()

from cadocms.models import Setting

@register.simple_tag(name="setting")
def get_setting(key):
    return Setting.objects.get(key=key).value;

@register.filter
def keyvalue(dict, key, default=None):    
    return dict.get(key, default)