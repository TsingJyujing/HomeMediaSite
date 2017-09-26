"""my_porn_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from xhamster_rater import views as xhamster_rater_views
from porn_videos import views as porn_video_views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', xhamster_rater_views.index),
    url(r'^rand_rate/', xhamster_rater_views.get_randomly),
    url(r'^reco_rate/', xhamster_rater_views.get_recommend),
    url(r'^view_videos/preview_gif/', porn_video_views.getPreviewImage),
    url(r'^modify_video_tag', porn_video_views.modify_video_tag),
    url(r'^star_video/', porn_video_views.star_video_page),
    url(r'^view_videos/', porn_video_views.view_videos),
    url(r'^view_images/', porn_video_views.view_images),
    url(r'^random_images/', porn_video_views.random_images),
    url(r'^query_images/', porn_video_views.query_images),
    url(r'^star_image_page/', porn_video_views.star_image_page),
    url(r'^delete_video/', porn_video_views.delete_video),
    url(r'^delete_images/', porn_video_views.delete_images),
]
