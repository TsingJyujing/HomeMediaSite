# coding:utf-8

import os
import re
import string
import mimetypes

from util.httputils import *
from util.db import *
from util.config import *
from django.http import HttpResponse
from django.shortcuts import render

def modify_image_tags(request):
    sqlQuery = "SELECT \"like\" is null or \"like\"!=1 FROM public.img_list WHERE index=%d" % ID

def star_image_page_render(request):
    ID = string.atoi(get_request_get(request, 'id'))
    sqlQuery = "SELECT \"like\" is null or \"like\"!=1 FROM public.img_list WHERE index=%d" % ID
    queryResult = fetchSQL(sqlQuery)[0][0]
    if queryResult:
        sqlQuery = "UPDATE public.img_list SET \"like\" = 1 WHERE index=%d" % ID
        return_info = "liked"
    else:
        sqlQuery = "UPDATE public.img_list SET \"like\" = 0 WHERE index=%d" % ID
        return_info = "disliked"
    executeSQLNewConn(sqlQuery)
    return HttpResponse(return_info)

def view_images_render(request, randomImage):
    frameCount = 2
    hostAddress = request.META["HTTP_HOST"].split(":")[0]
    if randomImage:
        sqlQuery = "select title, block, simindex, comment, index FROM public.img_list ORDER BY random() LIMIT 1 OFFSET 0"
        queryResult = fetchSQL(sqlQuery)[0]
        ID = queryResult[4]
    else:
        ID = string.atoi(get_request_get(request, 'id'))
        sqlQuery = "select title, block, simindex, comment FROM public.img_list where index=%d" % ID
        queryResult = fetchSQL(sqlQuery)[0]
    renderInfo = {"id":ID,"title":"[%s] %s" % (queryResult[1], queryResult[0]),"comment_text":queryResult[3]}
    dir_path = pimage_dir_local + "%08d/" % ID
    file_list = os.listdir(dir_path)
    fileSize = len(file_list)
    rowSize = (fileSize-1)/frameCount + 1
    renderInfo["imgGroupList"] = [];
    for rowIndex in range(rowSize):
        imgGroup = []
        for i in range(frameCount):
            imgInfo = {}
            indexReal = rowIndex*frameCount + i
            if indexReal>=fileSize:
                break
            imgInfo["frameSize"] = 12/frameCount
            imgInfo["filename"] = file_list[indexReal]
            imgInfo["url"] = "http://%s:%d/external/img_pool/" % (hostAddress,80) + "%08d/" % ID + file_list[indexReal]
            imgGroup.append(imgInfo)
        renderInfo["imgGroupList"].append(imgGroup)
    try:
        sqlQuery = "select title, block, index FROM public.img_list where index>%d order by index limit 1 offset 0" % ID
        queryResult = fetchSQL(sqlQuery)[0]
        renderInfo["nextInfo"] = {"title":"[%s] %s" % (queryResult[1], queryResult[0]), "id":queryResult[2]}
    except:
        renderInfo["nextInfo"] = {"title":"找不到", "id":0}
        
    try:
        sqlQuery = "select title, block, index FROM public.img_list where index<%d order by index desc limit 1 offset 0" % ID
        queryResult = fetchSQL(sqlQuery)[0]
        renderInfo["lastInfo"] = {"title":"[%s] %s" % (queryResult[1], queryResult[0]), "id":queryResult[2]}
    except:
        renderInfo["lastInfo"] = {"title":"找不到", "id":0}
    return render(request, "view_image.html", renderInfo)
    
    
def query_images_render(request):
    frameCount = 2
    query = get_request_get(request, 'query')
    type = get_request_get(request, 'type')
    pagesize = string.atoi(get_request_get_default(request, 'pagesize', default_imglist_pagesize))
    pageid = string.atoi(get_request_get_default(request, 'pageid', '1'))
    offset = (pageid-1)*pagesize
    hostAddress = request.META["HTTP_HOST"].split(":")[0]
    if type is None and query is not None:
        sqlCondition = " or ".join([("title like '%%%s%%'" % x) for x in query.split(" ")])
        sqlQuery = "SELECT index, title, block, imgcount FROM public.img_list where %s order by index desc limit %d offset %d" % (sqlCondition, pagesize, offset)
        queryResult = fetchSQL(sqlQuery)
        resultSetSize = len(queryResult)
        renderInfo = {"title":"图片引擎","imgInfoList":[],"paginationList":[]}
        for resRow in queryResult:
            imgInfo = {}
            imgInfo["id"] = resRow[0]
            imgInfo["showText"] = "[%s] [%d Pics] %s" % (resRow[2],resRow[3],resRow[1])
            renderInfo["imgInfoList"].append(imgInfo)
        #翻页显示控制
        if pageid > 0:
            renderInfo["paginationList"].append({
                'url': "./?query=%s&pageid=%d" % (query, 0),
                "text": "<<"
            })
            renderInfo["paginationList"].append({
                'url': "./?query=%s&pageid=%d" % (query, (pageid - 1)),
                "text": "<"
            })
        if resultSetSize>=pagesize:
            renderInfo["paginationList"].append({
                'url': "./?query=%s&pageid=%d" % (query, (pageid + 1)),
                "text": ">"
            })
        return render(request, "query_image.html", renderInfo)
    #elif type=="like" and query is None:
    else:
        sqlQuery = "SELECT index, title, block, imgcount FROM public.img_list where \"like\">0 order by imgcount desc limit %d offset %d" % (pagesize, offset)
        queryResult = fetchSQL(sqlQuery)
        renderInfo = {"title":"图片引擎","imgInfoList":[],"paginationList":[]}
        for resRow in queryResult:
            imgInfo = {}
            imgInfo["id"] = resRow[0]
            imgInfo["showText"] = "[%s] [%d Pics] %s" % (resRow[2],resRow[3],resRow[1])
            renderInfo["imgInfoList"].append(imgInfo)
        query = "like"
        #翻页显示控制
        if pageid > 0:
            renderInfo["paginationList"].append({
                'url': "./?type=%s&pageid=%d" % (query, 0),
                "text": "<<"
            })
            renderInfo["paginationList"].append({
                'url': "./?type=%s&pageid=%d" % (query, (pageid - 1)),
                "text": "<"
            })
        renderInfo["paginationList"].append({
            'url': "./?type=%s&pageid=%d" % (query, (pageid + 1)),
            "text": ">"
        })
        return render(request, "query_image.html", renderInfo)
        
