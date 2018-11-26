# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.template import RequestContext, Context, Template
from django.http import Http404
from django.contrib import auth
import django.contrib.sessions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core import serializers
import datetime
import traceback
import json
import os
import chardet
from django.db.models import Q, F
#加载框架模块
from framework.views import *
from datamanage.models import *
from usermanage.models import *

from logger.views import logger


import sys
reload(sys)
sys.setdefaultencoding("utf-8")


@login_required
def dataView1(request,datatype):
    """
    """
    try:

        menucontexts = getMenu(request)
        print (menucontexts)
        return render(request, datatype + ".html",{"contexts":menucontexts,"request":request})        

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404

    
@login_required    
def dataView(request, datatype):
    try:
        menucontexts = getMenu(request)
        #print (menucontexts)
        return render(request, datatype + ".html",{"contexts":menucontexts,"request":request})
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404





@login_required
def opDataView1(request,datatype,op):
    """
    """
    try:
        menucontexts = getMenu(request)
        if datatype == "mission":
            data = {}
            _id = ""
            canEdit = 0
            if op != "add":
                user = request.user
                _id = request.GET["id"]
                city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))
                _mission = Missions.objects.filter(id = _id)
                if op == "submit":
                    _mission = _mission.filter(Q(receiptor = user.username) & (Q(status = 1) | Q(status = 4)))
                elif op == "examine":
                    _mission = _mission.filter(sender = user.username, status = 2)
                elif op == "check":
                    _mission = _mission.filter((Q(sender = user) | Q(majorcity__in = city) | Q(assistcity__in = city) | Q(receiptor = user)))
                
                if not _mission:
                    raise Http404
                else:
                    dataJson = json.loads(serializers.serialize("json", _mission))[0]
        
                    data = dataJson["fields"]
                    data["id"] = dataJson["pk"]
                    data["date"] = data["date"].replace("T", " ")
                    if data["sender"] == user.username and int(data["status"]) < 3:
                        canEdit = 1
                    try:
                        esData = es.get(index="clue", id=data["dataid"])["_source"]
                        data.update(esData)
                    except:
                        esData = {}
                htmlname = "missiondetail.html"
            else:
                htmlname = "missionadd.html"
            return render(request, htmlname, {"contexts":menucontexts,"request":request, "op":op, "id": _id, "data":json.dumps(data), "canEdit": canEdit})

        else:
            if op == "add":
                return render(request, datatype + "edit.html",{"contexts":menucontexts,"request":request, "op":op})  
            else:
            #elif op == "edit":
                theid = request.GET["id"]
                try:
                    data = es.get(index=datatype, id=theid)["_source"]
                except Exception,e:
                    logger.error(e)
                    if str(e).find("TransportError") != -1:
                        data = {"code":404,"msg": "数据不存在"}
                    else:
                        data = {"code":1,"msg": "服务器异常"}
                return render(request, datatype + op + ".html",{"contexts":menucontexts,"request":request, "op":op, "id": theid, "data":json.dumps(data)})
          

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404



def opDataView(request, datatype, op ):
    try:
        menucontexts = getMenu(request)
        if datatype == "auction":
            data = {}
            _id = ""
            if op == "add":
                return render(request, datatype + "edit.html", {"contexts": menucontexts, "request": request, "op": op})
            else:
                _id = request.GET["id"]
              
                _auction = Auctions.objects.filter(id =_id)
                print _auction
                if _auction:
                    dataJson = json.loads(serializers.serialize("json", _auction))[0]
                    data = dataJson["fields"]
                    data["id"] = dataJson["pk"]                    
                #else:
                    #data = {"code": 404, "msg": "数据不存在"}
               
                      
                
                return render(request, datatype + op + ".html", {"contexts": menucontexts, "requset": request, "data": json.dumps(data),"op": op, "id": _id,})
                    
                             
                    
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404
            





@csrf_exempt
@login_required
def upFile(request):
    try:
        if request.method == "POST":
            username = request.user.username
            tmpPath = os.path.join(settings.BASE_DIR,"static","files")
            #outPath = os.path.join("static","files",username)
            if not os.path.exists(tmpPath):
                os.makedirs(tmpPath)          
            fileList = request.FILES.getlist('file', None)
            retData = []
            action = "上传文件："
            if fileList:
                for _file in fileList:
                    fileName = _file.name
                    action += "【" + fileName + "】"
                    fileContent = _file.read()
                    fileReName = getStrMd5(fileContent) + "_" + fileName
                    filePath = os.path.join(tmpPath,fileReName)
                    retData.append(fileReName)
                    if os.path.isfile(filePath):
                        Files.objects.filter(name=fileReName).update(delete= 0)
                        continue
                    with open(filePath,"wb") as f:
                        f.write(fileContent)
                    Files.objects.create(name=fileReName,path=filePath)
            writeLog(request, action)
            return HttpResponse(json.dumps(retData))
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常，上传失败"}')

