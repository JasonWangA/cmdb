#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang

import platform
import psutil
import django
import os
from cmdb import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()

