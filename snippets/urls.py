#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang


from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views
from rest_framework import routers, serializers, viewsets
from snippets.rest_viewset import  UserProfileViewSet,AssetViewSet
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'assets', AssetViewSet)
from snippets import views
# API endpoints
urlpatterns = format_suffix_patterns([
    # url(r'^$', views.api_root),

    url(r'^snippets/$',
        views.SnippetList.as_view(),
        name='snippet-list'),
    url(r'^snippets/(?P<pk>[0-9]+)/$',
        views.SnippetDetail.as_view(),
        name='snippet-detail'),
    url(r'^snippets/(?P<pk>[0-9]+)/highlight/$',
        views.SnippetHighlight.as_view(),
        name='snippet-highlight'),
    url(r'^users/$',
        views.UserList.as_view(),
        name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$',
        views.UserDetail.as_view(),
        name='user-detail'),
])

# Login and logout views for the browsable API
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^', include(router.urls)),
    url(r'^api_test',views.api_test,name='api_test'),
]