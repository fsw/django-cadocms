from django import template
from django.conf import settings

import urllib
register = template.Library()

from cadocms.models import Setting, Chunk

@register.filter()
def field_type(field):
    return field.field.__class__.__name__

@register.simple_tag(name="setting")
def get_setting(key):
    try: 
        row = Setting.objects.get(key=key)
        return row.value;
    except Setting.DoesNotExist:
        return getattr(settings, key)


@register.filter(name="setting")
def filter_setting(key):
    try:
        row = Setting.objects.get(key=key)
        return row.value;
    except Setting.DoesNotExist:
        return getattr(settings, key)


@register.filter
def keyvalue(dict, key, default=None):    
    return dict.get(key, default)

@register.simple_tag(name="chunk")
def get_chunk(key):
    for ChunkClass in Chunk.__subclasses__():
        if ChunkClass.objects.get(key=key).body:
            return '<div class="content">' + ChunkClass.objects.get(key=key).body + '</div>';
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
    request = context['request']
    return request.flavour

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
