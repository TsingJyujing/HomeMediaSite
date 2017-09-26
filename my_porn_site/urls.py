# -*- coding: utf-8 -*-
"""my_porn_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from daf.views import *
from task_manager.views import *
from page_render.views import *

urlpatterns = [

    url(r'^admin/', admin.site.urls),

    # 获取某一个ID下所有的图片和基础信息
    url(r'^get/images/', get_images_info),

    # 获取某一个ID的小说内容和基础信息
    url(r'^get/novel/', get_novel),

    # 依据标题搜索小说
    url(r'^query/novel/bytitle', query_novel_by_title),

    # 依据标题搜索视频（板块信息不完善）
    url(r'^query/video/bytitle', query_video_list),

    # 依据标题搜索图帖信息
    url(r'^query/images/bytitle', query_images_list),

    # 依据标题搜索图帖信息
    url(r'^query/images/nearby', get_nearby_images),

    # 根据ID查询视频的基础信息
    url(r'^query/video/byid', query_video),

    # 根据ID删除视频
    url(r'^remove/video', remove_video),

    # 根据ID删除视频
    url(r'^remove/novel', remove_novel),

    # 根据ID删除视频
    url(r'^remove/images', remove_images),

    # 设置是否喜欢视频
    url(r'^set/video/like', set_video_like),

    # 设置是否喜欢图片集
    url(r'^set/images/like', set_images_like),

    # 设置是否喜欢小说
    url(r'^set/novel/like', set_novel_like),

    # 获取所有正在进行的任务
    url(r'^query/task/all', query_tasks),

    # 查询小说的页面渲染
    url(r'^view/query/novel', render_query_novel),

    # 查询视频的页面渲染
    url(r'^view/query/video', render_query_video),

    # 查询视频的页面渲染
    url(r'^view/query/images', render_query_images),

    # 查询视频的页面渲染
    url(r'^view/images', render_view_images),

    # 浏览小说的页面
    url(r'^view/novel', render_novel_reader),

    # 添加任务
    url(r'^append/task', append_task),

    # 移除任务
    url(r'^remove/task', remove_task),

    # 任务管理界面
    url(r'^manage/tasks', render_task_manage_page),

    # 主页
    url(r'^$', render_index_page),
]