@login_required  
def getFile(request):
    try:
        fileName = request.GET["n"]
        username = request.user.username
        filePath = Files.objects.get(name=fileName).path
        with open(filePath,"rb") as fmail:
            fmessage = fmail.read()
        fname = fileName.split("_",1)[-1].encode("utf-8")
        response = HttpResponse(fmessage,content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % fname   
        return response           
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404

@csrf_exempt
@login_required
def unitManage(request):
    try:
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op in ["add", "edit"] and addUnit(request)) or (op in ["get", "export"] and getUnit(request)) or (op == "delete" and delUnit(request))

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()

def delUnit(request):
    try:
        ids = request.POST["ids"].split(",")       
        for _id in ids:
            es.delete(index = "unit", doc_type = "unit", id = _id, refresh=True)   
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


def addUnit(request):
    try:
        op = request.POST["op"]
        row = {"city": request.user.groups.get().group_perms_set.filter(perms__datatype="city")[0].perms.data}
        fileToKeep = []  
        for key in request.POST.keys():
            if key in ["op","_id"]:
                continue
            else:
                data = json.loads(request.POST.get(key, None))
                if key.find("new") != -1:
                    row["custom"].append(data)
                else:
                    try:
                        row[key] = json.loads(data["value"])
                    except ValueError:
                        row[key] = data["value"]
                if data["type"] == "file":
                    fileList = map(lambda x : os.path.basename(x), data["value"].split(","))
                    #print fileList
                    fileToKeep.extend(filter(lambda x : x and x not in fileToKeep,fileList))
        for item in fileToKeep:
            Files.objects.filter(name=item).update(stay = F("stay") + 1)
        Files.objects.filter(stay = 0).update(delete = F('delete') + 1)
        for item in Files.objects.filter(delete__gt = 50):
            os.remove(item.path)
            item.delete()        
        if op == "add":
            es.index(index = "unit", doc_type = "unit", body = row, refresh=True)
            action = "新建单位数据：【" + json.loads(request.POST["name"])["value"] + "】"
        else:
            _id = request.POST["_id"]
            es.update(index = "unit", doc_type = "unit", body = {"doc":row}, id=_id, refresh=True)
            action = "编辑单位数据：【" + json.loads(request.POST["name"])["value"] + "】"


        writeLog(request, action)        
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

def getUnit(request):
    try:
        op = request.POST.get("op")
        mustList = []
        exportAll = False
        city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))

        if op == "get":
            start = int(request.POST['start'])
            length = int(request.POST.get('length',10))
    
            orderNum = request.POST["order[0][column]"]
            orderKey = request.POST["columns["+orderNum+"][data]"]
            orderDir = request.POST["order[0][dir]"]
            keyword = request.POST["search[value]"]
            draw = request.POST.get("draw",0)
        elif op == "export":
            params = json.loads(request.POST["params"])
            start = params["start"]
            length = params["length"]
            orderNum = params["order"][0]["column"]
            orderKey = params["columns"][orderNum]["data"]
            orderDir = params["order"][0]["dir"]
            #query = json.loads(params["query"])
            keyword = params.get("keyword")
            if request.POST.get("all"):
                exportAll = True            
            
        if keyword:
            mustList.append({"wildcard":{"_all":"*" + keyword + "*"}})
        citymustList = {"bool": {"should": []}}
        for item in city:
            if item == "省厅":
                citymustList = False
                break
            else:
                citymustList["bool"]["should"].append({"term": {"city": item}})
        if citymustList:
            mustList.append(citymustList)

        #query = json.loads(request.POST.get("query"))
        #mustList.extend(query)
        #if query["term"]:
            #mustList.append({"term":query["term"]})
        #if query["match"]:
            #mustList.append({"match":query["match"]})
        #if query["match_phrase"]:
            #mustList.append({"match_phrase":query["match_phrase"]})
        body = {
            "query": {
                "bool": {
                    "must" : mustList,
                }
                },
            "size": int(length),
            "from": int(start)
        }
        if orderKey and not exportAll:
            body["sort"] = { orderKey: { "order": orderDir }}        
        #print body
        if op == "get":
            result = es.search(index="unit", doc_type="unit", body=body)
    
            retData = {"recordsTotal": result["hits"]["total"], "recordsFiltered": result["hits"]["total"], "data": [], "draw": draw} 
            for item in result["hits"]["hits"]:
                item["_source"]["_id"] = item["_id"]
                retData["data"].append(item["_source"])
            return HttpResponse(json.dumps(retData))
        elif op == "export":
            result = es.search(index="unit", body=body, scroll="1m")
            head = ("编号", "属地", "单位名字", "地址", "联系人及职务", "公网IP地址", "单机数量",  "单机杀毒软件", "软件系统及开发商", "服务器及供应商", "服务器品牌及型号", "路由器品牌及型号", "交换机品牌及型号", "防火墙品牌及型号", "入侵检测设备", "安全审计设备")
            fileObj = xlwt.Workbook(encoding = 'utf-8')
            headStyle = xlwt.Style.easyxf("font: bold on; align: wrap on, vert centre, horiz center")
            textStyle = xlwt.Style.easyxf("align: wrap on, vert centre, horiz center")
    
            table = fileObj.add_sheet('Sheet1',cell_overwrite_ok=True)
            for i in range(len(head)):
                table.write(0, i, head[i], headStyle)
                if i:
                    table.col(i).width = 256*20
                else:
                    table.col(0).width = 256*10
    
            i = 1
            while result:
                if not len(result["hits"]["hits"]):
                    break
                for item in result["hits"]["hits"]:
                    data = item["_source"]
                    line = [
                        str(i),
                        data.get("location", ""),
                        data.get("name", ""),
                        data.get("address", ""),
                        data.get("contact", ""),
                        ", ".join(data.get("ip", [])),
                        data.get("machinecount", ""),
                        ",".join(data.get("antivirus", [])),
                        "\r\n".join(map(lambda x: ", ".join(map(lambda y: y["value"], x)), data.get("serverer", []))),
                        "\r\n".join(map(lambda x: ", ".join(map(lambda y: y["value"], x)), data.get("servers", []))),
                        "\r\n".join(map(lambda x: ", ".join(map(lambda y: y["value"], x)), data.get("routers", []))),
                        "\r\n".join(map(lambda x: ", ".join(map(lambda y: y["value"], x)), data.get("switches", []))),
                        "\r\n".join(map(lambda x: ", ".join(map(lambda y: y["value"], x)), data.get("firewall", []))),
                        ", ".join(data.get("detecter", [])),
                        ", ".join(data.get("auditor", [])),
                    ]
                    #print line
                    for j in range(len(line)):
                        table.write(i, j, line[j], textStyle)
                    i+=1
                if exportAll:
                    result = es.scroll(scroll_id=result["_scroll_id"], scroll="1m")
                else:
                    break
    
            name = "受检单位_" + datetime.datetime.strftime(datetime.datetime.now(),"%Y_%m_%d_%H_%M_%S") + ".xls"
    
            response = HttpResponse(content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=%s' % name   
            fileObj.save(response)
            return response                 
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse(json.dumps({"draw": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}))    

def parseStructData(_list):
    _str = ""
    if len(_list):
        for item in _list:
            _dict = {}
            if len(item):
                for item2 in item:
                    _dict[item2["key"]] = item2["value"]
                _str += _dict["left"] + ", " + _dict["right"] + "\r\n"
    return _str
        
@csrf_exempt
@login_required
def clueManage(request):
    try:
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op in ["add", "edit"] and addClue(request)) or (op in ["get", "export"] and getClue(request)) or (op == "delete" and delClue(request)) or (op == "getattr" and getClueAttr(request)) or (op == "addattr" and addClueAttr(request)) or (op == "import" and importClue(request))

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()

