import pymysql
from DBUtils.PooledDB import PooledDB
from sklearn import metrics

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

'''
python object
http://www.runoob.com/python/python-object.html
'''
mysqlInfo = {
	"host": '39.108.231.238',
	"user": 'aliyun',
	"passwd": 'liu@2014',
	"dbname": 'DBTest',
	"port": 3306,
	"charset": 'utf8'
}


class PyDBPool:
	__pool = None

	# 构造函数中的变量全局可用
	def __init__(self) -> None:
		# 构造函数 创建数据库连接，操作游标
		self.conn = PyDBPool.getMysqlConn(self)
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
	def getMysqlConn(self):
		if PyDBPool.__pool is None:
			__pool = PooledDB(creator = pymysql, mincached = 1, maxcached = 20, host = mysqlInfo['host'],
							  user = mysqlInfo['user'], passwd = mysqlInfo['passwd'], db = mysqlInfo['dbname'],
							  port = mysqlInfo['port'], charset = mysqlInfo['charset'])
			print("__pool :", __pool)
			print("数据库连接池创建成功！")
			return __pool.connection()

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
				print("数据更新成功！")
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
