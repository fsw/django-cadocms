from django import template
import urllib
register = template.Library()

from cadolib.models import Setting

@register.simple_tag(name="setting")
def get_setting(key):
    return Setting.objects.get(key=key).value;
