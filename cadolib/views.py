from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from models import StaticPage
from django.shortcuts import get_object_or_404

def staticpage(request, url):
    print url
    staticpage = get_object_or_404(StaticPage, url='/' + url)
    context = RequestContext(request, {'staticpage': staticpage})
    return HttpResponse(loader.get_template('staticpage.html').render(context))