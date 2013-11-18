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

from cadocms.models import Moderated, MODERATION_STATUS, ModerationReason, Tree

from django.http import HttpResponse
import simplejson
from django.db.models.fields import NOT_PROVIDED


def staticpage(request, url):
    #print 'STATICPAGE', url
    for StaticPageClass in StaticPage.__subclasses__():
        staticpage = get_object_or_404(StaticPageClass, url=url[1:])
    context = RequestContext(request, {'staticpage': staticpage})
    return HttpResponse(loader.get_template('staticpage.html').render(context))

def extrafields(request, model, provider_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)()
    #path_bits = model.PROVIDER_FIELD.split('.')
    #setattr(model, path_bits.pop(0), provider_id)
    fields = model.get_provided_extra_fields_by_provider_id(provider_id)
    
    for key, field in fields:
        field['formfield'] = field['field'].formfield()
        field['formfield'].widget.attrs['id'] = 'id_extra[%s]' % key
        field['formfield'].widget.attrs['class'] = 'extra' + field['field'].__class__.__name__
        field['formfield'].widget.attrs['placeholder'] = field['formfield'].label
        field['input'] = field['formfield'].widget.render('extra[%s]' % key,  None if field['field'].default == NOT_PROVIDED else field['field'].default)
        field['html_id'] = 'id_extra[%s]' % key
        
    context = RequestContext(request, {
        'fields':fields,
        'provider_id':provider_id
    })
    #print form.as_p(), form.media
    return HttpResponse(loader.get_template('extrafields.html').render(context));
    
def api_tree_children(request, model, parent_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)
    return HttpResponse(
        simplejson.dumps(dict(model.tree.filter(parent_id=parent_id).values_list('id', 'name'))), 
        mimetype='application/json'
    )
    
def image_uploader(request):
    ret = {
           'test' : 'test'
           }
    return HttpResponse(
        simplejson.dumps(ret), 
        mimetype='application/json'
    )
    
def api_tree_path(request, model, item_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)
    return HttpResponse(
        simplejson.dumps(list(model.objects.get(id=item_id).get_ancestors(include_self=True).values_list('id', flat=True))), 
        mimetype='application/json'
    )
    
def api_tree_fullpath(request, model, item_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)
    path = list(model.objects.get(id=item_id).get_ancestors(include_self=True).values_list('id', flat=True))
    ret = [path]
    for i in path:
        ret.append(list(model.tree.filter(parent_id=i).values_list('id', 'name')));
        
    return HttpResponse(
        simplejson.dumps(ret), 
        mimetype='application/json'
    )
    
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
                return HttpResponse(simplejson.dumps({}), mimetype='application/json')
        
            elif request.POST.get('reject', 0):
                model.objects.get(id=request.POST.get('reject', 0)).moderate_reject(request.user, ModerationReason.objects.get(id=request.POST.get('reason', 0)));
                return HttpResponse(simplejson.dumps({}), mimetype='application/json')
            
            else:
                offset = 0;
                if 'offset' in request.GET:
                    offset = int(request.GET['offset']);
                    
                context['items'] = model.objects.filter(moderation_status__in=[MODERATION_STATUS['NEW'],MODERATION_STATUS['MODIFIED']])[offset:20]
                
                context['total'] = model.objects.filter(moderation_status__in=[MODERATION_STATUS['NEW'],MODERATION_STATUS['MODIFIED']]).count() - len(context['items'])
            
                context['admin_url_prefix'] = '/admin/' + model._meta.app_label + '/' + model._meta.object_name.lower() + '/';
    
    context['reasons'] = ModerationReason.objects.all();

    r = render_to_response('admin/moderation.html', context, RequestContext(request))
    return HttpResponse(r)

@staff_member_required
def admin_clearcache(request): 
    context = {}
    from StringIO import StringIO
    from django.core import management
    output = StringIO()
    management.call_command('clear_cache', stdout=output)
    context['output'] = output.getvalue()
    r = render_to_response('admin/clearcache.html', context, RequestContext(request))
    return HttpResponse(r)

@staff_member_required
def admin_rebuildindex(request): 
    context = {}
    from StringIO import StringIO
    from django.core import management
    output = StringIO()
    management.call_command('rebuild_index', noinput=True, interactive=False ,stdout=output)
    context['output'] = output.getvalue()
    r = render_to_response('admin/rebuildindex.html', context, RequestContext(request))
    return HttpResponse(r)
