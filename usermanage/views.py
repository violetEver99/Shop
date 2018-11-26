# -*- coding: utf-8 -*-
##############################################################################
# FileName: usermanage\views.py
# Description: web用户管理模块
# Version: V1.0
# Author: 
# Function List:
#   1. 用户/用户组的增加、编辑、删除
#   2. 用户/用户组权限管理
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
from django.db.models import Q
import django.contrib.sessions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import auth

import guardian
from guardian.models import UserObjectPermission
from guardian.models import GroupObjectPermission
from guardian.shortcuts import get_perms, assign, remove_perm, get_objects_for_user,get_objects_for_group
from guardian.core import ObjectPermissionChecker
from framework.models import *
from framework.views import *
from .models import UserProfile,GroupProfile,Perms,Group_Perms
import traceback
from logger.views import logger
import json

@login_required
def usermanage(request):
    """
    user management for superuser
    """
    try:
        if not has_perm_usermange(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")        
        a = getMenu(request)      
        return render(request,"usermanage.html",{"contexts":a,"request":request})
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        raise Http404

@csrf_exempt
@login_required
def getmenu(request):
    """
    """    
    try:         
        mainMenuList = mainMenu.objects.all()
        menu = []
        for menu1 in mainMenuList:
            a = {'name':menu1.name, 'url':menu1.url, 'open':True, 'id':'1_'+str(menu1.id), 'children':[]}
            for menu2 in menu1.submenu_set.all():
                b = {'name':menu2.name, 'url':menu2.url, 'id':'2_'+str(menu2.id), 'children':[]}
                #for menu3 in menu2.contenturl_set.all():
                    #c = {'name':menu3.name, 'url':menu3.url, 'id':'3_'+str(menu3.id)}
                    #b['children'].append(c)
                a['children'].append(b)
            menu.append(a)         

        return HttpResponse(json.dumps(menu))
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
    
@csrf_exempt
@login_required
def changepw(request):
    """
    修改密码
    """
    try:
        if request.method == "POST":
            op = request.POST.get("op")
            if op == "self":
                username = request.user.username
                newpasswd = request.POST['data']
                user = authenticate(username=username, password=newpasswd)
                if user is not None:           
                    return HttpResponse('{"code":1,"msg":"与原密码相同"}')
                else:
                    request.user.set_password(newpasswd)
                    request.user.save()
                    action = "修改密码"
                    writeLog(request, action)
                    return HttpResponse('{"code":0}')
            elif op == "reset":
                user = User.objects.get(id=request.POST.get("id"))
                if user:
                    user.set_password("888888")
                    user.save()
                    action = "用户名" + user.username + "修改密码"
                    writeLog(request, action)
                    return HttpResponse('{"code":0}')                    
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


def has_perm_usermange(user):
    try:
        if user.is_superuser:
            return True
        usermanageperm = subMenu.objects.filter(url="/usermanage/")[0]
        if user.has_perm("view_submenu",obj=usermanageperm):
            return True
        else:
            return False
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return False


@csrf_exempt
@login_required
def userManage(request):
    try:
        if not has_perm_usermange(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")               
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op == "add" and addUser(request)) or (op == "get" and getUser(request)) or (op == "edit" and editUser(request)) or (op == "del" and delUser(request))

    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())   


def getUser(request):
    """
    用户列表
    """
    try:

        retData = {
            "draw" : 0, 
            "recordsTotal" :0,
            "recordsFiltered" : 0,
            "data" : []
        }
        selfname = request.user.username
        users = User.objects.exclude(Q(username=selfname) | Q(username="AnonymousUser") | Q(username="admin"))    
        retData["recordsTotal"] = len(users)
        retData["recordsFiltered"] = len(users)
        for user in users:
            usersJson = {}
            usersJson['username'] = user.username
            usersJson['department'] = user.userprofile.department
            usersJson['info'] = user.userprofile.info
            
            group = user.groups.all()[0]
            usersJson['role'] = group.name
            usersJson['roleid'] = group.id
            usersJson['userid'] = user.id
            retData["data"].append(usersJson)     
        return HttpResponse(json.dumps(retData))
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        raise Http404

