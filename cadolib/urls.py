import os

from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.shortcuts import redirect
from django.conf import settings

from cadolib.views import extrafields

urls = patterns('',
    url(r'^extrafields/(?P<model>[A-Za-z0-9\-\.]*)/(?P<provider_id>\d+)$', 'cadolib.views.extrafields', name='cadolib_extrafields'),                      
)
