#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang


from assets import  models
from userinfo.models import UserProfile
from api import serializer
from rest_framework import  serializers,viewsets,routers


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = serializer.UserSerializer
class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = serializer.AssetSerializer
class ManufactoryViewSet(viewsets.ModelViewSet):
    queryset = models.Manufactory.objects.all()
    serializer_class = serializer.ManfactorySerializer