def addUser(request):
    """
    创建新用户
    """
    try:        
        username = request.POST["username"]
        checkuser = User.objects.filter(username = username)
        if checkuser:
            return HttpResponse('{"code":1,"msg":"用户名已存在"}')
        
        passwd = request.POST["passwd"]
        department = request.POST["department"]
        info = request.POST["info"]
        role = int(request.POST["role"])
        group = Group.objects.get(id=role)
        
        user = User.objects.create_user(username,None,passwd)
        userprofile = user.userprofile
        userprofile.department = department
        userprofile.info = info
        userprofile.save() 
        user.groups.add(group)
        action = "创建新用户：【" + username + "】"
        writeLog(request, action)
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

def editUser(request):
    """
    编辑用户
    """
    try:
        username = request.POST["username"]
        userid = int(request.POST["userid"])
        department = request.POST["department"]
        info = request.POST["info"]
        role = int(request.POST["role"])
        group = Group.objects.get(id=role)
        
        user = User.objects.get(id = userid)
        
        if user.username != username:
            checkuser = User.objects.filter(username = username)
            if checkuser:
                return HttpResponse('{"code":1,"msg":"用户名已存在"}')
            else:
                user.username = username
                user.save()
        
        userprofile = user.userprofile
        userprofile.department = department
        userprofile.info = info
        userprofile.save() 
        user.groups.clear()
        user.groups.add(group)
        return HttpResponse('{"code":0}')          
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

def delUser(request):
    """
    删除用户
    """
    try:            
        ids = json.loads(request.POST["ids"])
        action = "删除用户："
        for item in ids:
            user = User.objects.get(id=item)
            action += "【" + user.username + "】"
            user.delete()            
        writeLog(request, action)
        return HttpResponse('{"code":0}') 
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


@csrf_exempt
@login_required
def groupManage(request):
    try:
        if not has_perm_usermange(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")          
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op == "add" and addGroup(request)) or (op == "get" and getGroup(request)) or (op == "edit" and editGroup(request)) or (op == "del" and delGroup(request))

    except:
        #print traceback.format_exc()
        logger.debug(traceback.format_exc())   


def getGroup(request):
    """
    组列表
    """
    try:          
        retData = {
            "draw" : 0, 
            "recordsTotal" : 0,
            "recordsFiltered" :0,
            "data" : []
        }
        retData_flag = {
            "success": True,
            "results": [
              #{
                #"name"  : "Choice 1",
                #"value" : "value1", 
                #"text"  : "Choice 1", 
                #"disabled"  : False
               #}
            ]
        }
        
        if request.POST.has_key("flag"):
            _key = request.POST.get("key")
            if _key:
                groups = Group.objects.filter(groupprofile__usable = True,name__contains = _key)
            else:
                groups = Group.objects.filter(groupprofile__usable = True)

            retData["recordsTotal"] = len(groups)
            retData["recordsFiltered"] = len(groups)                
            for group in groups:
                groupsJson = {}
                groupsJson['name'] = group.name
                groupsJson['value'] = group.id
                groupsJson['text'] = group.name
                groupsJson['disabled'] = False
                retData_flag["results"].append(groupsJson)                      
            return HttpResponse(json.dumps(retData_flag))   
        
        else:
            groups = Group.objects.all()      
            retData["recordsTotal"] = len(groups)
            retData["recordsFiltered"] = len(groups)                 
            for group in groups:
                groupsJson = {}                
                groupsJson['groupname'] = group.name
                groupsJson['info'] = group.groupprofile.info
                groupsJson['usable'] = "可用" if group.groupprofile.usable else "未分配权限"
                groupsJson['id'] = group.id
                groupsJson['city'] = group.group_perms_set.filter(perms__datatype="city")[0].perms.data
                retData["data"].append(groupsJson)     
            return HttpResponse(json.dumps(retData))
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        raise Http404

