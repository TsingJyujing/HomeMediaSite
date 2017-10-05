# !/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2017-3-2
@author: Yuan Yi fan
"""
import os
import shutil
import datetime
import threadpool
import traceback
import cv2
from PIL import Image
from threading import Lock
# 如果直接执行的时候需要注意引用的库
import sys



sys.path.append("..")
from utility.files import get_extension
# from utility.str_util import *
from bdata.porn.caoliu import *
from utility.list_operation import list_unique
from utility.pyurllib import LiteDataDownloader
from config import local_images_path
from utility.connections import MongoDBCollection

insert_lock = Lock()

conn_pool_size = 32
thread_count = 32
page_to_read = 10
# 一个文件夹最少需要多少文件
files_count_limit_delete_dir = 2
# 图片文件保存的位置

# 定时运行参数
sleep_seconds = 23 * 3600  # 23Hours

# 初始化模型
model_file = "models/haarcascade_frontalface_alt2.xml"
face_cascade = cv2.CascadeClassifier(model_file)


def count_face(image_name, min_window=1.2, max_window=5):
    """
    Count faces in file by given parameters
    :param image_name:
    :param min_window:
    :param max_window:
    :return:
    """
    try:
        img = cv2.imread(image_name)
        return len(face_cascade.detectMultiScale(img, min_window, max_window))
    except:
        return 0


def count_face_in_dir(dir_name, min_window=1.2, max_window=5):
    """
    Count faces in dir
    :param dir_name:
    :param min_window:
    :param max_window:
    :return:
    """
    return sum(
        [count_face(os.path.join(dir_name, filename), min_window, max_window) for filename in os.listdir(dir_name)])


def write_face_count(coll, index, face_count):
    return coll.update_one({"_id": {"$eq": index}}, {"face_count": face_count}).modified_count > 0


def read_face_count(coll, index):
    return coll.find({"_id": index}).next()["face_count"]


def get_face_uncounted_index(coll):
    return [x["_id"] for x in coll.find({"face_count": {"$eq": None}})]


def count_faces():
    try:
        with MongoDBCollection("website_pron", "images_info") as coll:
            indexes = get_face_uncounted_index(coll)
            for i in indexes:
                try:
                    dir_name = os.path.join(local_images_path, "%08d" % i)
                    face = count_face_in_dir(dir_name, 1.1, 5)
                    write_face_count(coll, i, face)
                    print("There're %d faces in index=%d" % (face, i))
                except:
                    print("Error while counting faces in %d" % i)
    except Exception as err:
        print("Error while counting faces:\n" + traceback.format_exc())


def is_valid_image(filename):
    try:
        image_size = Image.open(filename).size
        assert len(image_size) >= 2
        assert image_size[0] > 240
        assert image_size[1] > 240
        return True
    except:
        return False


def remove_empty_dir(delete_limit):
    try:
        with MongoDBCollection("website_pron", "images_info") as coll:
            img_pool_dirs = os.listdir(local_images_path)
            for img_dir in img_pool_dirs:
                img_list_index = int(img_dir)
                current_dir = os.path.join(local_images_path, img_dir)
                files_in_dir = os.listdir(current_dir)
                for filename in files_in_dir:
                    full_filename = os.path.join(current_dir, filename)
                    is_valid = is_valid_image(full_filename)
                    if not is_valid:
                        os.remove(full_filename)
                        print("Image: %s deleted" % full_filename)
                files_in_dir = os.listdir(current_dir)
                if len(files_in_dir) <= delete_limit:
                    if not get_is_like(coll, img_list_index):
                        shutil.rmtree(current_dir)
                        remove_log(coll, img_list_index)
                        print("%d files in %s, removed." % (len(files_in_dir), img_dir))

    except Exception as err:
        print("Error while removing empty dir:\n" + traceback.format_exc())


def get_urls(n):
    urls = []
    for i in range(n):
        current_page_url = get_latest_urls(i + 1)
        print("Obtained %d urls in page %d" % (len(current_page_url), i + 1))
        urls += current_page_url
    return list_unique(urls)


def remove_log(coll, index):
    return coll.delete_one({"_id": {"$eq": index}}).deleted_count > 0


def is_url_existed(coll, url):
    return coll.count({"page_url": url})


def get_is_like(coll, index):
    return coll.find({"_id": index}).next()["like"]


def insert_log(coll, title, url, comment_text, image_urls):
    try:
        insert_lock.acquire()
        next_index = coll.find().sort("_id", -1).next()["_id"] + 1
        return coll.insert_one({
            "_id": next_index,
            "page_url": url.replace("http://%s/" % caoliu_host, "/"),
            "title": title,
            "block": "daguerre".upper(),
            "like": False,
            "image_urls": image_urls,
            "comment": comment_text
        }).inserted_id
    finally:
        insert_lock.release()


def process_page_url(url):
    try:
        with MongoDBCollection("website_pron", "images_info") as coll:
            if is_url_existed(coll, url.replace("http://%s/" % caoliu_host, "/")):
                raise Exception("URL is existed in db!")
            page_soup = get_soup(url)
            title = get_page_title(page_soup)
            images = get_page_images(page_soup)
            text = get_page_text(page_soup)
            # 下载小文件
            img_task_list = [
                LiteDataDownloader(image_url=img, tag="%d%s" % (i, get_extension(img)))
                for i, img in enumerate(images)]
            for task in img_task_list:
                task.start()
            for task in img_task_list:
                task.join()
            page_index = insert_log(coll, title, url, text, images)
            page_path = os.path.join(local_images_path, "%08d" % page_index)
            try:
                os.makedirs(page_path)
            except:
                print("dir may existed.")
            for task in img_task_list:
                task.write_file(os.path.join(page_path, task.tag))
            # create tasks
            print("Downloaded: %s" % url)

    except Exception as ex:
        print("Error while downloading..." + traceback.format_exc())


def download_image_lists(n):
    pool = threadpool.ThreadPool(thread_count)
    for i in range(n):
        try:
            urls = get_latest_urls(i + 1)
            print("Obtained %d urls in page %d" % (len(urls), i + 1))
            requests = threadpool.makeRequests(process_page_url, urls)
            [pool.putRequest(req) for req in requests]
            print("Requests appended to thread pool")
        except Exception as _:
            print("Error while appending thread pool\n" + traceback.format_exc())
    pool.wait()


def execute_one_cycle():
    print("Initialized, downloading...")
    download_image_lists(page_to_read)
    print("Downloaded, cleaning...")
    remove_empty_dir(files_count_limit_delete_dir)
    # count_faces()


if __name__ == "__main__":
    execute_one_cycle()
    with open("run.log", "a") as fid:
        fid.write("Updated in " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
