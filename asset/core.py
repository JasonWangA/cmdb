#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang


import json
from django.core.exceptions import ObjectDoesNotExist
from asset import models
from django.utils import timezone


class Asset(object):
    def __init__(self,request):
        ##初始化request请求
        self.request = request
        ##必要检查字段：sn,asset_id,asset_type
        self.mandatory_fields = ['sn','asset_id','asset_type'] #must contains 'sn' , 'asset_id' and 'asset_type'
        self.field_sets = {
            'asset':['manufactory'],
            'server':['model','cpu_count','cpu_core_count','cpu_model','raid_type','os_type','os_distribution','os_release'],
            'networkdevice':[]
        }
        ##定义响应信息字典
        self.response = {
            'error':[],
            'info':[],
            'warning':[]
        }
        ##定义响应信息函数
    def response_msg(self,msg_type,key,msg):
        ##根据不同的报错类型写入不同的字典
        if msg_type in self.response:
            self.response[msg_type].append({key:msg})
        else:
            raise ValueError
        ##定义必要字段检查函数
    def mandatory_check(self,data,only_check_sn=False):
        ##遍历必要字段，判断client 端传来的是是否包含必要字段中，不在则加入报错提示
        for field in self.mandatory_fields:
            if field  not in data:
                self.response_msg('error','MandatoryCheckFailed', "The field [%s] is mandatory and not provided in your reporting data" % field)
        else:
            if self.response['error']:return False
        ##新加入的未经过审核的资产在资产列表中是查不到相应的资产字段，会产生报错信息，并给次对象添加waiting_approval字段，这是判断是否为新资产的重要标志
        try:
            if not only_check_sn:
                self.asset_obj = models.Asset.objects.get(id=int(data['asset_id']),sn=data['sn'])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
            return True
        except ObjectDoesNotExist as e:
            self.response_msg('error','AssetDataInvalid', "Cannot find asset object in DB by using asset id [%s] and SN [%s] " % (data['asset_id'],data['sn']))
            ##添加资产待批准属性
            self.waiting_approval = True
            return False

    def get_asset_id_by_sn(self):
        ##客户端第一次连接服务器的时候,并不知道自己的资产id,因此他会从系统获取资产id,此后再次返回数据给服务端
        '''When the client first time reports it's data to Server,it doesn't know it's asset id yet,so it will come to the server asks for the asset it first,then report the data again  '''
        ##从client端获取数据
        data = self.request.POST.get("asset_data")
        response = {}
        #如果获得数据
        if data:
            try:
                #加载数据,转换为字典
                data = json.loads(data)
                #检查必要字段是否已经存在,如果存在,则返回资产id,不存在则说明为新资产,未经审核,未写入数据库
                if self.mandatory_check(data,only_check_sn=True): #the asset is already exist in DB,just return it's asset id to client
                    response = {'asset_id': self.asset_obj.id}
                else:
                    #如果存在waiting_approval属性,则说明已经存入资产审批区,但是未做批准入库
                    if hasattr(self,'waiting_approval'):
                        response = {'needs_aproval': "this is a new asset,needs IT admin's approval to create the new asset id."}
                        self.clean_data = data
                        #将未批准数据存入资产批准临时审批表
                        self.save_new_asset_to_approval_zone()
                        print(response)
                    else:
                        response = self.response
            except ValueError as e:
                #如果不存在改实例对象,说明此资产不存在
                self.response_msg('error','AssetDataInvalid', str(e))
                response = self.response

        else:
            ##说明client端汇报的数据非法
            self.response_msg('error','AssetDataInvalid', "The reported asset data is not valid or provided")
            response = self.response
        return response

    def save_new_asset_to_approval_zone(self):
        #保存新资产到批准区
        '''When find out it is a new asset, will save the data into approval zone to waiting for IT admin's approvals'''
        asset_sn = self.clean_data.get('sn')
        asset_already_in_approval_zone = models.NewAssetApprovalZone.objects.get_or_create(sn=asset_sn,
                                                                                           data=json.dumps(self.clean_data),
                                                                                           manufactory=self.clean_data.get('manufactory'),
                                                                                           model=self.clean_data.get('model'),
                                                                                           asset_type=self.clean_data.get('asset_type'),
                                                                                           ram_size=self.clean_data.get('ram_size'),
                                                                                           cpu_model=self.clean_data.get('cpu_model'),
                                                                                           cpu_count=self.clean_data.get('cpu_count'),
                                                                                           cpu_core_count=self.clean_data.get('cpu_core_count'),
                                                                                           os_distribution=self.clean_data.get('os_distribution'),
                                                                                           os_release=self.clean_data.get('os_release'),
                                                                                           os_type=self.clean_data.get('os_type'),

                                                                                           )
        return True
    def data_is_valid(self):
        data = self.request.POST.get("asset_data")
        if data:
            try:
                data = json.loads(data)
                #获取数据,对必要字段包括sn,资产id,资产类型进行验证
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response['error']:
                    #若果验证后不存在报错信息,则返回true
                    return True
            except ValueError as e:
                #否则返回报错信息
                self.response_msg('error','AssetDataInvalid', str(e))
        else:
            self.response_msg('error','AssetDataInvalid', "The reported asset data is not valid or provided")

    def __is_new_asset(self):
        #如果资产对象中不包含客户端数据资产类型相关的反向查询方法如asset.server,说明只创建了资产表对象,并为创建其他关联表
        if not hasattr(self.asset_obj, self.clean_data['asset_type']):#new asset
            return True
        else:
            return False
    def data_inject(self):
        '''save data into DB,the data_is_valid() must returns True before call this function'''

        #self.reformat_components('slot',self.clean_data.get('ram'))
        #self.reformat_components('name',self.clean_data.get('nic'))
        #如果是新资产,创建新资产
        if self.__is_new_asset():
            print('\033[32;1m---new asset,going to create----\033[0m')
            self.create_asset()
        else:#asset already already exist , just update it
            #否则,资产已经存在,下一次,客户端再传过来,只更新数据即可
            print('\033[33;1m---asset already exist ,going to update----\033[0m')

            self.update_asset()

    def data_is_valid_without_id(self):
        '''when there's no asset id in reporting data ,goes through this function fisrt'''
        #如果客户端收集的数据中不存在资产id,则先运行次函数
        data = self.request.POST.get("asset_data")
        if data:
            try:
                data = json.loads(data)
                ##如果存在资产则查询资产,不存在则创建资产
                asset_obj = models.Asset.objects.get_or_create(sn=data.get('sn'),name=data.get('sn')) #push asset id into reporting data before doing the mandatory check
                #给资产添加资产id
                data['asset_id'] = asset_obj[0].id
                #检查数据的合法性
                self.mandatory_check(data)
                #将客户端传过来的数据保存在asset对象中
                self.clean_data = data
                if not self.response['error']:
                    return True
            except ValueError as e:
                self.response_msg('error','AssetDataInvalid', str(e))
        else:
            self.response_msg('error','AssetDataInvalid', "The reported asset data is not valid or provided")


    def reformat_components(self,identify_field,data_set):
        '''This function is used as workround for some components's data structor is big dict ,yet
        the standard structor is list,e.g:
        standard: [{
            "slot": "1I:1:1",
            "capacity": 300,
            "sn": "",
            "model": "",
            "enclosure": "0",
            "iface_type": "SAS"
        },
        {
            "slot": "1I:1:2",
            "capacity": 300,
            "sn": "",
            "model": "",
            "enclosure": "0",
            "iface_type": "SAS"
        }]
        but for some components such as ram:
        {"PROC 2 DIMM 1": {
            "model": "<OUT OF SPEC>",
            "capacity": 0,
            "sn": "Not Specified",
            "manufactory": "UNKNOWN"
        },}
        it uses key as identified field, the key is actually equals slot field in db model field, this unstandard
        data source should be dprecated in the future, now I will just reformat it as workround
        '''
        for k,data in data_set.items():
            data[identify_field] = k
    def __verify_field(self,data_set,field_key,data_type,required=True):
        ##验证客户端传来的资产数据对应的键值对是否存在
        field_val = data_set.get(field_key)
        if field_val:
            try:
                #存在,则试图保存为指定类型的数据
                data_set[field_key] = data_type(field_val)
            except ValueError as e:
                #捕捉异常,如果不能转换数据类型
                self.response_msg('error','InvalidField', "The field [%s]'s data type is invalid, the correct data type should be [%s] " % (field_key,data_type) )

        elif required == True:
            #缺少必要字段则报错
                self.response_msg('error','LackOfField', "The field [%s] has no value provided in your reporting data [%s]" % (field_key,data_set) )



    def create_asset(self):
        '''
        invoke asset create function according to it's asset type
        :return:
        '''
        #通过反射自动判断要调用创建资产的函数
        func = getattr(self,'_create_%s' % self.clean_data['asset_type'])
        create_obj =func()

    def update_asset(self):
        #通过映射自动创建要执行更行的函数
        func = getattr(self,'_update_%s' % self.clean_data['asset_type'])
        create_obj =func()

    def _update_server(self):
        #更新网卡,硬盘,内存,cpu等server信息
        """
            # >>> c.disk_set.select_related()[0].id
            1
            >>> c = models.Asset.objects.last()
        """
        #data_source 为客户端传来的数据,fk为多对多关联反向查询的关联字段,update_fields为要进行更新的字段,identify_field为可标示的字段,即为不变字段,如macaddress
        nic = self.__update_asset_component(data_source=self.clean_data['nic'],
                                            fk='nic_set',
                                            update_fields = ['name','sn','model','macaddress','ipaddress','netmask','bonding'],
                                            identify_field = 'macaddress'
                                            )
        disk = self.__update_asset_component(data_source=self.clean_data['physical_disk_driver'],
                                             fk='disk_set',
                                            update_fields = ['slot','sn','model','manufactory','capacity','iface_type'],
                                            identify_field = 'slot'
                                            )
        ram = self.__update_asset_component(data_source=self.clean_data['ram'],
                                             fk='ram_set',
                                            update_fields = ['slot','sn','model','capacity'],
                                            identify_field = 'slot'
                                            )
        cpu = self.__update_cpu_component()
        manufactory = self.__update_manufactory_component()

        server = self.__update_server_component()
    def _create_server(self):
        self.__create_server_info()
        self.__create_or_update_manufactory()

        self.__create_cpu_component()
        self.__create_disk_component()
        self.__create_nic_component()
        self.__create_ram_component()
        #定义创建资产成功后返回给前端信息
        log_msg = "Asset [<a href='/admin/assets/asset/%s/' target='_blank'>%s</a>] has been created!" % (self.asset_obj.id,self.asset_obj)
        self.response_msg('info','NewAssetOnline',log_msg )
    def __create_server_info(self,ignore_errs=False):
        try:
            #验证客户端传过来的信息的数据类型合法后,创建资产信息
            self.__verify_field(self.clean_data,'model',str)
            if not len(self.response['error']) or ignore_errs == True: #no processing when there's no error happend
                data_set = {
                    'asset_id' : self.asset_obj.id,
                    'raid_type': self.clean_data.get('raid_type'),
                    #'model':self.clean_data.get('model'),
                    'os_type':self.clean_data.get('os_type'),
                    'os_distribution':self.clean_data.get('os_distribution'),
                    'os_release':self.clean_data.get('os_release'),
                }
                #根据获取信息,创建与此资产id对应的server字段
                obj = models.Server(**data_set)
                obj.asset.model = self.clean_data.get('model')
                obj.save()
                return obj
        except Exception as e:
            #否则创建对象存在异常
            self.response_msg('error','ObjectCreationException','Object [server] %s' % str(e) )
    def __create_or_update_manufactory(self,ignore_errs=False):
        try:
            #验证客户端传过来的信息的数据类型合法后,创建资产信息
            self.__verify_field(self.clean_data,'manufactory',str)
            manufactory = self.clean_data.get('manufactory')
            if not len(self.response['error']) or ignore_errs == True: #no processing when there's no error happend
                #判断厂商是否存在
                obj_exist = models.Manufactory.objects.filter(manufactory=manufactory)
                if obj_exist:
                    obj = obj_exist[0]
                else:#create a new one
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                self.asset_obj.manufactory = obj
                self.asset_obj.save()
        except Exception as e:
            self.response_msg('error','ObjectCreationException','Object [manufactory] %s' % str(e) )
    def __create_cpu_component(self,ignore_errs=False):
        try:
            #验证客户端传过来的信息的数据类型合法后,创建资产信息
            self.__verify_field(self.clean_data,'model',str)
            self.__verify_field(self.clean_data,'cpu_count',int)
            self.__verify_field(self.clean_data,'cpu_core_count',int)
            if not len(self.response['error']) or ignore_errs == True: #no processing when there's no error happend
                data_set = {
                    'asset_id' : self.asset_obj.id,
                    'cpu_model': self.clean_data.get('cpu_model'),
                    'cpu_count':self.clean_data.get('cpu_count'),
                    'cpu_core_count':self.clean_data.get('cpu_core_count'),
                }

                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" %(self.asset_obj,data_set)
                self.response_msg('info','NewComponentAdded',log_msg)
                return obj
        except Exception as e:
            self.response_msg('error','ObjectCreationException','Object [cpu] %s' % str(e) )
    def __create_disk_component(self):
        disk_info = self.clean_data.get('physical_disk_driver')
        if disk_info:
            #遍历所有硬盘,校验数据类型是否合法
            for disk_item in disk_info:
                try:
                    #验证客户端传过来的信息的数据类型合法后,创建资产信息
                    self.__verify_field(disk_item,'slot',str)
                    self.__verify_field(disk_item,'capacity',float)
                    self.__verify_field(disk_item,'iface_type',str)
                    self.__verify_field(disk_item,'model',str)
                    if not len(self.response['error']): #no processing when there's no error happend
                        data_set = {
                            'asset_id' : self.asset_obj.id,
                            'sn': disk_item.get('sn'),
                            'slot':disk_item.get('slot'),
                            'capacity':disk_item.get('capacity'),
                            'model':disk_item.get('model'),
                            'iface_type':disk_item.get('iface_type'),
                            'manufactory':disk_item.get('manufactory'),
                        }
                        #数据合法,创建硬盘表
                        obj = models.Disk(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error','ObjectCreationException','Object [disk] %s' % str(e) )
        else:
                self.response_msg('error','LackOfData','Disk info is not provied in your reporting data' )
    def __create_nic_component(self):
        nic_info = self.clean_data.get('nic')
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item,'macaddress',str)
                    if not len(self.response['error']): #no processing when there's no error happend
                        data_set = {
                            'asset_id' : self.asset_obj.id,
                            'name': nic_item.get('name'),
                            'sn': nic_item.get('sn'),
                            'macaddress':nic_item.get('macaddress'),
                            'ipaddress':nic_item.get('ipaddress'),
                            'bonding':nic_item.get('bonding'),
                            'model':nic_item.get('model'),
                            'netmask':nic_item.get('netmask'),
                        }

                        obj = models.NIC(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error','ObjectCreationException','Object [nic] %s' % str(e) )
        else:
                self.response_msg('error','LackOfData','NIC info is not provied in your reporting data' )
    def __create_ram_component(self):
        ram_info = self.clean_data.get('ram')
        if ram_info:
            for ram_item in ram_info:
                try:
                    self.__verify_field(ram_item,'capacity',int)
                    if not len(self.response['error']): #no processing when there's no error happend
                        data_set = {
                            'asset_id' : self.asset_obj.id,
                            'slot': ram_item.get("slot"),
                            'sn': ram_item.get('sn'),
                            'capacity':ram_item.get('capacity'),
                            'model':ram_item.get('model'),
                        }

                        obj = models.RAM(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error','ObjectCreationException','Object [ram] %s' % str(e) )
        else:
                self.response_msg('error','LackOfData','RAM info is not provied in your reporting data' )

    def __update_server_component(self):
        #定义服务器要进行更新的字段
        update_fields = ['model','raid_type','os_type','os_distribution','os_release']
        #如果有资产对象有有server属性
        if hasattr(self.asset_obj,'server'):
            #对要更新的字段,将服务器保存的数据和客户端传来的数据进行对比
            self.__compare_componet(model_obj=self.asset_obj.server,
                                    fields_from_db=update_fields ,
                                    data_source=self.clean_data)
        else:
            #否则创建server信息
            self.__create_server_info(ignore_errs=True)

    def __update_manufactory_component(self):
        self.__create_or_update_manufactory(ignore_errs=True)

    def __update_cpu_component(self):
        update_fields = ['cpu_model','cpu_count','cpu_core_count']
        if hasattr(self.asset_obj,'cpu'):
            self.__compare_componet(model_obj=self.asset_obj.cpu,
                                    fields_from_db=update_fields,
                                    data_source=self.clean_data)
        else:
            self.__create_cpu_component(ignore_errs=True)
    def __update_asset_component(self,data_source,fk,update_fields,identify_field=None):
        '''
        data_source: the data source of this component from reporting data
        fk: which key to use to find the connection between main Asset obj and each asset component
        update_fields: what fields in DB will be compared and updated
        identify_field: use this field to identify each component of an Asset , if set to None,means only use asset id to identify
         '''
        print(data_source,update_fields,identify_field)
        try:
            #获取该对象反向关联的字段对象,如server一对一关联资产,disk外键关联改资产id,则通过 obj.disk_set.selected_related()反向获取关联的disk信息
            component_obj = getattr(self.asset_obj,fk)
            #如果反向字段有select_related属性,说明有相关的硬件
            if hasattr(component_obj,'select_related'): # this component is reverse m2m relation with Asset model
                objects_from_db = component_obj.select_related()
                #遍历从数据源中获取的对象
                for obj in objects_from_db:
                    #获取客户端唯一不变的字段数据,如对于网卡不变的值为mac地址
                    key_field_data= getattr(obj,identify_field)
                    #use this key_field_data to find the relative data source from reporting data
                    if type(data_source) is list:
                        #如果数据源为列表,遍历数据源中的每一个数据
                        for source_data_item  in data_source:
                            #如果客户端传来的数据的唯一不变字段与服务器端的对应的key一致,则此字段为要比较的字段
                            key_field_data_from_source_data = source_data_item.get(identify_field)
                            if key_field_data_from_source_data:
                                if key_field_data == key_field_data_from_source_data: #find the matched source data for this component,then should compare each field in this component to see if there's any changes since last update
                                   self.__compare_componet(model_obj=obj,fields_from_db=update_fields,data_source=source_data_item)
                                   break #must break ast last ,then if the loop is finished , logic will goes for ..else part,then you will know that no source data is matched for by using this key_field_data, that means , this item is lacked from source data, it makes sense when the hardware info got changed. e.g: one of the RAM is broken, sb takes it away,then this data will not be reported in reporting data
                            else: #key field data from source data cannot be none
                                self.response_msg('warning','AssetUpdateWarning',"Asset component [%s]'s key field [%s] is not provided in reporting data " % (fk,identify_field) )

                        else:#couldn't find any matches, the asset component must be broken or changed manually
                            print('\033[33;1mError:cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!\033[0m' %(key_field_data) )
                            self.response_msg("error","AssetUpdateWarning","Cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!" %(key_field_data))
                    elif type(data_source) is dict :
                        for key,source_data_item  in data_source.items():
                            key_field_data_from_source_data = source_data_item.get(identify_field)
                            if key_field_data_from_source_data:
                                if key_field_data == key_field_data_from_source_data: #find the matched source data for this component,then should compare each field in this component to see if there's any changes since last update
                                   #找到对应的字段,无须继续遍历,退出循环
                                   self.__compare_componet(model_obj=obj,fields_from_db=update_fields,data_source=source_data_item)
                                   break #must break ast last ,then if the loop is finished , logic will goes for ..else part,then you will know that no source data is matched for by using this key_field_data, that means , this item is lacked from source data, it makes sense when the hardware info got changed. e.g: one of the RAM is broken, sb takes it away,then this data will not be reported in reporting data
                            else: #key field data from source data cannot be none
                                #如果客户端传来的数据不存在,则返回告警信息
                                self.response_msg('warning','AssetUpdateWarning',"Asset component [%s]'s key field [%s] is not provided in reporting data " % (fk,identify_field) )

                        else:
                            #如果遍历后未找到对应的key相关的信息,则说明不存在相关的资产信息
                            #couldn't find any matches, the asset component must be broken or changed manually
                            print('\033[33;1mWarning:cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!\033[0m' %(key_field_data) )
                    else:
                        print('\033[31;1mMust be sth wrong,logic should goes to here at all.\033[0m')
                #最后,对数据库中的数据和客户端传过来的数据进行交际,差集的比较,这种情况主要是针对客户端数据有新增资产或删除或资产的情况
                #compare all the components from DB with the data source from reporting data
                self.__filter_add_or_deleted_components(model_obj_name=component_obj.model._meta.object_name, data_from_db=objects_from_db,data_source=data_source,identify_field=identify_field)

            else:#    this component is reverse fk relation with Asset model
                pass
        except ValueError as e:
            print('\033[41;1m%s\033[0m' % str(e) )

    def __filter_add_or_deleted_components(self,model_obj_name,data_from_db,data_source,identify_field):
        '''This function is filter out all  component data in db but missing in reporting data, and all the data in reporting data but not in DB'''
        print(data_from_db,data_source,identify_field)
        data_source_key_list = [] #save all the idenified keys from client data,e.g: [macaddress1,macaddress2]
        #如果client端提供的数据是一个列表,将client端的key加入列表中去
        if type(data_source) is list:
            for data in data_source:
                data_source_key_list.append(data.get(identify_field))
        elif type(data_source) is dict:
            for key,data in data_source.items():
                if data.get(identify_field):
                    data_source_key_list.append(data.get(identify_field))
                else:#workround for some component uses key as identified field e.g: ram
                    data_source_key_list.append(key)
        print('-->identify field [%s] from db  :',data_source_key_list)
        print('-->identify[%s] from data source:',[getattr(obj,identify_field) for obj in data_from_db] )
        #将客户端的数据源列表转换为元组
        data_source_key_list = set(data_source_key_list)
        #将数据库中对应的字段转换为元组
        data_identify_val_from_db = set([getattr(obj,identify_field) for obj in data_from_db])
        data_only_in_db= data_identify_val_from_db - data_source_key_list #delete all this from db
        data_only_in_data_source=  data_source_key_list - data_identify_val_from_db #add into db
        print('\033[31;1mdata_only_in_db:\033[0m' ,data_only_in_db)
        print('\033[31;1mdata_only_in_data source:\033[0m' ,data_only_in_data_source)
        self.__delete_components(all_components=data_from_db, delete_list = data_only_in_db, identify_field=identify_field )
        if data_only_in_data_source:
            self.__add_components(model_obj_name=model_obj_name,all_components=data_source, add_list = data_only_in_data_source, identify_field=identify_field )

    def __add_components(self,model_obj_name,all_components,add_list,identify_field ):
        model_class = getattr(models,model_obj_name)
        will_be_creating_list = []
        print('--add component list:',add_list)
        if type(all_components) is list:
            for data in all_components:
                if data[identify_field] in add_list:
                    #print data
                    will_be_creating_list.append(data)
        elif type(all_components) is dict:
            for k,data in all_components.items():
                #workround for some components uses key as identified field ,e.g ram
                if data.get(identify_field):
                    if data[identify_field]  in add_list:
                        #print k,data
                        will_be_creating_list.append(data)
                else: #if the identified field cannot be found from data set,then try to compare the dict key
                    if k in add_list:
                        data[identify_field] = k #add this key into dict , because this dict will be used to create new component item in DB
                        will_be_creating_list.append(data)

        #creating components
        try:
            for component in will_be_creating_list:
                data_set = {}
                for field in model_class.auto_create_fields:
                    data_set[field] = component.get(field)
                data_set['asset_id'] = self.asset_obj.id
                obj= model_class(**data_set)
                obj.save()
                print('\033[32;1mCreated component with data:\033[0m', data_set)
                log_msg = "Asset[%s] --> component[%s] has justed added a new item [%s]" %(self.asset_obj,model_obj_name,data_set)
                self.response_msg('info','NewComponentAdded',log_msg)
                log_handler(self.asset_obj,'NewComponentAdded',self.request.user,log_msg,model_obj_name)

        except Exception as e:
            print("\033[31;1m %s \033[0m"  % e )
            log_msg = "Asset[%s] --> component[%s] has error: %s" %(self.asset_obj,model_obj_name,str(e))
            self.response_msg('error',"AddingComponentException",log_msg)
    def __delete_components(self,all_components, delete_list , identify_field ):
        '''All the objects in delete list will be deleted from DB'''
        deleting_obj_list = []
        print('--deleting components',delete_list,identify_field)
        for obj in all_components:
            val  = getattr(obj,identify_field)
            if val in delete_list:
                deleting_obj_list.append(obj)

        for i in deleting_obj_list:
            log_msg = "Asset[%s] --> component[%s] --> is lacking from reporting source data, assume it has been removed or replaced,will also delete it from DB" %(self.asset_obj,i)
            self.response_msg('info','HardwareChanges',log_msg)
            log_handler(self.asset_obj,'HardwareChanges',self.request.user,log_msg,i)
            i.delete()


    def __compare_componet(self,model_obj,fields_from_db,data_source):
        print('---going to compare:[%s]' % model_obj,fields_from_db)
        print('---source data:', data_source)
        #遍历要比较的数据库字段
        for field in fields_from_db:
            #从数据库中获取对应字段的值
            val_from_db = getattr(model_obj,field)
            #从客户端或浏览器获取相关的字段信息
            val_from_data_source = data_source.get(field)
            #如果clinet传过来的对应字段存在,则根据数据库中存在的数据类型,将client传过来的对应的数据进行格式转换,便于两者比较
            if val_from_data_source:
                #if type(val_from_db) is unicode:val_from_data_source = unicode(val_from_data_source)#no unicode in py3
                #if type(val_from_db) in (int,long):val_from_data_source = int(val_from_data_source) #no long in py3
                if type(val_from_db) in (int,):val_from_data_source = int(val_from_data_source)
                elif type(val_from_db) is float:val_from_data_source = float(val_from_data_source)
                elif type(val_from_db) is str:val_from_data_source = str(val_from_data_source).strip()
                if val_from_db == val_from_data_source:# this field haven't changed since last update
                    pass
                    #print '\033[32;1m val_from_db[%s]  == val_from_data_source[%s]\033[0m' %(val_from_db,val_from_data_source)
                else:
                    #如果两者数据不相同,则将客户端数据更新到服务器
                    print('\033[34;1m val_from_db[%s]  != val_from_data_source[%s]\033[0m' %(val_from_db,val_from_data_source),type(val_from_db),type(val_from_data_source) ,field)
                    db_field = model_obj._meta.get_field(field)
                    db_field.save_form_data(model_obj, val_from_data_source)
                    model_obj.update_date = timezone.now()
                    model_obj.save()
                    #将创建的日志记录保存下来
                    log_msg = "Asset[%s] --> component[%s] --> field[%s] has changed from [%s] to [%s]" %(self.asset_obj,model_obj,field,val_from_db,val_from_data_source)
                    self.response_msg('info','FieldChanged',log_msg)
                    log_handler(self.asset_obj,'FieldChanged',self.request.user,log_msg,model_obj)
            else:
                #如果客户端传来的数据中不包含要更新的信息,则提示此情况
                self.response_msg('warning','AssetUpdateWarning',"Asset component [%s]'s field [%s] is not provided in reporting data " % (model_obj,field) )

        model_obj.save()


def log_handler(asset_obj,event_name,user,detail,component=None):
    '''    (1,u'硬件变更'),
        (2,u'新增配件'),
        (3,u'设备下线'),
        (4,u'设备上线'),'''
    log_catelog = {
        1 : ['FieldChanged','HardwareChanges'],
        2 : ['NewComponentAdded'],
    }
    if not user.id:
        pass
        user = models.UserProfiles.objects.filter(is_admin=True).last()
    event_type = None
    for k,v in log_catelog.items():
        if event_name in v:
            event_type = k
            break
    log_obj = models.EventLog(
        name =event_name,
        event_type = event_type,
        asset_id = asset_obj.id,
        component = component,
        detail = detail,
        user_id = user.id
    )

    log_obj.save()