# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-04 06:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='raidadaptor',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=200, verbose_name='名称'),
            preserve_default=False,
        ),
    ]
