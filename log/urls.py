#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang


from django.conf.urls import url
from log import views
urlpatterns = [
    url(r'^assetslogs', views.assetslogs,name='assetslogs',),
    url(r'^executelogs', views.executelogs,name='executelogs',),
    url(r'^loginlogs', views.loginlogs,name='loginlogs',),
]