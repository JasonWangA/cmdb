# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-01 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0002_auto_20161129_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofiles',
            name='valid_end_time',
            field=models.DateField(blank=True, verbose_name='账户失效日期'),
        ),
    ]
