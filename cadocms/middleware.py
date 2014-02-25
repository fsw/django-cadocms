# Source: http://detectmobilebrowsers.com/
# Ported by Matt Sullivan http://sullerton.com/2011/03/django-mobile-browser-detection-middleware/
import re, sys, cProfile
from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from cStringIO import StringIO
from cadocms.views import staticpage
from django.http import Http404

reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local
 
_thread_locals = local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class Middleware():
    def process_request(self, request):
        
        if settings.CADO_L10NURLS and len(settings.CADO_LANGUAGES) > 0:
            #this is a multilanguage site
            url_lang = None
            chunks = request.path_info.split('/')
            chunk0 = chunks.pop(1)
            for code, name in settings.CADO_LANGUAGES:
                #print code, name, chunk0
                if chunk0 == code:
                    url_lang = code
                    translation.activate(url_lang)
                    request.LANGUAGE_CODE = translation.get_language()
            
            
            #TODO: read those from settings:
            if url_lang is None and chunk0 not in ['dev', 'admin', 'media', 'static', 'captcha', 'robots.txt', '__debug__']:
                #redirect
                preffered_language = translation.get_language_from_request(request)
                if(preffered_language not in dict(settings.CADO_LANGUAGES)):
                    preffered_language = settings.CADO_LANGUAGES[0][0]
                return HttpResponseRedirect("/" + preffered_language + request.path_info)
        #elif len(settings.CADO_LANGUAGES) == 1:
        #    translation.activate(settings.CADO_LANGUAGES[0][0])
        #    request.LANGUAGE_CODE = translation.get_language()
            
            
        request.flavour = None
        if request.is_ajax():
            request.flavour = 'ajax'
        else:
            for key, name, prefix in settings.CADO_FLAVOURS:
                if request.get_host().startswith(prefix):
                    request.flavour = key
        
        #first time visitor
        if not request.session.get('flavour', None):
            flavour = 'desktop'
            if request.META.has_key('HTTP_USER_AGENT'):
                user_agent = request.META['HTTP_USER_AGENT']
                b = reg_b.search(user_agent)
                v = reg_v.search(user_agent[0:4])
                if b or v:
                    flavour = 'mobile'
            request.session['flavour'] = flavour
            if (flavour != request.flavour) and (flavour != 'ajax'):
                for key, name, prefix in settings.CADO_FLAVOURS:
                    if key == flavour:
                        HttpResponseRedirect('http://' + prefix + settings.CADO_FULL_DOMAIN + request.path_info)
        
        _thread_locals.request = request
        
class Profiler(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'prof' in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and 'prof' in request.GET:
            self.profiler.create_stats()
            out = StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            self.profiler.print_stats(1)
            sys.stdout = old_stdout
            response.content = '<pre>%s</pre>' % out.getvalue()
        return response
    
    
class StaticPagesFallback(object): 
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a flatpage for non-404 responses.
        try:
            return staticpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response
