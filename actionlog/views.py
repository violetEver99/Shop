# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.template import RequestContext, Context, Template,loader
from django.http import Http404
from django.contrib import auth
from django.contrib.auth.models import User,Permission,Group
import django.contrib.sessions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
# Create your views here.
import traceback
from django.db import transaction
import os
import re
import json
import logging
import time
import datetime
from django.db.models.functions import Lower
from logger.views import logger
from framework.views import *
from .models import userActionLog

# Create your views here.
@csrf_exempt
@login_required
def actionlog(request):
    """操作日志"""
    try:
        if not has_perm_log(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")           
        if request.method == "GET":
            menu=getMenu(request)
            return HttpResponse(loader.get_template("actionlog.html").render({"contexts":menu,"request":request}))
    except:
        logger.debug(traceback.format_exc())
        raise Http404      
    
    
@csrf_exempt
@login_required
def logManage(request):
    try:
        if not has_perm_log(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")           
        if request.method == "POST":
            op = request.POST.get("op")
            return (op == "get" and getLog(request)) or (op == "delete" and delLog(request))

    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())
        
def delLog(request):
    try:
        idstring = request.POST["ids"]
        userActionLog.objects.extra(where=['id IN ('+idstring+')']).delete()
        
        return HttpResponse('{"code":0}')
    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
        

def getLog(request):
    try:
        start = int(request.POST['start'],0)
        length = int(request.POST.get('length',10))
        orderNum = request.POST["order[0][column]"]
        orderKey = request.POST["columns["+orderNum+"][data]"]
        orderDir = request.POST["order[0][dir]"]
        orderKey = "-" + orderKey if orderDir == 'asc' else orderKey
        searchKeyword = request.POST['search[value]'] 
        searchColumn = request.POST['searchcolumn']        
        retData= {	
            "draw": request.POST.get("draw",0),
            "recordsTotal":0,
            "recordsFiltered":0,
            "data": []
        }          
        if searchKeyword:
            if searchColumn == "ALL":
                total = userActionLog.objects.filter(Q(username__contains=searchKeyword)|Q(ipaddr__contains=searchKeyword)|Q(action__contains=searchKeyword)).count()
                result = userActionLog.objects.filter(Q(username__contains=searchKeyword)|Q(ipaddr__contains=searchKeyword)|Q(action__contains=searchKeyword)).order_by(orderKey)[start:start+length-1]
            elif searchColumn == "username":
                total = userActionLog.objects.filter(Q(username__contains=searchKeyword)).count()
                result = userActionLog.objects.filter(Q(username__contains=searchKeyword)).order_by(orderKey)[start:start+length-1]
            elif searchColumn == "ipaddr":
                total = userActionLog.objects.filter(Q(ipaddr__contains=searchKeyword)).count()
                result = userActionLog.objects.filter(Q(ipaddr__contains=searchKeyword)).order_by(orderKey)[start:start+length-1]     
            elif searchColumn == "action":
                total = userActionLog.objects.filter(Q(action__contains=searchKeyword)).count()
                result = userActionLog.objects.filter(Q(action__contains=searchKeyword)).order_by(orderKey)[start:start+length-1]   
            #elif searchColumn == "app":
                #total = userActionLog.objects.filter(Q(app__contains=searchKeyword)).count()
                #result = userActionLog.objects.filter(Q(app__contains=searchKeyword)).order_by(orderKey)[start:start+length-1]  
            else:
                total = 0
                result = []
        else:
            total = userActionLog.objects.all().count()
            result = userActionLog.objects.all().order_by(orderKey)[start:start+length-1]
            
        retData["recordsTotal"] = total
        retData["recordsFiltered"] = total
        for item in result:
            dataJson = {}
            dataJson['id'] = item.id
            dataJson['username'] = item.username
            dataJson['ipaddr'] = item.ipaddr
            dataJson['action'] = item.action
            dataJson['action_time'] = datetime.datetime.strftime(item.action_time,"%Y-%m-%d %H:%M:%S") if item.action_time else ""
            #dataJson['app'] = item.app
            retData['data'].append(dataJson)        
        return HttpResponse(json.dumps(retData))
    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())    
        return HttpResponse(json.dumps({"draw": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}))   
    
def has_perm_log(user):
    try:
        if user.is_superuser:
            return True
        actionlogperm = subMenu.objects.filter(url="/actionlog/")[0]
        if user.has_perm("view_submenu",obj=actionlogperm):
            return True
        else:
            return False
    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())  
        return False