from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from models import StaticPage
from django.shortcuts import get_object_or_404
from django.db.models.loading import get_model
from django.forms.forms import Form

from django.test.utils import get_runner
from django.conf import settings

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.db.models import get_app, get_models

from cadocms.models import Moderated, MODERATION_STATUS, ModerationReason

def staticpage(request, url):
    print url
    for StaticPageClass in StaticPage.__subclasses__():
        staticpage = get_object_or_404(StaticPageClass, url=url)
    context = RequestContext(request, {'staticpage': staticpage})
    return HttpResponse(loader.get_template('staticpage.html').render(context))

def extrafields(request, model, provider_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)()
    #path_bits = model.PROVIDER_FIELD.split('.')
    #setattr(model, path_bits.pop(0), provider_id)
    form = Form()
    for key, field in model.get_provided_extra_fields_by_provider_id(provider_id):
        form.fields['extra[%s]' % key] = field['field'].formfield()
    return HttpResponse(form.as_p())

def testsuite(request):
    #SQLITE
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([])
    return HttpResponse("DUPA")


@staff_member_required
def admin_moderation(request): 
    context = {}
    
    #TODO support of multiple moderated models (TABS?)
    for model in get_models():
        if issubclass(model, Moderated):
            
            if request.POST.get('accept', 0):
                model.objects.get(id=request.POST.get('accept', 0)).moderate_accept(request.user);
        
            if request.POST.get('reject', 0):
                model.objects.get(id=request.POST.get('reject', 0)).moderate_reject(request.user, ModerationReason.objects.get(id=request.POST.get('reason', 0)));
    
            context['items'] = model.objects.filter(moderation_status__in=[MODERATION_STATUS['NEW'],MODERATION_STATUS['MODIFIED']])[0:20]
            context['admin_url_prefix'] = '/admin/' + model._meta.app_label + '/' + model._meta.object_name.lower() + '/';
    
    context['reasons'] = ModerationReason.objects.all();

    r = render_to_response('admin/moderation.html', context, RequestContext(request))
    return HttpResponse(r)