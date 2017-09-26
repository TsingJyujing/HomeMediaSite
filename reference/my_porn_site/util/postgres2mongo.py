import pymongo
import psycopg2
import math


def get_mongo_connection():
    return pymongo.MongoClient("localhost", 27017)


def get_pg_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="979323",
        database="pvideo"
    )


def migrate_images():
    mgconn = get_mongo_connection()  # IDE Code
    pgconn = get_pg_connection()

    collection = mgconn.get_database("website_pron").get_collection("images_info")
    collection.drop()

    cur = pgconn.cursor()
    cur.execute("SELECT index, title, block, \"like\", url, image_urls,face_count  FROM public.img_list")

    for row in cur.fetchall():
        doc = {
            "_id": row[0],
            "title": str(row[1]),
            "like": row[3] > 0,
            "block": str(row[2]).upper()

        }
        if row[5] is not None:
            if len(row[5]) > 0:
                doc["image_urls"] = [str(url) for url in row[5]]

        if row[4] is not None:
            doc["page_url"] = row[4]

        if row[6] >= 0:
            doc["face_count"] = int(row[6])

        collection.insert_one(doc)

    cur.close()
    pgconn.close()
    mgconn.close()


def migrate_video():
    """
    :param pgconn:
    :param mgconn:
    :return:
    """
    mgconn = get_mongo_connection()  # IDE Code
    pgconn = get_pg_connection()

    collection = mgconn.get_database("website_pron").get_collection("video_info")
    collection.drop()

    cur = pgconn.cursor()
    cur.execute("SELECT index, tags, basic_info, like_it FROM public.video_basic_info")
    for row in cur.fetchall():
        id = row[0]
        taglist = row[1]
        basic_info = row[2]
        likeit = row[3] > 0
        mongoObject = {
            "_id": id,
            "tags": taglist,
            "like": likeit,
            "name": basic_info["name"],
            "time": basic_info["secs"],
            "size": {
                "width": basic_info["width"],
                "height": basic_info["height"]
            },
            "frame_rate": basic_info["frame_rate"]
        }

        collection.insert_one(
            mongoObject
        )
    cur.close()
    pgconn.close()
    mgconn.close()


def migrate_novels():
    pageSize = 20
    SQLgetsize = "SELECT count(1) FROM public.porn_novel"
    SQLmodel = "SELECT index,title, novel_text, novel_type, words_count FROM public.porn_novel LIMIT %d OFFSET %d"
    mgconn = get_mongo_connection()  # IDE Code
    pgconn = get_pg_connection()

    collection = mgconn.get_database("website_pron").get_collection("novels")
    collection.drop()

    cur = pgconn.cursor()
    cur.execute(SQLgetsize)
    sqlSize = cur.fetchone()[0]
    cur.close()
    cur = pgconn.cursor()

    iterSize = long(math.ceil(sqlSize * 1.0 / pageSize))

    for i in xrange(iterSize):
        cur = pgconn.cursor()
        cur.execute(SQLmodel % (pageSize, i * pageSize))
        for row in cur.fetchall():
            try:
                doc = {
                    "_id": row[0],
                    "title": str(row[1]),
                    "novel_text": row[2],
                    "novel_type": row[3],
                    "words_count": row[4]
                }
                collection.insert_one(doc)
            except Exception as ex:
                print "Error while migration:", ex.message
        cur.close()

    cur.close()
    pgconn.close()
    mgconn.close()


if __name__ == "__main__":
    #print "Migrating images..."
    #migrate_images()
    print "Migrating novels..."
    migrate_novels()
    #print "Migrating videos..."
    #migrate_video()
