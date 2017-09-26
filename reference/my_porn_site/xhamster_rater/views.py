# coding:utf-8
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from util import db, funs
import string


def index(request):
    return HttpResponseRedirect("/view_videos/")
    #return HttpResponse(u"Connected@" + request.META["HTTP_HOST"])


def get_randomly(request):
    conn = db.genSQLConnection()
    try:
        rateVideo(conn,
                     string.atoi(request.GET['id']),
                     string.atof(request.GET['rate']))
    except Exception, e:
        print "Error", e.message
    search_result = queryRandomUnratedVideo(conn)
    return render(request, "rand_rate.html", search_result)
    
def get_recommend(request):
    conn = db.genSQLConnection()
    try:
        rateVideo(conn,
                 string.atoi(request.GET['id']),
                 string.atof(request.GET['rate']))
    except Exception, e:
        print "Error", e.message
    search_result = queryRecommandUnratedVideo(conn)
    return render(request, "rand_rate.html", search_result)


def queryRandomUnratedVideo(sql_connection):
    cur = sql_connection.cursor()
    sql_cmd = "select id, title, img_urls, categories, video_time " \
              "from xhamster_spider where myrate is null order by random() limit 1 offset 0"
    cur.execute(sql_cmd)
    res = cur.fetchall()
    cur.close()
    if len(res) == 0:  # Can't find info
        raise Exception("Can't find log in database.")
    else:
        res = res[0]
        result = {
            "id": res[0],
            "title": res[1].replace("`", "'"),
            "img_urls": res[2],
            "categories": res[3],
            "video_time": funs.time2duration(res[4])
        }
    return result


def queryRecommandUnratedVideo(sql_connection):
    cur = sql_connection.cursor()
    sql_cmd = "select id, title, img_urls, categories, video_time " \
              "from xhamster_spider where myrate is null order by recommand_info limit 1 offset 0"
    cur.execute(sql_cmd)
    res = cur.fetchall()
    cur.close()
    if len(res) == 0:  # Can't find info
        raise Exception("Can't find log in database.")
    else:
        res = res[0]
        result = {
            "id": res[0],
            "title": res[1].replace("`", "'"),
            "img_urls": res[2],
            "categories": res[3],
            "video_time": funs.time2duration(res[4])
        }
    return result


def rateVideo(sql_connection, id, rate):
    sql_cmd = "UPDATE xhamster_spider SET myrate=%f WHERE id=%d" % (rate, id)
    cur = sql_connection.cursor()
    cur.execute(sql_cmd)
    sql_connection.commit()
    cur.close()
