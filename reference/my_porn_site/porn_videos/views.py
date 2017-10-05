# coding:utf-8

import os
import re
import string
import mimetypes
from image_render import *
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.shortcuts import render
from wsgiref.util import FileWrapper
from util.httputils import *
from util.db import *
from util.config import *
import shutil
import json
import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
    
range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

def modify_video_tag(request):
    try:
        ID = string.atoi(get_request_get(request, 'id'))
        Tag = get_request_get(request, 'tag')
        Operation = get_request_get(request, 'op')
        if Operation not in ["add","dec"]:
            raise Exception("Operation not defined")
        queryResult = fetchSQL("SELECT tags FROM public.video_basic_info WHERE index = %d" % ID)[0][0]
        tags = set(queryResult)
        if Operation=="add":
            tags.add(Tag)
        else:
            tags.discard(Tag)
        jtags = json.dumps([x for x in tags])
        SQLExeCmd = "UPDATE public.video_basic_info SET tags='%s' WHERE index=%d" % (jtags,ID)
        execSQL(SQLExeCmd)
        return HttpResponse("success")
    except Exception, e:
        return HttpResponse(e.message)
        
def random_images(request):
    try:
        return view_images_render(request, True)
    except Exception, e:
        print "Error message:", e.message
        return HttpResponse("Error while processing parameters." + e.message)
        
def delete_video(request):
    try:
        ID = string.atoi(get_request_get(request, 'id'))
        sqlQuery = "SELECT basic_info->>'name' as video_name FROM public.video_basic_info WHERE index=%d" % (ID)
        queryRes = fetchSQL(sqlQuery)[0][0]
        sqlQuery = "DELETE FROM public.video_basic_info WHERE index=%d" % (ID)
        execSQL(sqlQuery)
        shutil.move(pvideo_path + pvideo_file % ID, pvideo_path_delete + queryRes)
        return HttpResponse("success")
    except Exception, e:
        return HttpResponse("Error while processing parameters." + e.message)
        

def delete_images(request):
    try:
        ID = string.atoi(get_request_get(request, 'id'))
        sqlQuery = "DELETE FROM public.img_list WHERE index=%d" % (ID)
        execSQL(sqlQuery)
        shutil.move(
            pimage_dir_local + "%08d" % ID,
            pimage_dir_delete)
        return HttpResponse("success")
    except Exception, e:
        return HttpResponse("Error while processing parameters." + e.message)
        
        
def view_images(request):
    try:
        return view_images_render(request, False)
    except Exception, e:
        print "Error message:", e.message
        return HttpResponse("Error while processing parameters." + e.message)
        
def query_images(request):
    try:
        return query_images_render(request)
    except Exception, e:
        print "Error message:", e.message
        return HttpResponse("Error while processing parameters." + e.message)
        
def star_image_page(request):
    try:
        return star_image_page_render(request)
    except Exception, e:
        print "Error message:", e.message
        return HttpResponse("Error while processing parameters." + e.message)
        
def star_video_page(request):
    ID = string.atoi(get_request_get(request, 'id'))
    islike = string.atoi(get_request_get(request, 'like'))
    sqlQuery = "UPDATE public.video_basic_info SET like_it=%d WHERE index=%d" % (islike,ID)
    execSQL(sqlQuery)
    return HttpResponse("success")
    
