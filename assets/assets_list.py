#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import django
import os
from cmdb import settings
from django.core.exceptions import ObjectDoesNotExist
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()
from assets import models

def fetch_asset_list():
    asset_list = models.Asset.objects.all()
    print(asset_list)
    data_list = []
    for obj in asset_list:
        print(hasattr(obj,'server'))
        # if hasattr(obj,'server') or hasattr(obj,'networkdevice'):
        if hasattr(obj,'asset_type'):
            if obj.asset_type == 'server':
                print('here')
                data = {
                        'id': obj.id,
                        'name': obj.name,
                        'asset_type':obj.asset_type,
                        'status': obj.status,
                        'management_ip': obj.management_ip,
                        'sn': obj.sn,
                        'contact': obj.contract_id,
                        'manufacture': obj.manufactory.manufactory,
                        'idc': None if not obj.idc else obj.idc.model.idc.name,
                        'cab_name': obj.idc.name,
                        'business_unit': None if not obj.business_unit else obj.business_unit.name,
                        'os_release':obj.server.os_release,
                         'cpu_model' : None if not obj.cpu else obj.cpu.cpu_model,
                         'cpu_core_count' : None if not obj.cpu else obj.cpu.cpu_core_count,
                         'ram_size': sum([i.capacity if i.capacity else 0 for i in obj.ram_set.select_related()]),
                        'disk_size': sum([i.capacity if i.capacity else 0 for i in obj.disk_set.select_related()]),
                }
                print(data_list.append(data))
    return  data_list


if __name__ == '__main__':
    data_list = fetch_asset_list()
    print(data_list)