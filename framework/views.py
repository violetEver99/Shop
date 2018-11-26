# -*- coding: utf-8 -*-
##############################################################################
# FileName: logger\views.py
# Description: web框架
# Version: V1.0
# Author: Qiurong
# Function List:
#   1. 组建页面菜单
#   2. 记录用户操作日志
# History:
#	<author>		<time>		<version>		<desc>
#	Qiurong		    2016/8/10	V1.0			创建文件
###############################################################################
from django.conf import settings
from django.contrib.auth.models import User,Permission,Group
from guardian.core import ObjectPermissionChecker
#from guardian.models import UserObjectPermission
#from guardian.models import GroupObjectPermission
#from guardian.shortcuts import get_perms,assign
from framework.models import *
import traceback
from logger.views import logger
from actionlog.models import userActionLog
import json
import datetime

def getmenuFromContentUrl(ukey,cotenturldict,preurl,checker):
    menulist = []
    if cotenturldict.has_key(ukey):
        for uitem in cotenturldict[ukey]:
            if uitem.url.startswith(preurl):
                if not checker:
                    c = {'name':uitem.name, 'id':'3_'+str(uitem.id), 'allowpermission':getPermCodes("contenturl"), 'children':[]}
                else:
                    c = {'name':uitem.name, 'id':'3_'+str(uitem.id), 'allowpermission':filter(lambda item:checker.has_perm(item,uitem),getPermCodes("contenturl")), 'children':[]}
                #c['children'].append({'name':uitem.name+"_添加", 'url':uitem.url, 'id':'3_'+str(uitem.id)+'_add','children':[]})
                #c['children'].append({'name':uitem.name+"_修改", 'url':uitem.url, 'id':'3_'+str(uitem.id)+'_edit','children':[]})
                #c['children'].append({'name':uitem.name+"_删除", 'url':uitem.url, 'id':'3_'+str(uitem.id)+'_delete','children':[]})
                c['children'].extend(getmenuFromContentUrl(ukey+1, cotenturldict,uitem.url,checker))
                menulist.append(c)
        #logger.debug(menulist)
        return menulist
    else:
        return []
    
