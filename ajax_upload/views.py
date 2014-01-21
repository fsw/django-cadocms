from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ajax_upload.forms import UploadedFileForm


@csrf_exempt
@require_POST
def upload(request):
    #print 'XXXX'
    form = UploadedFileForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        uploaded_file = form.save()
        data = {
            'path': uploaded_file.file.url,
        }
        #print simplejson.dumps(data)
        return HttpResponse(simplejson.dumps(data), content_type="application/json")
    else:
        return HttpResponseBadRequest(simplejson.dumps({'errors': form.errors}))
