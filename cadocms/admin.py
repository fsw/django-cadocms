from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from models import StaticPage, Setting, Moderated, MODERATION_STATUS, Chunk, ModerationReason
from django import forms
from django.conf import settings

#from modeltranslation.models import autodiscover

from modeltranslation.admin import TranslationAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import unquote, quote
from django.core.urlresolvers import reverse

import reversion

class ModeratedAdmin(reversion.VersionAdmin):
    object_history_template = "admin/moderated_history.html"

    def history_view(self, request, object_id, extra_context=None):
        
        if not self.has_change_permission(request):
            raise PermissionDenied
        object_id = unquote(object_id) # Underscores in primary key get quoted to "_5F"
        opts = self.model._meta
        action_list = [
            {
                "revision": version.revision,
                "url": reverse("%s:%s_%s_revision" % (self.admin_site.name, opts.app_label, opts.module_name), args=(quote(version.object_id), version.id)),
            }
            for version
            in self._order_version_queryset(self.revision_manager.get_for_object_reference(
                self.model,
                object_id,
            ).select_related("revision__user"))
        ]
        # Compile the context.
        full_action_list = []
        
        for log_action in LogEntry.objects.filter(
                object_id=object_id,
                content_type__id__exact=ContentType.objects.get_for_model(self.model).id
            ).select_related().order_by('action_time'):
            while (len(action_list) and (log_action.action_time > action_list[0]['revision'].date_created)):
                full_action_list.append(action_list.pop(0))
            full_action_list.append({"log":log_action})
            #print len(action_list)
        while (len(action_list)):
            full_action_list.append(action_list.pop(0))
        
        context = {"action_list": full_action_list}
            

        context.update(extra_context or {})
        return super(reversion.VersionAdmin, self).history_view(request, object_id, context)
    
        return super(ModeratedAdmin, self).history_view(request, object_id, context)

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
        for StaticPageClass in StaticPage.__subclasses__():
            same_url = StaticPageClass.objects.filter(url=url)
            if self.instance.pk:
                same_url = same_url.exclude(pk=self.instance.pk)

            if same_url.all().exists():
                raise forms.ValidationError('Flatpage with url %(url)s already exists' % {'url': url})
        
        return super(StaticPageForm, self).clean()

class StaticPageAdmin(reversion.VersionAdmin, TranslationAdmin):
    form = StaticPageForm
    #fieldsets = (
    #             (None, {'fields': ('url', 'title', 'content', 'seo_title', 'seo_keywords', 'seo_description')}),
    #)
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

class ChunkAdmin(reversion.VersionAdmin, TranslationAdmin):
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

"""

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

"""
