# coding:utf-8
import psycopg2
from DBUtils.PooledDB import PooledDB

pool = PooledDB(psycopg2,8,database="pvideo",
    user="postgres",
    password="979323",
    host="localhost",
    port="5432")
    
def genSQLConnection():
    return pool.connection()

# queryInfo obsoleted
    
# Old name:executeSQLNewConn
def execSQL(querySQL):
    conn = genSQLConnection()
    curs = conn.cursor()
    curs.execute(querySQL)
    conn.commit()
    curs.close()
    conn.close()
    
# Old name:queryInfoNewConn
def fetchSQL(querySQL):
    conn = genSQLConnection()
    curs = conn.cursor()
    curs.execute(querySQL)
    queryResult = curs.fetchall()
    curs.close()
    conn.close()
    return queryResult
