from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.widgets import ClearableFileInput
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile

import urllib2, os

EXTRAFIELDS_HTML_WIDGET = u"""
<script type="text/javascript">
if (typeof document.extraFieldsQueue === 'undefined') {
    document.extraFieldsQueue = new Array();
}
document.extraFieldsQueue.push(['%(url)s', '%(name)s', '%(provider)s']);
</script>
"""

class ExtraFieldsValuesWidget(forms.Textarea):
    class Media:
        js = (settings.STATIC_URL + 'cadocms/extrafields.js', )

    def __init__(self, language=None, attrs=None, provider_field='PROVIDER_FIELD', model_name = 'MODEL_NAME'):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.provider_field = provider_field
        self.model_name = model_name
        #print '__INIT WIDGET %s %s' % (self.model_name, self.provider_field)
        super(ExtraFieldsValuesWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ExtraFieldsValuesWidget, self).render(name, value, attrs)
        
        #TODO:
        #provider = 'category';
        #model = 'unravelling.Item';
        print 'RENDERING WIDGET %s %s' % (self.model_name, self.provider_field)
        return rendered + mark_safe(EXTRAFIELDS_HTML_WIDGET % {
                            'url': reverse('cadocms.views.extrafields', kwargs={'model':self.model_name, 'provider_id':0}),
                            'value': value,
                            'name': name,
                            'provider': self.provider_field})

class HTMLFieldWidget(forms.Textarea):
    
    class Media:
        js = (
              settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'js/tinymce_setup.js',
        )
        
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'mceEditor'
        return super(HTMLFieldWidget, self).render(name, value, attrs)

class HTMLFieldWidgetTrivial(forms.Textarea):
    
    class Media:
        js = (
              settings.STATIC_URL + 'grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              settings.STATIC_URL + 'js/tinymce_setup_trivial.js',
        )
        
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'mceEditor'
        return super(HTMLFieldWidgetTrivial, self).render(name, value, attrs)


class UrlOrFileInput(ClearableFileInput):

    def render(self, name, value, attrs=None):
        parent = super(UrlOrFileInput, self).render(name, value, attrs)
        return parent + mark_safe('or paste URL: <input type="text" value="" name="%s_url"/>' % name)

    def value_from_datadict(self, data, files, name):
        upload = super(UrlOrFileInput, self).value_from_datadict(data, files, name)
        url = data.get('%s_url' % name, None)
        if url:
            #TODO support for non-jpgs (via PIL?)
            img_temp = NamedTemporaryFile(delete=True)
            try:
                img_temp.write(urllib2.urlopen(url).read())
            except:
                return upload
            img_temp.flush()
            img_temp.file.seek(0)
            size = os.fstat(img_temp.file.fileno()).st_size
            return InMemoryUploadedFile(img_temp, None, img_temp.name + '.jpg' , 'image/jpeg', size, None)
        #print url
        #print upload
        #print type(upload)
        return upload
