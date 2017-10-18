#!/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-2-4
@author: Yuan Yi fan

配置文件，记录各种配置
"""
import os

# 请求超时设置
request_timeout = 600

# 浏览器的User Agent参数
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + \
             "AppleWebKit/537.36 (KHTML, like Gecko) " + \
             "Chrome/42.0.2311.135 " + \
             "Safari/537.36 " + \
             "Edge/12.10240"

# 是否类Unix系统
is_unix = os.getcwd().startswith("/")

# 自动修改路径的程序
def auto_fix_path(unix_path):
    if is_unix:
        return unix_path
    else:
        return unix_path.replace("/mnt/d/", "d:/")


# XML解析器
XML_decoder = 'lxml'

# 临时文件存储规则
video_temp = "buffer/video_temp_%X.mp4"
shortcuts_temp = "buffer/shortcuts_temp_%X.gif"

# Web主文件夹
media_file_dir = auto_fix_path("/mnt/d/Data/WebServer/")

# 视频文件/预览图片保存路径模板
video_saving_path = media_file_dir + "video/file/porv_%d.mp4"
shortcuts_saving_path = media_file_dir + "video/preview/prev_%d.gif"

trash_video_dir = media_file_dir + "trash/video/"
trash_video_file = trash_video_dir + "porv_%d.mp4"
trash_video_info = trash_video_dir + "porv_%d.json"

"""
Should inited by dict, for example:
{
    "page_index":10200,
    "image_filename":"0.jpg"
}
"""
image_url_template = "/file/images/%(page_index)08d/%(image_filename)s"

local_images_path = auto_fix_path("/mnt/d/Data/WebServer/images/")
local_image_list_path = auto_fix_path("/mnt/d/Data/WebServer/images/%(page_index)08d/")
local_novel_path_gen = auto_fix_path("/mnt/d/Data/WebServer/novel/%d.txt")
trash_novel_path_gen = auto_fix_path("/mnt/d/Data/WebServer/trash/novel/%s.txt")
trash_image_path_gen = auto_fix_path("/mnt/d/Data/WebServer/trash/images/%(page_index)08d/")