def isBlank(data):
    return not bool(filter(lambda x : x, data))

def buildData(string):
    data = []
    for item in string.split(","):
        item2 = item.split(":")
        if len(item2) > 1:
            data.append([{"key": "left", "value": item2[0]},{"key": "right", "value": item2[1]}])
        else:
            data.append([{"key": "left", "value": item2[0]}])
    return data

def importClue(request):
    try:
        fileObj = request.FILES.get('file', None)
        row = {"city": request.user.groups.get().group_perms_set.filter(perms__datatype="city")[0].perms.data, "mission":-1, "hostfeature": "", "report": ""}
        fileData = fileObj.read()
        try:
            excelObj = xlrd.open_workbook(file_contents= fileData)
        except:
            return HttpResponse('{"code":1,"msg":"文件错误，请检查是否为excel文件，并确认是否有使用模版！"}')    
        encoding = chardet.detect(fileData)["encoding"] or "utf-8"
        print encoding
        sheel = excelObj.sheets()[0]
        rowLength = sheel.nrows - 2
        print rowLength
        noData = True
        if rowLength:
            for i in range(rowLength):
                line = sheel.row_values(i + 2)
                print line
                if not isBlank(line):
                    noData = False
                    _row = row.copy()
                    _row["direction"] = line[0]
                    _row["location"] = line[1]
                    _row["time"] = line[2]
                    _row["unit"] = line[4]
                    _row["remark"] = line[9]
                    _row["ip"] = line[3].split(",")
                    _row["email"] = line[7].split(",")
                    _row["email2"] = line[8].split(",")
                    _row["controlip"] = buildData(line[5])
                    _row["url"] = buildData(line[6])
                    es.index(index = "clue", doc_type = "clue", body = _row, refresh=True)
                    
                    if line[0]:
                        if not DataAttr.objects.filter(name = line[0], type = "direction"):
                            DataAttr.objects.create(name=line[0], type= "direction")
        if noData:
            return HttpResponse('{"code":1,"msg":"导入结束，未导入任何数据"}')
        else:
            return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')            

def addClueAttr(request):
    try:
        attrType = request.POST.get("type")
        attrName = request.POST.get("name")
        if DataAttr.objects.filter(name = attrName, type = attrType):
            return HttpResponse('{"code":0}')
        if attrType == "unit":
            attrName = attrName.split(",")
            DataAttr.objects.create(name=attrName[0], charge=attrName[1], location=attrName[2], contact=attrName[3], type=attrType)
        else:
            DataAttr.objects.create(name=attrName, type=attrType)

        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')    

