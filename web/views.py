# -*- coding: utf-8 -*-
##############################################################################
# FileName: web\views.py
# Description: 公共模块
# Version: V1.0
# Author: 
# Function List:
#   1. 
# History:
#	<author>		<time>		<version>		<desc>
#			    2016/8/16	V1.0			创建文件
###############################################################################
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, render_to_response
from django.template import RequestContext, Context, Template,loader
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth import authenticate
import django.contrib.sessions
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth

import guardian
from guardian.models import UserObjectPermission
from guardian.models import GroupObjectPermission
from guardian.shortcuts import get_perms, assign, remove_perm, get_objects_for_user
from framework.models import *
from framework.views import *
import traceback
from logger.views import logger
import json


@csrf_exempt    
def login(request):
    """
    加载登录页面 && 登录
    """    
    try:
        #user = auth.authenticate(username="admin", password="huaanxinxi")
        ##user = auth.authenticate(username="test", password="123456")
        #auth.login(request, user)        
        if request.method == "GET":
            if request.user.is_authenticated():
                if request.user.is_superuser:
                    return HttpResponseRedirect("usermanage")
                else:
                    #return HttpResponseRedirect("data/missionview")
                    return HttpResponseRedirect("data/auctionview")
            return render(request,"login.html",{})
        elif request.method == "POST":
            username=request.POST['username']
            password=request.POST['password']
            try:
                checkuser = User.objects.get(username = username)
            except Exception,e:
                if str(e).find("does not exist"):
                    return render(request,"login.html",{"loginfailed":u"用户名不存在"})    
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request,user)
                if user.is_superuser:
                    return HttpResponseRedirect("usermanage")
                else:
                    #return HttpResponseRedirect("data/missionview")
                    return HttpResponseRedirect("data/auctionview")
            else:
                return render(request,"login.html",{"loginfailed":u"密码错误"})  

    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        raise Http404        

@csrf_exempt
def logout(request):
    """
    退出登录
    """
    try:
        if request.user.is_authenticated():
            auth.logout(request)

        return HttpResponseRedirect("/")  
    except:
        logger.info(traceback.format_exc())
        #print traceback.format_exc()
        raise Http404

