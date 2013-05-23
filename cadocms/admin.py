from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from models import StaticPage, Setting, Moderated, MODERATION_STATUS, Chunk
from django import forms
from django.conf import settings
import reversion

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

class StaticPageAdmin(reversion.VersionAdmin):
    form = StaticPageForm
    fieldsets = (
                 (None, {'fields': ('url', 'title', 'content', 'seo_title', 'seo_keywords', 'seo_description')}),
    )
    list_display = ('url', 'title')
    search_fields = ('url', 'title')

    
class SettingAdmin(reversion.VersionAdmin):
    list_display = ('__str__', 'description',)
    list_display_links = ('__str__',)
    fieldsets = (
        (None, {
            'fields': ('key', 'description', 'value')
        }),
    )
    readonly_fields=('key', 'description',)
    
    def has_add_permission(self, request):
        return False
    
    def get_actions(self, request):
        actions = super(SettingAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

class ChunkAdmin(reversion.VersionAdmin):
    list_display = ('__str__',)
    list_display_links = ('__str__',)
    fieldsets = (
        (None, {
            'fields': ('key', 'body')
        }),
    )
    readonly_fields=('key',)
    
    def has_add_permission(self, request):
        return False
    
    def get_actions(self, request):
        actions = super(ChunkAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


def approve_moderated(modeladmin, request, queryset):
    for obj in queryset:
        obj.moderation_status = MODERATION_STATUS['OK']
        obj.save()

approve_moderated.short_description = "Approve selected moderated objects"


def reject_moderated(modeladmin, request, queryset):
    for obj in queryset:
        obj.moderation_status = MODERATION_STATUS['REJECTED']
        obj.save()

reject_moderated.short_description = "Reject selected moderated objects"


class ModeratedAdmin(admin.ModelAdmin):
    actions = [reject_moderated, approve_moderated]
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(ModeratedAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def queryset(self, request):
        return self.model.objects.filter(moderation_status__in=[MODERATION_STATUS['NEW'],MODERATION_STATUS['MODIFIED']])


def add_moderated_admin(model, name = 'moderate'):
    class  Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, ModeratedAdmin)
    return ModeratedAdmin


