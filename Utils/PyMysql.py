import pymysql
import pymssql

import datetime

'''
python object
http://www.runoob.com/python/python-object.html
'''
mysqlInfo = {
    "host": '39.108.231.238',
    "user": 'aliyun',
    "passwd": 'liu@2014',
    "dbname": 'ROSAS',
    "port": 3306,
    "charset": 'utf8'
}

mssqlInfo = {
    "host": '120.25.238.73',
    "user": 'web',
    "passwd": 'pass@word1',
    "dbname": 'ROSAS_HN',
    "charset": 'utf8'
}


def mysqlTest():
    # 对可变参数  最好指定参数名 host = xxx,
    # 打开数据库连接
    conn = pymysql.connect(host=mysqlInfo["host"], user=mysqlInfo["user"], password=mysqlInfo["passwd"],
                           db=mysqlInfo["dbname"],
                           charset=mysqlInfo["charset"])

    print(conn)
    # 获取游标
    # 原理是一次性讲数据加载到内存中
    # cursor = conn.cursor()  # 默认普通游标 fetchall 全部数据放到内存中

    # 它的做法是从储存块中读取记录，并且一条一条返回给你。这里有一个更适合的名字：流式游标。
    ssCursor = conn.cursor(pymysql.cursors.SSCursor)  # 流式游标

    sql = "SELECT * FROM `PROPERTIES_DB` LIMIT 100000;";

    try:
        starttime = datetime.datetime.now()
        print('starttime = ', starttime)
        ssCursor.execute(sql)  # 执行sql语句
        endtime = datetime.datetime.now()
        print('endtime = ', endtime)
        print('endtime - starttime = ', (endtime - starttime).seconds)

        # results = ssCursor.fetchall()  # 获取所有数据

        # for i in results:
        #     print('i = ' ,i)

        while True:
            row = ssCursor.fetchone()
            print('row = ',row)
            break

        # print('results = \n', results)
    except Exception as e:
        print(e)
    finally:
        conn.close()


def mssqlTest():
    conn = pymssql.connect(host=mssqlInfo["host"], user=mssqlInfo["user"], password=mssqlInfo["passwd"],
                           database=mssqlInfo["dbname"],
                           charset=mssqlInfo["charset"])

    print(conn)

    # 获取游标

    # 原理是一次性讲数据加载到内存中
    # cursor = conn.cursor()  # 默认普通游标 fetchall 全部数据放到内存中

    # 它的做法是从储存块中读取记录，并且一条一条返回给你。这里有一个更适合的名字：流式游标。
    # 好像pymssql 没有这个用法
    ssCursor = conn.cursor(pymssql.cursors.SSCursor)  # 流式游标

    sql = "SELECT top 10 TTIME,DEF_CELLNAME, PI55,PI56,PI378 FROM pi_cell WHERE (CONVERT(FLOAT, pi55) + CONVERT(FLOAT, pi56)) = 0 AND CONVERT(FLOAT, pi378) >= 0"

    try:
        starttime = datetime.datetime.now()
        print('starttime = ', starttime)
        ssCursor.execute(sql)  # 执行sql语句
        endtime = datetime.datetime.now()
        print('endtime = ', endtime)
        print('endtime - starttime = ', (endtime - starttime).seconds)

        results = ssCursor.fetchall()  # 获取所有数据


        # print('results = \n', results)
    except Exception as e:
        print(e)
    finally:
        conn.close()


mysqlTest()
