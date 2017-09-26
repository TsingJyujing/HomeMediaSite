import pymongo

def generate_mongodb_connection():
    return pymongo.MongoClient("localhost", 27017)


class MongoDBConnection:
    def __init__(self):
        pass

    def __enter__(self):
        self.conn = generate_mongodb_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class MongoDBDatabase:
    def __init__(self, db_name):
        assert db_name is not None
        self.db_name = db_name

    def __enter__(self):
        self.conn = generate_mongodb_connection()
        return self.conn.get_database(self.db_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

class MongoDBCollection:
    def __init__(self, db_name, coll_name):
        assert db_name is not None
        assert coll_name is not None
        self.db_name = db_name
        self.coll_name = coll_name

    def __enter__(self):
        self.conn = generate_mongodb_connection()
        return self.conn.get_database(self.db_name).get_collection(self.coll_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()