from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from models import StaticPage
from django.shortcuts import get_object_or_404
from django.db.models.loading import get_model
from django.forms.forms import Form

def staticpage(request, url):
    print url
    staticpage = get_object_or_404(StaticPage, url=url)
    context = RequestContext(request, {'staticpage': staticpage})
    return HttpResponse(loader.get_template('staticpage.html').render(context))

def extrafields(request, model, provider_id):
    app_label, model_name = model.split(".")
    model = get_model(app_label, model_name)()
    #path_bits = model.PROVIDER_FIELD.split('.')
    #setattr(model, path_bits.pop(0), provider_id)
    form = Form()
    for key, field in model.get_provided_extra_fields_by_provider_id(provider_id).items():
        form.fields['extra[%s]' % key] = field['field'].formfield()
    return HttpResponse(form.as_p())