def getClueAttr(request):
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
        attrType = request.POST.get("type")
        key = request.POST.get("key")
        if request.POST.has_key("flag"):       
            if attrType == "unit":
                mustList = []
                city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))        
                citymustList = {"bool": {"shoula": []}}
                for item in city:
                    if item == "省厅":
                        citymustList = False
                        break
                    else:
                        citymustList["bool"]["should"].append({"term": {"city": item}})
                if citymustList:
                    mustList.append(citymustList)
                if key:
                    mustList.append({"wildcard":{"_all":"*"+key+"*"}})
                body = {
                    "query": {
                        "bool": {
                            "must" : mustList,
                        }
                    }
                }
                result = es.search(index="unit", doc_type="unit", body=body)
                for unit in result["hits"]["hits"]:
                    data = unit["_source"]["name"] + ", " + unit["_source"]["address"]
                    retData_flag["results"].append({"name":data, "value":data, "text":data, "disabled":False})                    
            else:
                if key:
                    attrs = DataAttr.objects.filter(type = attrType, name__contains = key)
                else:
                    attrs = DataAttr.objects.filter(type = attrType)
                for attr in attrs:
                    data = attr.name
                    retData_flag["results"].append({"name":data, "value":data, "text":data, "disabled":False})
            retData_flag["results"].append({"name":"新增", "value":"new", "text":"新增", "disabled":False})
            return HttpResponse(json.dumps(retData_flag))           
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        raise Http404    

def delClue(request):
    try:
        ids = request.POST["ids"].split(",")         
        for _id in ids:
            es.delete(index = "clue", doc_type = "clue", id = _id, refresh=True)   
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


def addClue(request):
    try:
        op = request.POST["op"]
        row = {"city": request.user.groups.get().group_perms_set.filter(perms__datatype="city")[0].perms.data, "mission":-1}
        fileToKeep = []    
        for key in request.POST.keys():
            if key in ["op", "_id"]:
                continue
            else:
                data = json.loads(request.POST.get(key, None))
                if key.find("new") != -1:
                    row["custom"].append(data)
                else:
                    try:
                        row[key] = json.loads(data["value"])
                    except ValueError:
                        row[key] = data["value"]
                if data["type"] == "file":
                    fileList = map(lambda x : os.path.basename(x), data["value"].split(","))
                    #print fileList
                    fileToKeep.extend(filter(lambda x : x and x not in fileToKeep,fileList))
        for item in fileToKeep:
            Files.objects.filter(name=item).update(stay = F("stay") + 1)
        Files.objects.filter(stay = 0).update(delete = F('delete') + 1)
        for item in Files.objects.filter(delete__gt = 50):
            os.remove(item.path)
            item.delete()

        if op == "add":
            es.index(index = "clue", doc_type = "clue", body = row, refresh=True)
            action = "新建线索数据"
        else:
            _id = request.POST["_id"]
            es.update(index = "clue", doc_type = "clue", body = {"doc":row}, id=_id, refresh=True)
            action = "编辑线索数据"


        writeLog(request, action)        
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

