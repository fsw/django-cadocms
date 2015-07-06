import urllib

from datetime import date, datetime
from django import template
from django.conf import settings
from cadocms.models import Setting, Chunk, StaticPage

from django.template import defaultfilters
from django.utils.encoding import force_text
from django.utils.formats import number_format
from django.utils.timezone import is_aware, utc
from django.utils.translation import pgettext, ungettext, ugettext as _
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re
from django.forms.fields import CheckboxInput

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput)

#http://stackoverflow.com/questions/721035/django-templates-stripping-spaces
@stringfilter
def spacify(value, autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(re.sub('\s', '&'+'nbsp;', esc(value)))
spacify.needs_autoescape = True
register.filter(spacify)

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.filter()
def smart_ul(list, attrs=''):
    if not list:
        return ''
    else:
        ret = '<ul %s>' % (attrs,)
        for item in list:
            ret = ret + '<li>%s</li>' % (item,)
        ret = ret + '</ul>'
        return mark_safe(ret);
        
SETTINGS_CACHE = {}

@register.simple_tag(name="setting")
def get_setting(key):
    if not SETTINGS_CACHE.has_key(key):
        try: 
            row = Setting.objects.get(key=key)
            SETTINGS_CACHE[key] = row.value;
        except Setting.DoesNotExist:
            try:
                SETTINGS_CACHE[key] = getattr(settings, key)
            except:
                new = Setting(key=key)
                new.save();
                SETTINGS_CACHE[key] = new.value;
        
    return SETTINGS_CACHE[key]

@register.filter(name="setting")
def filter_setting(key):
    try:
        row = Setting.objects.get(key=key)
        return row.value;
    except Setting.DoesNotExist:
        return getattr(settings, key)

@register.simple_tag(name="host_setting")
def get_host_setting(key):
    return getattr(settings.HOST, key)

@register.filter(name="host_setting")
def filter_host_setting(key):
    return getattr(settings.HOST, key)

@register.filter
def keyvalue(o, key, default=None):
    if isinstance(o, dict):
        return o.get(key, default)
    else:
        print o.__dict__
        print key
        return o.__dict__.get(key, default)
        

@register.simple_tag(name="chunk")
def get_chunk(key, raw=False):
    for ChunkClass in Chunk.__subclasses__():
        try:
            chunk = ChunkClass.objects.get(key=key)
        except ChunkClass.DoesNotExist:
            chunk = ChunkClass(key=key, body='please edit this in admin chunks panel:<br/><b>%s</b>' % key)
            chunk.save()
            
        if chunk.body:
            if raw:
                return chunk.body
            else:
                return '<div class="content">' + chunk.body + '</div>';
        else:
            if raw:
                return ''
            else:
                return '<div class="content"></div>';

@register.simple_tag(name="staticpage")
def get_staticpage(key):
    for StaticpageClass in StaticPage.__subclasses__():
        if StaticpageClass.objects.get(url=key).content:
            return '<div class="content">' + StaticpageClass.objects.get(url=key).content + '</div>';
        else:
            return '<div class="content"></div>';
        
class FlavoursNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name
    def render(self, context):
        request = context['request']
        #print request.path_info        
        ret = []
        for key, flavour, prefix in settings.CADO_FLAVOURS:
            ret.append({
                        'key': key,
                        'name': flavour, 
                        'current': request.flavour == key,
                        'url': 'http://' + prefix + settings.CADO_FULL_DOMAIN + request.path_info,
                        'prefix': prefix
                        })
        context[self.var_name] = ret
        return ''
    
@register.simple_tag(name="get_current_flavour", takes_context = True)
def get_flavour(context):
    #CADO_FLAVOURS
    request = context.get('request', None)
    return getattr(request, 'flavour', 'desktop')

@register.tag(name='get_available_flavours')
def get_available_flavours(parser, token):
    error = False
    try:
        tag_name, _as, var_name = token.split_contents()
        if _as != 'as':
            error = True
    except:
        error = True

    if error:
        raise TemplateSyntaxError, 'get_available_flavours'
    else:
        return FlavoursNode(var_name)
    
    
@register.tag(name='captureas')  
def do_captureas(parser, token):  
    try:  
        tag_name, args = token.contents.split(None, 1)  
    except ValueError:  
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")  
    nodelist = parser.parse(('endcaptureas',))  
    parser.delete_first_token()  
    return CaptureasNode(nodelist, args)  
  
class CaptureasNode(template.Node):  
    def __init__(self, nodelist, varname):  
        self.nodelist = nodelist  
        self.varname = varname  
  
    def render(self, context):  
        output = self.nodelist.render(context)  
        context[self.varname] = output  
        return ''  

from datetime import timedelta

@register.filter
def hmsfrom(date):
    now = datetime.now().replace(tzinfo=None)
    delta = now - date.replace(tzinfo=None)
    delta2 = timedelta(days=delta.days, seconds=delta.seconds)
    return delta2

@register.filter
def secondsfrom(date):
    now = datetime.now().replace(tzinfo=None)
    delta = now - date.replace(tzinfo=None)
    return (delta.days * 60 * 60 * 24) + delta.seconds

@register.filter
def get_range( value ):
    return range( value )
  
  
def paginator(page, url, adjacent_pages=2):
    
    page_numbers = [n for n in \
                    range(page.number - adjacent_pages, page.number + adjacent_pages + 1) \
                    if n > 0 and n <= page.paginator.num_pages]
    return {
        'page': page.number,
        'pages': page.paginator.num_pages,
        'page_numbers': page_numbers,
        'next': page.next_page_number,
        'url': url,
        'previous': page.previous_page_number,
        'has_next': page.has_next,
        'has_previous': page.has_previous,
        'show_first': 1 not in page_numbers,
        'show_last': page.paginator.num_pages not in page_numbers,
    }

register.inclusion_tag('paginator.html')(paginator)



@register.filter
def simpletime(value):
    
    if not isinstance(value, date): # datetime is a subclass of date
        return value

    now = datetime.now(utc if is_aware(value) else None)
    if value < now:
        delta = now - value
        if delta.days != 0:
            if delta.days < 31:
                return ungettext(
                    # Translators: \\u00a0 is non-breaking space
                    'yesterday', '%(count)s days ago', delta.days
                ) % {'count': delta.days}
            else:
                if value.year == now.year:
                    return value.strftime("%d %B");
                else: 
                    return value.strftime("%B %Y");
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a second ago', '%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a minute ago', '%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'an hour ago', '%(count)s hours ago', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s from now'
            ) % {'delta': defaultfilters.timeuntil(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a second from now', '%(count)s seconds from now', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a minute from now', '%(count)s minutes from now', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'an hour from now', '%(count)s hours from now', count
            ) % {'count': count}