def getMenu(request):
    try:   
        user = request.user
        appMenu = []
        mainMenuList = mainMenu.objects.all()

        for menu1 in mainMenuList:
            if user.has_perm('view_mainmenu',obj=menu1):
                a = {'name':menu1.name, 'url':menu1.url, 'open':True,'id':'1_'+str(menu1.id), 'children':[]}
                for menu2 in menu1.submenu_set.all():
                    if user.has_perm('view_submenu',obj=menu2):
                        b = {'name':menu2.name, 'url':menu2.url, 'id':'2_'+str(menu2.id), 'children':[]}
                        cotenturldict = {}
                        for menu3 in menu2.contenturl_set.all():
                            if user.has_perm('view_contenturl',obj=menu3):
                                len_key = len(menu3.url.split("/"))
                                if cotenturldict.has_key(len_key):
                                    cotenturldict[len_key].append(menu3)
                                else:
                                    cotenturldict[len_key] = [menu3]
                        b['children'].extend(getmenuFromContentUrl(3, cotenturldict, menu2.url,user))
                        a['children'].append(b)
                appMenu.append(a)                

            #for mainmenu in mainMenuList:
                #if user.has_perm('view_mainmenu',obj=mainmenu):
                    #b = []
                    #for submenu in mainmenu.submenu_set.all():
                        #if user.has_perm('view_submenu',obj=submenu):
                            #b.append({"name":submenu.name,"url":submenu.url})
                    #appMenu.append({"mainmenu":{"name":mainmenu.name,"url":mainmenu.url},"submenus":b})
                    
        url = request.path
        _submenu = subMenu.objects.filter(url = url)
        if _submenu:
            try:
                _submenu = _submenu[0]
                breadMenu = [{"name":_submenu.parentMenu.name,"url":_submenu.parentMenu.url},{"name":_submenu.name,"url":_submenu.url}]    
            except:
                breadMenu = []
        else:
            _contenturl = contentUrl.objects.filter(url = url)
            if _contenturl:
                try:
                    _contenturl = _contenturl[0]
                    breadMenu = [{"name":_contenturl.parentMenu.parentMenu.name,"url":_contenturl.parentMenu.parentMenu.url},{"name":_contenturl.parentMenu.name,"url":_contenturl.parentMenu.url}]
                    additionMenu = [{"name":_contenturl.name,"url":_contenturl.url}]
                    while True:
                        url = url.rsplit("/",1)[0]
                        _contenturl = contentUrl.objects.filter(url = url)
                        if _contenturl:
                            additionMenu.append({"name":_contenturl[0].name,"url":_contenturl[0].url})
                        else:
                            break
                    breadMenu.extend(additionMenu[::-1])
                except:
                    breadMenu = []            
        
        #burllist = filter(lambda item:item, url.split("/"))
        #print burllist
        
        #urllen = len(burllist)
        #if urllen == 0 :
            #breadMenu = [] 
        #elif urllen == 1:
            #try:
                #breadCrumb = subMenu.objects.get(url="/"+"/".join(burllist))
                #breadMenu = [{"name":breadCrumb.parentMenu.name,"url":breadCrumb.parentMenu.url},{"name":breadCrumb.name,"url":breadCrumb.url}]    
            #except:
                #breadMenu = []
        #elif urllen == 2:
            #try:
                #breadCrumb = contentUrl.objects.get(url="/"+"/".join(burllist))
                #breadMenu = [{"name":breadCrumb.parentMenu.parentMenu.name,"url":breadCrumb.parentMenu.parentMenu.url},{"name":breadCrumb.parentMenu.name,"url":breadCrumb.parentMenu.url},{"name":breadCrumb.name,"url":breadCrumb.url}]    
            #except:
                #breadMenu = []
        #elif urllen >= 3:
            #try:
                #breadCrumb = contentUrl.objects.get(url="/"+"/".join(burllist[0:2]))
                #breadMenu = [{"name":breadCrumb.parentMenu.parentMenu.name,"url":breadCrumb.parentMenu.parentMenu.url},{"name":breadCrumb.parentMenu.name,"url":breadCrumb.parentMenu.url},{"name":breadCrumb.name,"url":breadCrumb.url}] 
            #except:
                ##print traceback.format_exc()
                #breadMenu = []
            #for i in range(3,urllen+1):
                #try:
                    #breadCrumb = contentUrl.objects.get(url="/"+"/".join(burllist[0:i]))
                    #breadMenu.append({"name":breadCrumb.name,"url":breadCrumb.url})
                #except:
                    #pass
        #else:                
            #breadMenu = [] 
        
        retData = {"menu": appMenu, "bread":breadMenu}
        return retData
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return {}


def getMenuFromGroup(groupid):
    try:
        groupMenu = []
        mainMenuList = mainMenu.objects.all()
        if groupid == -1:
            for menu1 in mainMenuList:
                a = {'name':menu1.name, 'url':menu1.url, 'open':True, 'id':'1_'+str(menu1.id), 'children':[]}
                for menu2 in menu1.submenu_set.all():
                    b = {'name':menu2.name, 'url':menu2.url, 'id':'2_'+str(menu2.id), 'children':[]}
                    for menu3 in menu2.contenturl_set.all():
                        c = {'name':menu3.name, 'url':menu3.url, 'id':'3_'+str(menu3.id)}
                        b['children'].append(c)
                    a['children'].append(b)
                groupMenu.append(a) 
        else: 
            group = Group.objects.get(id=groupid)
            checker = ObjectPermissionChecker(group)
            for menu1 in mainMenuList:
                if checker.has_perm('view_mainmenu',obj=menu1):
                    a = {'name':menu1.name, 'url':menu1.url, 'open':True,'id':'1_'+str(menu1.id), 'children':[]}
                    for menu2 in menu1.submenu_set.all():
                        if checker.has_perm('view_submenu',obj=menu2):
                            b = {'name':menu2.name, 'url':menu2.url, 'id':'2_'+str(menu2.id), 'children':[]}
                            for menu3 in menu2.contenturl_set.all():
                                if checker.has_perm('view_contenturl',obj=menu3):
                                    c = {'name':menu3.name, 'url':menu3.url, 'id':'3_'+str(menu3.id)}
                                    b['children'].append(c)
                            a['children'].append(b)
                    groupMenu.append(a)
        return groupMenu
    except:
        logger.debug(traceback.format_exc())
        #print traceback.format_exc()
        return []
    

def writeLog(request, action):
    username = request.user.username
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
        ipaddr =  request.META['HTTP_X_FORWARDED_FOR']  
    else:  
        ipaddr = request.META['REMOTE_ADDR']  
    now = datetime.datetime.now()
    userActionLog.objects.create(username=username, ipaddr=ipaddr, action=action,action_time=now)