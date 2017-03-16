#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PythonPie <contact@pythonpie.com>
# Copyright (c) 2015 - THSTACK <contact@thstack.com>

from django.conf.urls import include, url
from django.contrib import admin

from BES.apphome import views
from django.conf.urls import handler404, handler500

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.index, name="page_index"),
    url(r'^cpu/$', views.cpu, name="page_cpu"),
    url(r'^mem/$', views.mem, name="page_mem"),
    url(r'^io/$', views.io, name="page_io"),
    url(r'^net/$', views.net, name="page_net"),

    url(r'^data/', include('BES.appdata.urls')),
]


