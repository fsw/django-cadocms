from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

EXTRAFIELDS_HTML_WIDGET = u"""
<script type="text/javascript">
if (jQuery != undefined) {
    var django = {
        'jQuery':jQuery,
    }
}
(function($){
$(document).ready(function($) {
document.registerExtraField('unravelling.Item', '%(name)s', '%(provider)s');
});})(django.jQuery);</script>
"""

class ExtraFieldsValuesWidget(forms.Textarea):
    class Media:
        js = (settings.STATIC_URL + 'extrafields.js', )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ExtraFieldsValuesWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ExtraFieldsValuesWidget, self).render(name, value, attrs)
        #TODO:
        provider = 'category'
        return rendered + mark_safe(EXTRAFIELDS_HTML_WIDGET % {
                            'value': value, 'name': name, 'provider': provider})
        