def addGroup(request):
    """
    创建新角色
    """
    try:
        groupname = request.POST["groupname"]
        info = request.POST["info"]
        city = request.POST["city"]
        checkgroup = Group.objects.filter(name=groupname)
        if checkgroup:
            return HttpResponse('{"code":1,"msg":"用户组名已存在"}')
        group = Group.objects.create(name=groupname)
        perms = Perms.objects.filter(data=city, datatype="city")
        if not perms:
            perms = Perms.objects.create(data=city, datatype="city")
        else:
            perms = perms[0]
        Group_Perms.objects.create(group=group,perms=perms)
        groupprofile = group.groupprofile
        groupprofile.info = info
        groupprofile.usable = 0
        groupprofile.save()
        action = "创建新角色：【" + groupname + "】"
        writeLog(request, action)    
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
    
    
@csrf_exempt
def editGroup(request):
    """
    编辑角色信息
    """
    try:
        gid = int(request.POST["id"])
        groupname = request.POST["groupname"]
        info = request.POST["info"]
        city = request.POST["city"]
        group = Group.objects.get(id=gid)
        
        if group.name != groupname:
            checkrolegroup = Group.objects.filter(name=groupname)
            if checkrolegroup:
                return HttpResponse('{"code":1,"msg":"用户组名已存在"}')
            else:
                group.name = groupname    
                group.save()
        perms = Perms.objects.filter(data=city, datatype="city")
        if not perms:
            perms = Perms.objects.create(data=city, datatype="city")
        else:
            perms = perms[0]
        Group_Perms.objects.create(group=group,perms=perms)       
        groupprofile = group.groupprofile
        groupprofile.info = info
        groupprofile.save() 
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


def delGroup(request):
    """
    删除角色
    """
    try:           
        ids = json.loads(request.POST["ids"])
        action = "删除角色："
        for item in ids:
            group = Group.objects.get(id=item)
            action += "【" + group.name + "】"
            User.objects.filter(groups__in=[group]).delete()
            group.delete() 
        writeLog(request, action)
        #guardian.utils.clean_orphan_obj_perms()
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')



@csrf_exempt
@login_required
def permsManage(request):
    try:
        if not has_perm_usermange(request.user):
            #auth.logout(request)
            return HttpResponseRedirect("/")          
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op == "get" and getPerms(request)) or (op == "set" and setPerms(request))

    except:
        logger.debug(traceback.format_exc())  
        #print traceback.format_exc()


def getPerms(request):
    """
    获取用户权限
    """
    try:

        gid = int(request.POST["id"])
        
        group = Group.objects.get(id=gid)

        permsDir = {}
        checker = ObjectPermissionChecker(group)
        mainMenuList = mainMenu.objects.all()
        
        for menu1 in mainMenuList:
            if checker.has_perm('view_mainmenu',menu1):
                permsDir['1_'+str(menu1.id)] = 1
                for menu2 in menu1.submenu_set.all():
                    if checker.has_perm('view_submenu',menu2):
                        permsDir['2_'+str(menu2.id)] = 1
                        for menu3 in menu2.contenturl_set.all():
                            if checker.has_perm('view_contenturl',menu3):
                                permsDir['3_'+str(menu3.id)] = 1           
        return HttpResponse(json.dumps(permsDir))

        
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

@csrf_exempt
def setPerms(request):
    """
    设置用户权限
    """
    try:
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/")  
        if request.method == "POST":
            gid = request.POST["id"]
            group = Group.objects.get(id=gid)

            permsList = json.loads(request.POST["perms"])
            checker = ObjectPermissionChecker(request.user)            
            
            for obj in get_objects_for_group(group, 'framework.view_mainmenu'):
                remove_perm('framework.view_mainmenu', group, obj)
            for obj in get_objects_for_group(group, 'framework.view_submenu'):
                remove_perm('framework.view_submenu', group, obj)
            for obj in get_objects_for_group(group, 'framework.view_contenturl'):
                remove_perm('framework.view_contenturl', group, obj)
            
            for perm in permsList:
                db,objID = perm.split("_")
                if db == "1":
                    obj = mainMenu.objects.get(id=int(objID))
                    if checker.has_perm('view_mainmenu', obj):
                        assign('view_mainmenu', group, obj)
                elif db == "2":
                    obj = subMenu.objects.get(id=int(objID))
                    if checker.has_perm('view_submenu', obj):
                        assign('view_submenu', group, obj)
                elif db == "3":
                    obj = contentUrl.objects.get(id=int(objID))
                    if checker.has_perm('view_contenturl', obj):
                        assign('view_contenturl', group, obj)
            groupprofile = group.groupprofile
            groupprofile.usable = 1
            groupprofile.save()
            action = "配置角色【" + group.name + "】的菜单权限"

            writeLog(request, action)
            return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
    


    
    
    

    