def view_videos(request):
    ID = get_request_get(request, 'id')
    hostAddress = request.META["HTTP_HOST"].split(":")[0]
    if ID is not None:
        ID = string.atoi(ID)
    query = get_request_get(request, 'query')
    new = get_request_get(request, 'new')
    pagesize = string.atoi(get_request_get_default(request, 'pagesize', default_pagesize))
    pageid = string.atoi(get_request_get_default(request, 'pageid', '1'))
    if query is None and new is None and ID is None:
        """
        标记为Like的视频
        """
        offset = (pageid - 1) * pagesize
        sql_query = """
                    SELECT  index, tags, basic_info, like_it 
                    FROM public.video_basic_info 
                    WHERE like_it>0
                    ORDER BY index desc 
                    LIMIT %d 
                    OFFSET %d
                    """ % (pagesize, offset)
        queryResult = fetchSQL(sql_query)
        resultSetSize = len(queryResult)
        renderInfo = generateRenderStruct(queryResult, hostAddress)
        # 翻页显示控制
        if pageid > 0:
            renderInfo["paginationList"].append({
                'url': "./?pageid=%d" % 0,
                "text": "<<"
            })
            renderInfo["paginationList"].append({
                'url': "./?pageid=%d" % ( pageid - 1),
                "text": "<"
            })
        if resultSetSize>=pagesize:
            renderInfo["paginationList"].append({
                'url': "./?pageid=%d" % (pageid + 1),
                "text": ">"
            })
        return render(request, "view_video.html", renderInfo)

    elif query is not None and new is None and ID is None:
        """
        搜索视频
        """
        sqlCondition = " or ".join([("basic_info->>'name' like '%%%s%%'" % x) for x in query.split(" ")])
        offset = (pageid - 1) * pagesize
        sql_query = """
                    SELECT  index, tags, basic_info, like_it 
                    FROM public.video_basic_info 
                    WHERE %s
                    ORDER BY index desc 
                    LIMIT %d 
                    OFFSET %d
                    """ % (sqlCondition, pagesize, offset)
        queryResult = fetchSQL(sql_query)
        resultSetSize = len(queryResult)
        renderInfo = generateRenderStruct(queryResult, hostAddress)
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
        return render(request, "view_video.html", renderInfo)

    elif query is None and new == "1" and ID is None:
        """
        依照分页规则获取最新的pagesize条数据
        """
        offset = (pageid - 1) * pagesize
        sql_query = """
                    SELECT  index, tags, basic_info, like_it 
                    FROM public.video_basic_info 
                    ORDER BY index desc 
                    LIMIT %d 
                    OFFSET %d
                    """ % (pagesize, offset)
        queryResult = fetchSQL(sql_query)
        resultSetSize = len(queryResult)
        renderInfo = generateRenderStruct(queryResult, hostAddress)
        # 翻页显示控制
        if pageid > 0:
            renderInfo["paginationList"].append({
                'url': "./?new=1&pageid=%d" % 0,
                "text": "<<"
            })
            renderInfo["paginationList"].append({
                'url': "./?new=1&pageid=%d" % (pageid - 1),
                "text": "<"
            })
        if resultSetSize>=pagesize:
            renderInfo["paginationList"].append({
                'url': "./?new=1&pageid=%d" % (pageid + 1),
                "text": ">"
            })
        return render(request, "view_video.html", renderInfo)
    elif query is None and new == "0" and ID is None:
        """
        随机视频
        """
        offset = 0
        sql_query = """
                    SELECT  index, tags, basic_info, like_it 
                    FROM public.video_basic_info 
                    ORDER BY random()
                    LIMIT %d 
                    OFFSET %d
                    """ % (pagesize, offset)
        queryResult = fetchSQL(sql_query)
        resultSetSize = len(queryResult)
        renderInfo = generateRenderStruct(queryResult, hostAddress)
        # 翻页显示控制
        renderInfo["paginationList"].append({
            'url': "./?new=0",
            "text": "刷新"
        })
        return render(request, "view_video.html", renderInfo)
    elif query is None and new is None and ID is not None:
        """
        仅仅显示一个视频的信息
        并且显示标记Tag的按钮，以及详细设置的控件
        """
        """
        依照分页规则获取最新的pagesize条数据
        """
        sql_query = """
                    SELECT  index, tags, basic_info, like_it 
                    FROM public.video_basic_info 
                    WHERE index=%s
                    LIMIT 1
                    OFFSET 0
                    """ % ID
        queryResult = fetchSQL(sql_query)
        like_it_info = queryResult[0][3]>0
        sqlQuery = "SELECT tag_id, tag_info FROM public.tag_info;"
        tagAllSet = fetchSQL(sqlQuery)
        tagDict = {}
        for row in tagAllSet:
            tagDict[row[0]] = row[1]
        tagSet = set([x[0] for x in tagAllSet])
        renderInfo = generateRenderStruct(queryResult, hostAddress)
        
        for videoInfo in renderInfo["videoInfoList"]:
            exset = [x["tagID"] for x in videoInfo["tagList"]]
            tagList = list(tagSet - set(exset))
            videoInfo["addTagList"] = [{"tagID":x,"tagText":tagDict[x]} for x in tagList]
            videoInfo["id"] = ID
            videoInfo["like_this_video"] = like_it_info
        return render(request, "single_video.html", renderInfo)
    else:
        raise Exception("Error parameters")
    return HttpResponse("Unachievable place")