def getClue(request):
    try:
        op = request.POST.get("op")
        mustList = []
        exportAll = False
        if op == "get":
            start = int(request.POST['start'])
            length = int(request.POST.get('length',10))

            orderNum = request.POST["order[0][column]"]
            orderKey = request.POST["columns["+orderNum+"][data]"]
            orderDir = request.POST["order[0][dir]"]
            #query = json.loads(request.POST.get("query"))
            keyword = request.POST.get("keyword")
            field = request.POST.get("field")
            time = request.POST.get("time")
            draw = request.POST.get("draw",0)
        elif op == "export":
            params = json.loads(request.POST["params"])
            start = params["start"]
            length = params["length"]
            orderNum = params["order"][0]["column"]
            orderKey = params["columns"][orderNum]["data"]
            orderDir = params["order"][0]["dir"]
            #query = json.loads(params["query"])
            keyword = params.get("keyword")
            field = params.get("field")
            time = params.get("time")
            if request.POST.get("all"):
                exportAll = True
        #if request.POST.has_key("mission"):
            #mustList.append({"term": {"mission": int(request.POST["mission"])}})
        #else:
        permsMustList = {"bool": {"should": []}}
        city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))
        direction = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="direction"))
        for item in city:
            if item == "省厅":
                permsMustList = False
                break
            else:
                permsMustList["bool"]["should"].append({"term": {"city": item}})
        if permsMustList:
            for item in direction:
                permsMustList["bool"]["should"].append({"term": {"direction": item}})
            mustList.append(permsMustList)

        if time:
            mustList.append({"range":{"time":json.loads(time)}})
        #mustList.extend(query)
        if keyword and field:
            _field = field
            if field in ["controlip", "url"]:
                _field = field + ".value"
            searchMustList = {
                "bool": {
                    "should": [{
                        "wildcard": {
                            _field: "*" + keyword + "*"
                        }
                      },
                      {
                        "match": {
                            _field: keyword
                        }
                      }
                ]}}
            if _field == "email":
                _field = _field + "2"
                searchMustList["bool"]["should"].extend([{
                        "wildcard": {
                            _field: "*" + keyword + "*"
                        }
                      },
                      {
                        "match": {
                            _field: keyword
                        }
                      }
                ])
            mustList.append(searchMustList)
        body = {
            "query": {
                "bool": {
                    "must" : mustList,
                }
            },
            "size":int(length),
            "from":int(start)       
        }
        if field in ["controlip", "url"]:
            body["query"] = {
                "nested":{
                    "path": field,
                    "query": {
                        "bool": {
                            "must" : mustList,
                        }
                    }                    
                }
            }
        if orderKey and not exportAll:
            body["sort"] = { orderKey: { "order": orderDir }}
        print body
        if op == "get":
            result = es.search(index="clue", body=body)
            retData = {"recordsTotal": result["hits"]["total"], "recordsFiltered": result["hits"]["total"], "data": [], "draw": draw} 
            for item in result["hits"]["hits"]:
                item["_source"]["_id"] = item["_id"]
                retData["data"].append(item["_source"])
            #if keyword:
                #return HttpResponse(json.dumps(retData).replace(keyword,"<em>" + keyword + "</em>"))
            #else:
            return HttpResponse(json.dumps(retData))
        elif op == "export":
            result = es.search(index="clue", body=body, scroll="1m")
            head = ("编号", "方向", "属地", "发现时间", "受控IP","所属单位","主控IP及端口号","主控域名及端口号", "攻击邮箱","被攻击邮箱","备注")
            fileObj = xlwt.Workbook(encoding = 'utf-8')
            headStyle = xlwt.Style.easyxf("font: bold on; align: wrap on, vert centre, horiz center")
            textStyle = xlwt.Style.easyxf("align: wrap on, vert centre, horiz center")
            
            table = fileObj.add_sheet('Sheet1',cell_overwrite_ok=True)
            for i in range(len(head)):
                table.write(0, i, head[i], headStyle)
                if i:
                    table.col(i).width = 256*20
                else:
                    table.col(0).width = 256*10
            
            i = 1
            while result:
                if not len(result["hits"]["hits"]):
                    break
                for item in result["hits"]["hits"]:
                    data = item["_source"]
                    line = [
                        str(i),
                        data.get("direction", ""),
                        data.get("location", ""),
                        data.get("time", ""),
                        "\r\n".join(data.get("ip", [])),
                        data.get("unit", ""),
                        "\r\n".join(map(lambda x: ":".join(map(lambda y: y["value"], x)), data.get("controlip", []))),
                        "\r\n".join(map(lambda x: ":".join(map(lambda y: y["value"], x)), data.get("url", []))),
                        "\r\n".join(data.get("email", [])),
                        "\r\n".join(data.get("email2", [])),
                        data.get("remark", ""),
                    ]
                    #print line
                    for j in range(len(line)):
                        table.write(i, j, line[j], textStyle)
                    i+=1
                if exportAll:
                    result = es.scroll(scroll_id=result["_scroll_id"], scroll="1m")
                else:
                    break

            name = "窃密线索_" + datetime.datetime.strftime(datetime.datetime.now(),"%Y_%m_%d_%H_%M_%S") + ".xls"

            response = HttpResponse(content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=%s' % name   
            fileObj.save(response)
            return response     
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse(json.dumps({"draw": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}))    
        
@csrf_exempt
@login_required
def missionManage(request):
    try:
        if request.method == "POST":
            op = request.POST.get("op")
            #request.POST.pop("op")
            return (op == "add" and addMission(request)) or (op == "get" and getMission(request)) or (op == "status" and changeMStatus(request)) or (op == "getdata" and getMissionData(request)) or (op == "submitdata" and submitMissionData(request)) or (op == "editclue" and editMissionClue(request))

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()

def editMissionClue(request):
    try:
        row = {"ip": request.POST.get("ip"),
               "controlip": request.POST.get("controlip"),
               "url": request.POST.get("url"),
               "email": request.POST.get("email"),
               "email2": request.POST.get("email2"),
               "hostfeature": request.POST.get("hostfeature"),
               "location":request.POST.get("location"),
               "time": request.POST.get("time")
               }       
        for key in row:
            try:
                row[key] = json.loads(row[key])
            except:
                pass
        fileList = map(lambda x : os.path.basename(x), request.POST.get("hostfeature").split(","))
        if fileList:
            for item in fileList:
                Files.objects.filter(name=item).update(stay = F("stay") + 1)
            Files.objects.filter(stay = 0).update(delete = F('delete') + 1)
            for item in Files.objects.filter(delete__gt = 50):
                os.remove(item.path)
                item.delete()
    
        _mission = Missions.objects.get(id=request.POST.get("id"))
        _id = _mission.dataid
        es.update(index = "clue", doc_type = "clue", body = {"doc":row}, id=_id, refresh=True)
       
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
    

def submitMissionData(request):
    try:
        _mission = Missions.objects.get(id=request.POST.get("id"))
        status = int(request.POST.get("status"))
        
        _mission.ischecked = int(request.POST.get("ischecked"))
        _mission.result = request.POST.get("result")
        _mission.codes = request.POST.get("codes")
        _mission.project = request.POST.get("project")
        _mission.count = request.POST.get("count")
        _mission.status = status
        _mission.save()

        if status == 2:
            message = "<a href='/data/missionview?id="+str(_mission.id)+"' target='_blank'>" + u"编号：" + str(_mission.id) + u"任务用户已提交数据，请及时处理！" + "</a>"
            wrappedMessage = json.dumps({"message":message,"sender":u"任务提醒","broadcast":2,"missioncounts":1,"type":"handlemission","date":datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")})
            redisMessage = RedisMessage(wrappedMessage)
            redis_publisher = RedisPublisher(facility='foobar', users = [ _mission.sender])         
            redis_publisher.publish_message(redisMessage)                     
    
            action = "提交任务数据"
            writeLog(request, action)

        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

def getMissionData(request):
    try:
        _mission = Missions.objects.get(id=request.POST.get("id"))
        cluetype = _mission.cluetype
        if cluetype in ["ip", "url", "email"]:
            index = "ips"
        else:
            index = cluetype        

        result = es.get_source(index=index, doc_type=index, id=_mission.dataid)
        return HttpResponse(json.dumps(result))
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"获取任务信息失败"}')

def getMission(request):

    try:
        user = request.user.username
        city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))
        if request.POST.has_key("flag"):
            retData = {
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
            data = Missions.objects.filter((Q(sender = user) | Q(receiver__in = city) | Q(receiptor = user)) & Q(status = 3))
            for item in data:
                groupsJson = {}
                groupsJson['name'] = item.id
                groupsJson['value'] = item.id
                groupsJson['text'] = item.id
                groupsJson['disabled'] = False     
                retData["results"].append(groupsJson)
        else:
            retData = {
                "draw" : 0, 
                "recordsTotal" :0,
                "recordsFiltered" : 0,
                "data" : []
            }

            if request.POST.get("id"):
                data = Missions.objects.filter(id=request.POST.get("id"))
            else:
                data = Missions.objects.filter((Q(sender = user) | Q(majorcity__in = city) | Q(assistcity__in = city) | Q(receiptor = user)))
                status = request.POST.get("filter")
                if status != "-1":
                    data = data.filter(status = status)
            retData["recordsTotal"] = len(data)
            retData["recordsFiltered"] = len(data)
            data = json.loads(serializers.serialize("json", data))
            for item in data:
                dataJson = {}
                dataJson = item["fields"]
                dataJson["id"] = item["pk"]
                dataJson["date"] = dataJson["date"].replace("T", " ")
                #dataJson["sendername"] = dataJson["sendername"] + ("," + dataJson["senderphone"] if dataJson["senderphone"] else "")
                #if dataJson["receiptorname"]:
                    #dataJson["receiptorname"] = dataJson["receiptorname"] + ("," + dataJson["receiptorphone"] if dataJson["receiptorphone"] else "")
                
                try:
                    esData = es.get(index="clue", id=dataJson["dataid"])["_source"]
                    dataJson.update(esData)
                except:
                    esData = {}
                #dataJson["ip"] = esData.get("ip", "")
                #dataJson["controlip"] = esData.get("controlip", "")
                #dataJson["url"] = esData.get("url", "")
                #dataJson["email"] = esData.get("email", "")
                #dataJson["email2"] = esData.get("email2", "")
                #dataJson["hostfeature"] = esData.get("hostfeature", "")
                #dataJson["location"] = esData.get("location", "")
                #dataJson["time"] = esData.get("time", "")
                retData["data"].append(dataJson)
        return HttpResponse(json.dumps(retData))

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse(json.dumps({"draw": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}))  

def addMission(request):
    '''
    '''
    try:
        user = request.user.username
        mid = request.POST.get("mid")
        sendername = request.POST.get("sendername")
        senderphone = request.POST.get("senderphone")
        majorcity = request.POST.get("majorcity")
        assistcity = request.POST.get("assistcity")
        direction = request.POST.get("direction")

        receiveCity = filter(lambda item:item,[majorcity, assistcity])

        row = {"ip": request.POST.get("ip"),
               "controlip": request.POST.get("controlip"),
               "url": request.POST.get("url"),
               "email": request.POST.get("email"),
               "email2": request.POST.get("email2"),
               "hostfeature": request.POST.get("hostfeature"),
               "direction": direction,
               "city": receiveCity,
               "unit":"",
               "remark":"",
               "report":"",
               "location":request.POST.get("location"),
               "time": request.POST.get("time")
            }
        for key in row:
            try:
                row[key] = json.loads(row[key])
            except:
                pass
        fileToKeep = []

        fileList = map(lambda x : os.path.basename(x), request.POST.get("hostfeature").split(","))
        fileToKeep.extend(filter(lambda x : x and x not in fileToKeep,fileList))
        for item in fileToKeep:
            Files.objects.filter(name=item).update(stay = F("stay") + 1)
        Files.objects.filter(stay = 0).update(delete = F('delete') + 1)
        for item in Files.objects.filter(delete__gt = 50):
            os.remove(item.path)
            item.delete()    
        newmission = Missions.objects.create(sender = user,
                                             mid = mid,
                                             majorcity = majorcity,
                                             assistcity = assistcity,
                                             date = datetime.datetime.now(),
                                             status = 0,
                                             sendername = sendername,
                                             senderphone = senderphone,
                                             direction = direction)
        
        row["mission"] = newmission.id
        newclue = es.index(index = "clue", doc_type = "clue", body = row)
        newmission.dataid = newclue["_id"]
        newmission.save()
        for city in receiveCity:
            receivers = []
            groups =  Group.objects.filter(group_perms__perms__data = city)
            for item in groups:
                receivers.extend(map(lambda x:x.username, item.user_set.all())) 
            if not receivers:
                continue
            missionCounts = Missions.objects.filter(Q(majorcity=city,status=0) | Q(assistcity=city,status=0)).count()
            message = "<a href='/data/missionview' target='_blank'>" + u"您有" + str(missionCounts) + u"个新任务！" + "</a>"
            wrappedMessage = json.dumps({"message":message,"sender":u"任务提醒","broadcast":2,"missioncounts":1,"type":"newmission","date":datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")})
            redisMessage = RedisMessage(wrappedMessage)
            redis_publisher = RedisPublisher(facility='foobar', users=receivers)         
            redis_publisher.publish_message(redisMessage)

        action = "发布任务"
        writeLog(request, action)        
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')


def changeMStatus(request):

    try:
        missionID = request.POST.get("id")
        status = int(request.POST.get("status"))
        username = request.user.username
        _mission = Missions.objects.get(id=missionID)
        if status == 1:
            if _mission.status:
                return HttpResponse('{"code":1,"msg":"任务已经被其他用户领取，请刷新列表！"}')
            _mission.status = 1
            _mission.receiptor = username
            _mission.receiptorname = request.POST["receiptorname"]
            _mission.receiptorphone = request.POST["receiptorphone"]
            _mission.save()
            action = "领取任务"
        else:
            _mission.status = status
            action = "通过任务"
            if status == 4:
                action = "不通过任务"
            _mission.save()
            missionResult = {"3": "已通过","4": "不通过，请重新提交"}
            message = "<a href='/data/missionview?id="+str(_mission.id)+"' target='_blank'>" + u"编号：" + str(_mission.id) + u"任务" + missionResult[str(status)] + "</a>"
            wrappedMessage = json.dumps({"message":message,"sender":u"任务提醒","broadcast":2,"missioncounts":1,"type":"newmission","date":datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")})
            redisMessage = RedisMessage(wrappedMessage)
            redis_publisher = RedisPublisher(facility='foobar', users = [ _mission.receiptor])         
            redis_publisher.publish_message(redisMessage)                

        writeLog(request, action)        
        return HttpResponse('{"code":0}')


    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')

@csrf_exempt
@login_required
def multiSearch(request):

    try:
        mustList = []
        permsMustList = {"bool": {"should": []}}
        city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))
        direction = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="direction"))
        for item in city:
            if item == "省厅":
                permsMustList = False
                break
            else:
                permsMustList["bool"]["should"].append({"term": {"city": item}})
        if permsMustList:
            for item in direction:
                permsMustList["bool"]["should"].append({"term": {"direction": item}})
            mustList.append(permsMustList)

        query = json.loads(request.POST.get("query"))
        mustList.extend(query)
        for item in query:
            if item.has_key("match") or item.has_key("match_phrase"):
                action = "全文检索线索数据，关键词为：【"+item.values()[0].values()[0]+"】"
                writeLog(request, action)
        #if query["term"]:
            #mustList.append({"term":query["term"]})
        #if query["match"]:
            #mustList.append({"match":query["match"]})
            #action = "全文检索线索数据，关键词为：【"+query["match"].values()[0]+"】"
            #writeLog(request, action)            
        #if query["match_phrase"]:
            #mustList.append({"match_phrase":query["match_phrase"]})
            #action = "全文检索线索数据，关键词为：【"+query["match_phrase"].values()[0]+"】"
            #writeLog(request, action)          
        searchQuery = []
        searchQuery.append({"index":"ips","doc_type":"ips","search_type":"query_then_fetch"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList + [{"term": {"datatype": "ip"}}],
                }
            }
        })
        searchQuery.append({"index":"ips","doc_type":"ips"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList + [{"term": {"datatype": "url"}}],
                }
            }
        })
        searchQuery.append({"index":"ips","doc_type":"ips"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList + [{"term": {"datatype": "email"}}],
                }
            }
        })
        searchQuery.append({"index":"horse","doc_type":"horse"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList,
                }
            }
        })
        searchQuery.append({"index":"people","doc_type":"people"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList,
                }
            }
        })
        searchQuery.append({"index":"custom","doc_type":"custom"})
        searchQuery.append({
            "query": {
                "bool": {
                    "must" : mustList,
                }
            }
        })
        result = es.msearch(searchQuery)
        retData = {}
        index = ["ip", "url", "email", "horse", "people", "custom"]
        for i in range(6):
            retData[index[i]] = result["responses"][i]["hits"]["total"]
        return HttpResponse(json.dumps(retData))

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1,"msg":"服务器异常"}')
    
