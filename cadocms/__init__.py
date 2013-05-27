from django.http import HttpResponse
from django.template import RequestContext, Context, loader

__version__ = '0.1.0'
__all__ = ['renderTemplate',]

def renderTemplate(request, name, context = {}):
    (request.flavour)
    
    #context['base_template'] = 'base.html'
    context = RequestContext(request, context)
    return HttpResponse(loader.get_template(name + '.html').render(context))
