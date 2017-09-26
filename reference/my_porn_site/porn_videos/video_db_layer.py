# coding:utf-8
"""
模块设计：所有视频的数据库交互和某一个文件的交互全部在这里完成
主要支持的功能：

增加：
    暂不支持

删除：
    删除某一视频以及文件

修改：
    增加某个Tag
    删除某个Tag

查找：
    分页查找最新的N条视频
    随机找出N条视频
    找出对应某一ID的视频
    获取所有的Tag(Dict)
    分页查找最喜欢的视频
"""
import json
from util.db import *

class video_data():
    def __init__(self):
    
"""
第一组API：查询数据库里的视频信息
index, tags, basic_info, like_it 
"""
def query_video_by_id(id):
    sql_cmd = """
    SELECT index, tags, basic_info, like_it, similarity_video_indexes
    FROM public.video_basic_info 
    WHERE index=%d
        """ % (id)
    res = fetchSQL(sql_cmd)[0] #仅保留第一行
    
    