@csrf_exempt
@login_required
def availTime(request):
    try:
        if request.method == "POST":
            _type = request.POST.get("_type")
            key = request.POST.get("key")
            city = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="city"))
            direction = map(lambda x:x.perms.data, request.user.groups.get().group_perms_set.filter(perms__datatype="direction"))     
            mustList = []
            permsMustList = {"bool": {"should": []}}            
            for item in city:
                if item == "省厅":
                    permsMustList = False
                    break
                else:
                    permsMustList["bool"]["should"].append({"term": {"city": item}})
            if permsMustList:
                for item in direction:
                    permsMustList["bool"]["should"].append({"term": {"direction": item}})
                mustList.append(permsMustList)
            body = {
                "query": {
                    "bool": {
                        "must": mustList
                    }
                    },
                "size": 0
            }            
            retData = {
                "success": True,
                "results": [
                    #{
                        #"name"  : "全部",
                        #"value" : "all", 
                        #"text"  : "全部", 
                        #"disabled"  : False
                    #}
                ]
            }              
            if _type in ["year", "month"]:
                _format = {"year": "yyyy", "month": "yyyy-MM"}
                
                body["aggs"] = {
                      "aa": {
                        "date_histogram": {
                          "field": "time",
                          "format": _format[_type],
                          "min_doc_count": 1,
                          "interval": _type
                        }
                      }
                    }
                result = es.search(index="clue", doc_type="clue", body=body)
                for item in result["aggregations"]["aa"]["buckets"]:
                    data = item["key_as_string"]
                    if data.find(key) != -1:
                        retData["results"].append({"name":data, "value":data, "text":data, "disabled":False})    
                return HttpResponse(json.dumps(retData)) 
            
    except:
        print traceback.format_exc()
        logger.debug(traceback.format_exc())
        return HttpResponse('{"success":false}')        
    
    
    
    
    
