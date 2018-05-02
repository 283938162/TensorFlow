import pymysql
import pymssql
from DBUtils.PooledDB import PooledDB
from sklearn import metrics

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

'''
python object
http://www.runoob.com/python/python-object.html
'''

# 阿里云 测试数据
# mysqlInfo = {
#     "host": '39.108.231.238',
#     "user": 'aliyun',
#     "passwd": 'liu@2014',
#     "dbname": 'ROSAS',
#     "port": 3306,
#     "charset": 'utf8'
# }

# 公司测试库

mysqlInfo = {
    "host": '120.76.26.161',
    "user": 'cm',
    "passwd": 'cm',
    "dbname": 'ROSAS',
    "port": 3306,
    "charset": 'utf8'
}

sqlServerInfo = {
    "host": '120.25.238.73',
    "user": 'web',
    "passwd": 'pass@word1',
    "dbname": 'ROSAS_HN',
    "charset": 'utf8'
}


class PyDBPool:
    __pool = None

    # 构造函数中的变量全局可用
    # 构造函数重载 传入数据库类型的参数
    def __init__(self, dbclassify) -> None:
        # 构造函数 创建数据库连接，操作游标
        self.conn = PyDBPool.getDBConn(self, dbclassify)
        self.cursor = self.conn.cursor()

    # 数据库连接池连接
    # self 代表类的实例，self 在定义类的方法时是必须有的，虽然在调用时不必传入相应的参数。
    # 每实例化一个对象都会 创建一次 没必须 使用类方法 声明一个静态方法就行

    # def getMysqlConn(self):
    # 	if PyDBPool.__pool is None:
    # 		__pool = PooledDB(creator = pymysql, mincached = 1, maxcached = 20, host = mysqlInfo['host'],
    # 						  user = mysqlInfo['user'], passwd = mysqlInfo['passwd'], db = mysqlInfo['dbname'],
    # 						  port = mysqlInfo['port'], charset = mysqlInfo['charset'])
    # 		print("__pool :", __pool)
    # 		print("数据库连接池创建成功！")
    # 		return __pool.connection()
    #
    #

    @staticmethod  # 通过注解声明一个静态方法，只创建一次 类似java的 static{}
    def getDBConn(self, dbclassify):
        if dbclassify == 'mysql':
            if PyDBPool.__pool is None:
                __pool = PooledDB(creator=pymysql, mincached=1, maxcached=20, host=mysqlInfo['host'],
                                  user=mysqlInfo['user'], passwd=mysqlInfo['passwd'], db=mysqlInfo['dbname'],
                                  port=mysqlInfo['port'], charset=mysqlInfo['charset'])
                print("__pool :", __pool)
                print("mysql数据库连接池创建成功！")
                return __pool.connection()
        elif dbclassify == 'mssql':
            if PyDBPool.__pool is None:
                __pool = PooledDB(creator=pymssql, mincached=1, maxcached=20, host=sqlServerInfo['host'],
                                  user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                                  database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])
                print("__pool :", __pool)
                print("sqlserver数据库连接池创建成功！")
                return __pool.connection()
        else:
            print('请输入正确的数据库类型！mysql 或者 mssql')

    # 连接资源释放
    def dispose(self):
        self.cursor.close()
        self.conn.close()

    # 插入/更新/删除sql
    def update(self, sql):
        print("sql = ", sql)
        try:
            num = self.cursor.execute(sql)
            if sql[0] == 'd':
                print("数据删除成功！")
            elif sql[0] == 'i':
                print("数据插入成功！")
            elif sql[0] == 'u':
                print("更新操作执行成功！")
            self.conn.commit()

            return num
        except Exception as e:
            print(e)

    # 查询
    def select(self, sql):
        print("sql = ", sql)

        self.cursor.execute(sql)

        result = self.cursor.fetchall()

        return result


def sqlserver(param):
    dbpool = PyDBPool('mssql')
    mssqlRes = dbpool.select("select * from ROSAS_HN.dbo.manager_task_detail where TASK_DETAIL_ID = 3510")
    print(mssqlRes)
    dbpool.dispose()
    return mssqlRes


if __name__ == '__main__':
    mssqlRes = sqlserver('mssql')

    # todo
    # 释放资源
