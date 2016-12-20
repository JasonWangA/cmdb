from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from assets import models
from assets import forms,admin
from assets import assets_list
from django.core.paginator import  Paginator,EmptyPage,PageNotAnInteger
from assets import core,tables
import json
# Create your views here.
@login_required
def assetslist(request):
    print(request)
    asset_obj_list = tables.table_filter(request, admin.AssetAdmin, models.Asset)
    # asset_obj_list = models.Asset.objects.all()
    print("asset_obj_list:", asset_obj_list)
    order_res = tables.get_orderby(request, asset_obj_list, admin.AssetAdmin)
    print('----->',order_res)
    paginator = Paginator(order_res[0], admin.AssetAdmin.list_per_page)

    page = request.GET.get('page')
    try:
        asset_objs = paginator.page(page)
    except PageNotAnInteger:
        asset_objs = paginator.page(1)
    except EmptyPage:
        asset_objs = paginator.page(paginator.num_pages)

    table_obj = tables.TableHandler(request,
                                    models.Asset,
                                    admin.AssetAdmin,
                                    asset_objs,
                                    order_res
                                    )
    print(table_obj.admin_class.list_display)

    return render(request, 'assets/assetlist.html', {'table_obj': table_obj,
                                                  'paginator': paginator})
#机房列表
@login_required
def assetsarea(request):
    idclist = models.IDC.objects.all()
    paginator = Paginator(idclist,10)
    page = request.GET.get('page')
    try:
        idclist_obj = paginator.page(page)
    except PageNotAnInteger:
        idclist_obj = paginator.page(1)
    except EmptyPage:
        idclist_obj = paginator.page(paginator.num_pages)
    return render(request,'assets/assetsarea.html',{'idclist':idclist_obj})

#模块列表
def modellist(request,func):
    pass
    return HttpResponseRedirect('/assets/assetsarea/')
#机柜列表
def cabinet(request,func):
    pass
    return HttpResponseRedirect('/assets/assetsarea/')
#网络设备列表
def netlist(request):
    return render(request,'assets/networklist.html')
#ip列表
def iplist(request):
    pass
    return HttpResponseRedirect('/assets/assetsarea/')
#机房相关资产
def idcasset(request):
    pass
    return HttpResponseRedirect('/assets/assetsarea/')
#添加机房功能
# @login_required
def addarea(request):
    form = forms.IDCForm()
    if request.method == 'POST':
        form = forms.IDCForm(request.POST,request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            new_article_obj = models.IDC(**form_data)
            new_article_obj.save()
            return HttpResponseRedirect('/assets/assetsarea/')
    return render(request,'assets/addarea.html',{'formidc':form})
#编辑机房功能
@login_required
def compiles_area(request,func):
    obj = models.IDC.objects.get(id=int(func))
    if request.method == 'POST':
        formdata = forms.IDCForm(request.POST,instance=obj)
        if formdata.is_valid():
            formdata.save()
            return HttpResponseRedirect('/assets/assetsarea/')
    form = forms.IDCForm(instance=obj)
    if form.is_valid():
        form.save()
    return render(request,'assets/addarea.html',{'formidc':form})
#机房详细信息
@login_required
def roomdetail(request,func):
    if request.method == 'GET':
        obj = models.IDC.objects.get(id=func)
        return render(request,'assets/roomdetail.html',{'form':obj})
#服务器详细资产信息
# @login_required
def hostdetail(request,page):
    if request.method == 'GET':
        obj = models.Asset.objects.get(id=page)
        return render(request,'assets/hostdetail.html',{'assets':obj})
#服务器更新功能
@login_required
def hostupdate(request):
    if request.method == 'POST':
        func = int(json.loads(request.POST.get('updateid')))
        if func:
            obj = models.Asset.objects.get(id=func)
            hostname = obj.name
            print(hostname)
            try:
                Asset = core.Assets(name=hostname)
                Asset.initialize()
                Asset.data_inject()
                return HttpResponse('ok')
            except:
                return HttpResponse('no')
