#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
from django.conf.urls import url
from userinfo import views
urlpatterns = [
    url(r'^group/$', views.group,name='group',),
    url(r'^user/$', views.user,name='user',),
    url(r'^(\w+)/adds/', views.adds,name='adds',),
    url(r'^compiles/(\w+)/(\d+)/', views.compiles,name='compiles',),
    url(r'^userdetail/(\d+)/', views.userdetail,name='userdetail',),
    url(r'^deletes/', views.deletes,name='deletes',),
]

