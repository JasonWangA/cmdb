from django.shortcuts import render,HttpResponsePermanentRedirect,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from log import models
from utils import core
import time
# Create your views here.
# @login_required
def index(request):
    return render(request,'base/_layout.html')



def a_login(request):
    #登录功能
    if request.method == 'POST':
        #根据django自带的用户认证取出数据
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        print('here')
        username = request.POST.get('username')
        print(username)
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
            return render(request, 'basic/login.html', {'login_err':login_err})
    #如果是get
    return render(request, 'basic/login.html')
#退出返回登录页
def a_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')