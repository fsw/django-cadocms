import inspect

from django.conf.urls import include, patterns, url
from django.shortcuts import redirect
from django.conf import settings
from django.views.generic.base import TemplateView

from filebrowser.sites import site as filebrowserSite
from django.contrib import admin
admin.autodiscover()

from views import admin_moderation

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT,}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT,}),
    url(r'^admin/manual/$', TemplateView.as_view(template_name='admin/manual.html')),
    url(r'^admin/rosetta/', include('rosetta.urls')),
    url(r'^admin/moderation/$', admin_moderation),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^extrafields/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<provider_id>\d+)$', 'cadocms.views.extrafields'),
    url(r'^api/children/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<parent_id>\d+)$', 'cadocms.views.api_tree_children'),
    url(r'^api/path/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<item_id>\d+)$', 'cadocms.views.api_tree_path'),
    url(r'^api/fullpath/(?P<model>[A-Za-z0-9\-\.\_]*)/(?P<item_id>\d+)$', 'cadocms.views.api_tree_fullpath'),
      
    url(r'^testsuite/$', 'cadocms.views.testsuite'),

    url(r'^admin/filebrowser/', include(filebrowserSite.urls)),

    url(r'^captcha/', include('captcha.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
                      
)



"""
def Urls():
    
    def getPatterns(self):
        print "ASDFADSF"
        return pattrns() 
"""

