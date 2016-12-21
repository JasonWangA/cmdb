# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-29 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofiles',
            name='valid_begin_time',
            field=models.DateField(blank=True, null=True, verbose_name='账户生效日期'),
        ),
        migrations.AlterField(
            model_name='userprofiles',
            name='valid_end_time',
            field=models.DateField(blank=True, null=True, verbose_name='账户失效日期'),
        ),
    ]
