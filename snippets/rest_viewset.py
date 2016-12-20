#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
from assets import  models
from snippets import serializers
from rest_framework import routers, viewsets

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = serializers.AssetSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer

class BusinessUnitViewSet(viewsets.ModelViewSet):
    queryset =  models.BusinessUnit.objects.all()
    serializer_class = serializers.BusinessUnitSerializer


class ManufactoryViewSet(viewsets.ModelViewSet):
    queryset =  models.Manufactory.objects.all()
    serializer_class = serializers.ManufactorySerializer