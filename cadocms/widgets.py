from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

EXTRAFIELDS_HTML_WIDGET = u"""
<script type="text/javascript">
if (jQuery != undefined) {
    var grp = {
        'jQuery':jQuery,
    }
}
(function($){
$(document).ready(function($) {
document.registerExtraField('%(url)s', '%(name)s', '%(provider)s');
});})(grp.jQuery);</script>
"""

class ExtraFieldsValuesWidget(forms.Textarea):
    class Media:
        js = (settings.STATIC_URL + 'extrafields.js', )

    def __init__(self, language=None, attrs=None, provider_field='PROVIDER_FIELD', model_name = 'MODEL_NAME'):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.provider_field = provider_field
        self.model_name = model_name
        super(ExtraFieldsValuesWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ExtraFieldsValuesWidget, self).render(name, value, attrs)
        
        #TODO:
        #provider = 'category';
        #model = 'unravelling.Item';
        print 'RENDERING FIELD %s %s' % (self.model_name, self.provider_field)
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