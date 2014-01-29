from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ajax_upload.forms import UploadedFileForm
import json


@csrf_exempt
@require_POST
def upload(request):
    #print 'XXXX'
    
    content_type = "text/plain";
    if request.META.get('HTTP_ACCEPT'):
        if 'application/json' in request.META.get('HTTP_ACCEPT').split(","):
            content_type = "application/json";
    
    form = UploadedFileForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        uploaded_file = form.save()
        data = {
            'path': uploaded_file.file.url,
        }
        #print simplejson.dumps(data)
        return HttpResponse(json.dumps(data), content_type=content_type)
    else:
        return HttpResponseBadRequest(json.dumps({'errors': form.errors}), content_type=content_type)