@csrf_exempt
@login_required    
def auctionManage(request):
    try:
        if request.method == "POST":
            op = request.POST.get("op")
            #print ("can come to auctionManage")
            return (op in ["add", "edit"] and addAuction(request)) or (op == "get" and getAuction(request)) or (op == "delete" and delAuction(request)) 

    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        
        
 
                  
        



    
def addAuction(request):
    try:
        #print ("can come to addAuction")
        op =  request.POST["op"]
        _auction = {}
        for key in request.POST.keys():
            if key in ["op", "_id"]:
                continue
            else:
                data = request.POST.get(key)
                print data
                #try:
                _auction[key] = data 
                #except ValueError:
                    #_auction[key] =  json.loads(data["value"])

          
                
        if op == "add":    
            newauction = Auctions.objects.create(auctionid = _auction["auctionid"],
                                         auctionname = _auction["auctionname"],
                                         auctionprice = _auction["auctionprice"],
                                         auctionnum = _auction["auctionnum"],
                                         auctiondesc = _auction["auctiondesc"]
                                         )
        else:
            _id = request.POST["_id"]
            auction = Auctions.objects.filter(id = _id).update(auctionid = _auction["auctionid"],
                                                           auctionname = _auction["auctionname"],
                                                           auctionprice = _auction["auctionprice"],
                                                           auctionnum = _auction["auctionnum"],
                                                           auctiondesc = _auction["auctiondesc"]
                                                           )
        return HttpResponse('{"code":0}')
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1, "msg":"服务器异常"}')

def getAuction(request):
    try:
        #print ("come to here")
        retData = {
            "draw": 0,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "data": [],
        }
        if request.POST.get("id"):
            data = Auctions.objects.filter(id = request.POST.get("id"))
        else:
            data = Auctions.objects.all()
        
        retData["recordsTotal"] = len(data)
        retData["recordsFiltered"] = len(data)
        data = json.loads(serializers.serialize("json", data))
        #print data
        for item in data:
            dataJson =  {}
            dataJson = item["fields"]
            dataJson["id"] =  item["pk"]
            retData["data"].append(dataJson)
        #print retData
        return HttpResponse(json.dumps(retData))
    
    except:
        logger.debug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse(json.dumps({"draw": 0, "recordsTotal": 0, "recordsFiltered": 0, "data": []}))



def delAuction(request):
    try:
        
        ids = request.POST["ids"].split(",")
        print("can be here")
        print  ids
        for _id in ids:
            Auctions.objects.filter(id = _id).delete()
        return HttpResponse('{"code":0}')
    except:
        logger.dubug(traceback.format_exc())
        print traceback.format_exc()
        return HttpResponse('{"code":1, "msg":"服务器异常"}')
        