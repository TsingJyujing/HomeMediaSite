import sys
sys.path.append("..")
from utility.connections import MongoDBCollection, ExtSSHConnection
from config import *

remote_video_path = "/media/yuanyifan/ext_data/webserver/video/file/porv_%d.mp4"
remote_video_preview_path = "/media/yuanyifan/ext_data/webserver/video/preview/prev_%d.gif"


def migrate_videos_from_server():
    with MongoDBCollection("website_pron", "video_info", host="192.168.1.103") as remote_coll:
        with MongoDBCollection("website_pron", "video_info") as local_coll:
            with ExtSSHConnection("192.168.1.103", "yuanyifan", "979323") as ext_ssh:
                for doc in remote_coll.find({"$or": [{"source": {"$ne": None}}, {"like": True}]}):
                    _id = doc["_id"]
                    if local_coll.find_one({"_id": _id}) is None:
                        print("Downloading...")
                        print(doc)
                        ext_ssh.sftp_conn.get(remote_video_preview_path % _id, shortcuts_saving_path % _id)
                        ext_ssh.sftp_conn.get(remote_video_path % _id, video_saving_path % _id)
                        local_coll.insert_one(doc)


if __name__ == '__main__':
    migrate_videos_from_server()
