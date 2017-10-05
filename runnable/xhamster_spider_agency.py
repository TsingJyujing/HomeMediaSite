import sys
import json
import time
import base64
import threading
import traceback

sys.path.append("..")

from config import request_timeout
from utility.connections import MongoDBDatabase, MongoDBCollection
from utility.debug_tool import LastOpMonitor
from utility.pyurllib import urlread2, URLReadThread

concurrency_num = 32
failed_time_limit = 10
agency_address = "http://47.90.245.126:8087"


def url_read_json(url):
    th = URLReadThread(url)
    th.start()
    th.join(request_timeout)
    if th.data is None:
        raise Exception("Error while reading API:" + url)
    obj = json.loads(urlread2(url))
    if obj.has_key("status"):
        if obj["status"] == "error":
            raise Exception("Error in remote API:" + json.dumps(obj))
    return obj


def get_top_urls(page_index):
    return [base64.b64decode(x).decode("UTF-8") for x in
            url_read_json(agency_address + "/agency/xhamster/query/top/?index=%d" % page_index)["data"]]


def query_url(url):
    return url_read_json(agency_address + "/agency/xhamster/query/info?url=" + base64.b64encode(url.encode("UTF-8")))


class SpiderThread(threading.Thread):
    def __init__(self, db_name="spider", coll_prefix="xhamster"):
        threading.Thread.__init__(self)
        self.db_name = db_name
        self.coll_prefix = coll_prefix
        self.last_op = "Uninited."

    @property
    def last_op(self):
        return self._last_op

    @last_op.setter
    def last_op(self, value):
        self._last_op = value + "%f" % time.time()

    def run(self):
        try:
            # print("Process started: " + self.name)
            self.last_op = "Inited."
            with MongoDBDatabase(self.db_name) as mongoDB:
                failed_times = 0
                waitingColl = mongoDB.get_collection(self.coll_prefix + "_queue")
                runningColl = mongoDB.get_collection(self.coll_prefix + "_running")
                storageColl = mongoDB.get_collection(self.coll_prefix + "_storage")
                coll_list = (waitingColl, runningColl, storageColl)
                while True:
                    if failed_times >= failed_time_limit:
                        print("Failed too much, ended: " + self.name)
                        break
                    task = waitingColl.find_one_and_delete({})
                    self.last_op = "Got a task."
                    if task is None:
                        failed_times += 1
                        print("Failed: " + self.name)
                        self.last_op = "Fail sleeping."
                        time.sleep(2)
                    else:
                        url = task["_id"]
                        try:
                            runningColl.insert_one({"_id": url})
                            if storageColl.find_one({"_id": url}, {"_id": 1}) is None:
                                self.last_op = "Querying."
                                doc_storage = query_url(url)
                                self.last_op = "Queried."
                                relatedURLs = doc_storage.pop("related")
                                runningColl.delete_one({"_id": url})
                                storageColl.insert_one(doc_storage)
                                self.last_op = "Inserted, appending."
                                for task in relatedURLs:
                                    condition_doc = {"_id": task.split("?")[0]}
                                    if all((coll.find_one(condition_doc, {"_id": 1}) is None for coll in coll_list)):
                                        waitingColl.insert_one(condition_doc)
                            else:
                                print("DUMP  : %s" % url)
                            failed_times = 0
                        except:
                            print("ERROR :%s" % url)
                            waitingColl.insert_one({"_id": url})
                            runningColl.delete_one({"_id": url})
                            failed_times += 1
                            print("Errored: " + self.name)
        except Exception as exc:
            print("THREAD TERMINATED ABNORMALLY!" + self.name)
            print(traceback.format_exc())
            self.last_op = "\n" + traceback.format_exc()
        finally:
            print("THREAD TERMINATED NORMALLY!" + self.name)
            print(traceback.format_exc())
            self.last_op = "\n" + traceback.format_exc()


if __name__ == '__main__':
    dbName = "spider"
    collPrefix = "xhamster"

    with MongoDBDatabase(dbName) as mgdb:
        for res in mgdb.get_collection(collPrefix + "_running").find({}):
            try:
                mgdb.get_collection(collPrefix + "_queue").insert(res)
            except:
                pass
        mgdb.get_collection(collPrefix + "_running").drop()

    with MongoDBCollection(dbName, collPrefix + "_queue") as coll:
        if coll.count() <= 0:
            for i in range(3):
                for url in get_top_urls(i + 1):
                    try:
                        coll.insert({"_id": url})
                    except:
                        print("Error while inserting " + url)

    thread_list = [SpiderThread(db_name=dbName, coll_prefix=collPrefix) for _ in range(concurrency_num)]
    [t.start() for t in thread_list]
    opThread = LastOpMonitor(thread_list, 5)
    # opThread.start()
    [t.join() for t in thread_list]