def getPreviewImage(request):
    try:
        ID = request.GET['id']
        filename = preview_dir + preview_file % ID
        response = StreamingHttpResponse(file_iterator(filename))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(preview_file % ID)
        return response
    except:
        return HttpResponse("CDN Error: error while processing parameters.")


def file_iterator(file_name, chunk_size=4096):
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

# TEST VIEW VIDEO
def testViewVideo(request):
    return render(request, "view_video.html", {
        "title": "Test Video",
        "videoInfoList": [
            {
                "previewUrl": "http://192.168.1.103/prev_1128.gif",
                "mp4Url": "http://192.168.1.103/porv_1128.mp4",
                "videoTitle": "VideoTest1",
                "playTime": "10:25",
                "resolution": "100×150",
                "tagList": ["porn", "pussy wide"],
            },
            {
                "previewUrl": "http://192.168.1.103/prev_1128.gif",
                "mp4Url": "http://192.168.1.103/porv_1128.mp4",
                "videoTitle": "VideoTest2",
                "playTime": "10:25",
                "resolution": "100×150",
                "tagList": [
                    "porn", "anal", "homemade", "porn", "anal", "homemade",
                    "porn", "anal", "homemade", "porn", "anal", "homemade",
                    "porn", "anal", "homemade", "porn", "anal", "homemade",
                ],
            },
        ],"paginationList":[
            {'url':"javascript:alert(1);", "text":1},
            {'url': "javascript:alert(2);", "text": 2},
            {'url': "javascript:alert(3);", "text": 3},
        ]})


def testIterator(request):
    return render(request, "test_iterator.html",
                  {"testList": [
                      {'a': ['a', 'b', 'v'], 'b': 2},
                      {'a': ['a1', 'b1', 'v1'], 'b': 2, "c": 'd'},
                      {'a': ['a2', 'b', 'v'], 'b': 2, "c": 1},
                  ]})


def generateRenderStruct(queryResult, hostAddress):
    tagAllSet = fetchSQL("SELECT tag_id,tag_info FROM public.tag_info;")
    tagDict = {}
    for row in tagAllSet:
        tagDict[row[0]] = row[1]
        
    renderInfo = {"title": "Video System", "paginationList": [], "videoInfoList": []}
    for resRow in queryResult:
        id = resRow[0]
        listTags = resRow[1]
        basicInfo = resRow[2]
        renderInfo["videoInfoList"].append({
            "previewUrl": preview_dir % (hostAddress,CDNPort) + preview_file % id,
            "mp4Url": pvideo_dir % (hostAddress,CDNPort) + pvideo_file % id,
            "videoTitle": basicInfo["name"],
            "playTime": basicInfo["duration"],
            "resolution": "%d×%d" % (basicInfo["width"], basicInfo["height"]),
            "tagList": [{"tagID":x,"tagText":tagDict[x]} for x in listTags],
            "id":id
        })
    return renderInfo
