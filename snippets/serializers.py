#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang

from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User
from assets import models
"""
class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
    owner = serializers.ReadOnlyField(source='owner.username')

    def create(self, validated_data):

        #Create and return a new `Snippet` instance, given the validated data.

        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):

        #Update and return an existing `Snippet` instance, given the validated data.

        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance


from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'snippets')
"""
class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        # model = User
        model = models.UserProfile
        # fields = ('url', 'id', 'username', 'snippets')
        fields = ('name','id','email','phone')

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('id','name','asset_type','business_unit','sn','manufactory','management_ip')
        depth = 2

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessUnit
        fields = ('parent_unit', 'name', 'id')


#class ManufactorySerializer(serializers.HyperlinkedModelSerializer):
class ManufactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manufactory
        fields = ('manufactory', 'id')
