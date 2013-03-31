from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from models import StaticPage
from django import forms
from django.conf import settings

class StaticPageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
        help_text = _("Example: 'about/contact'"),
        error_message = _("This value must contain only letters, numbers,"
                          " dots, underscores, dashes, slashes or tildes."))

    class Meta:
        model = StaticPage

    def clean_url(self):
        url = self.cleaned_data['url']
        #if not url.startswith('/'):
        #    raise forms.ValidationError(ugettext("URL is missing a leading slash."))
        #if (settings.APPEND_SLASH and
        #    'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE_CLASSES and
        #    not url.endswith('/')):
        #    raise forms.ValidationError(ugettext("URL is missing a trailing slash."))
        return url

    def clean(self):
        url = self.cleaned_data.get('url', None)
        same_url = StaticPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if same_url.all().exists():
            raise forms.ValidationError('Flatpage with url %(url)s already exists' % {'url': url})

        return super(StaticPageForm, self).clean()

class StaticPageAdmin(admin.ModelAdmin):
    form = StaticPageForm
    fieldsets = (
                 (None, {'fields': ('url', 'title', 'content', 'seo_title', 'seo_keywords', 'seo_description')}),
    )
    list_display = ('url', 'title')
    search_fields = ('url', 'title')

class CommonMedia:
    js = (
      'https://ajax.googleapis.com/ajax/libs/dojo/1.6.0/dojo/dojo.xd.js',
      '/static/admin/editor.js',
    )
    css = {
      'all': ('/static/admin/editor.css',),
    }
    

admin.site.register(StaticPage, StaticPageAdmin, Media = CommonMedia)

