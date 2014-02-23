from django.conf.urls import include, patterns, url
from django.conf.urls.i18n import i18n_patterns

from django.conf import settings
from django.views.generic.base import TemplateView

from filebrowser.sites import site as filebrowserSite
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/manual/$', TemplateView.as_view(template_name='admin/manual.html')),
    url(r'^admin/rosetta/', include('rosetta.urls')),
    url(r'^admin/moderation/$', 'cadocms.views.admin_moderation'),
    url(r'^admin/clearcache/$', 'cadocms.views.admin_clearcache'),
    url(r'^admin/rebuildindex/$', 'cadocms.views.admin_rebuildindex'),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^ajax-upload/', include('ajax_upload.urls')),
    
    url(r'^accounts/extrafields/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<provider_id>\d+)$', 'cadocms.views.extrafields'),
    url(r'^api/children/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<parent_id>\d+)/$', 'cadocms.views.api_tree_children'),
    url(r'^api/path/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<item_id>\d+)/$', 'cadocms.views.api_tree_path'),
    url(r'^api/fullpath/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<item_id>\d+)/$', 'cadocms.views.api_tree_fullpath'),
    
    url(r'^api/image_uploader/$', 'cadocms.views.image_uploader'),
      
    url(r'^testsuite/$', 'cadocms.views.testsuite'),

    url(r'^admin/filebrowser/', include(filebrowserSite.urls)),

    url(r'^captcha/', include('captcha.urls')),
    url(r'^grappelli/', include('grappelli.urls')),   
    
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')), 
    url(r'^', include('grappelli.urls')),                      
)

if settings.HOST.CLASS == 'DEV':
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT,}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT,}),                    
    )

if settings.EXTRA_URLS:
    urlpatterns += patterns('', *settings.EXTRA_URLS)

for extra in settings.EXTRA_URLCONFS:
    #print extra
    extrapatterns = __import__(extra, globals(), locals(), ['urlpatterns'], -1) 
    urlpatterns += extrapatterns.urlpatterns
