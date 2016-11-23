#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
from django.conf.urls import url
from assets import views
urlpatterns = [
    #列表展示
    url(r'^assetslist/', views.assetslist,name='assetslist',),
    url(r'^assetsarea', views.assetsarea,name='assetsarea',),
    url(r'^netlist', views.netlist,name='netlist',),
    url(r'^iplist', views.iplist,name='iplist',),
    url(r'^modellist/(\d+)', views.modellist,name='modellist',),
    url(r'^cabinet/(\d+)', views.cabinet,name='cabinet',),
    url(r'^idcasset/(\d+)', views.idcasset,name='idcasset',),
    #添加
    url(r'^addarea', views.addarea,name='addarea',),
    #详细信息
    url(r'^hostdetail/(\d+)', views.hostdetail,name='hostdetail',),
    #服务器更新
    url(r'^hostupdate', views.hostupdate,name='hostupdate',),
    url(r'^roomdetail/(\d+)', views.roomdetail,name='roomdetail',),
    #编辑
    url(r'^compilesarea/(\d+)', views.compiles_area,name='compilesarea',),
]
