#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang


from django.conf.urls import url
from install import views
# Create your views here.
urlpatterns = [
    url(r'^salt_key', views.salt_key,name='salt_key',),
    url(r'^batchcmd', views.batchcmd,name='batchcmd',),
    url(r'^batchfile', views.batchfile,name='batchfile',),
    url(r'^remote', views.remote,name='remote',),
    url(r'^update', views.update,name='update',),
    url(r'^allowkey', views.allowkey,name='allowkey',),
    url(r'^deletekey', views.deletekey,name='deletekey',),
]
