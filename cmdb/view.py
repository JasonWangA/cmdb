#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
# Create your views here.
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.core.exceptions import ObjectDoesNotExist
import django
from asset.dashboard import AssetDashboard
from django.contrib.auth.decorators import login_required


@login_required
def index(request):

    return render(request,'index.html',)



def acc_login(request):
    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        print(user)
        if user is not None:
            #使用自带认证登录
            login(request,user)
            #登录成功返回首页
            username = request.POST.get('username')
            return HttpResponseRedirect('/')
        else:
            #登录失败
            login_err = "Wrong username or password!"
            print(login_err)
            #返回错误消息
            return render(request,'login.html',{'login_err': 'Wrong username or password!'})
    else:
        return render(request, 'login.html')

#退出返回登录页
def acc_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')

