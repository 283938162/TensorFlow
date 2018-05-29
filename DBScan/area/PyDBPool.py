import pymysql
import pymssql
import time
import re

from DBUtils.PooledDB import PooledDB
from Logger import Logger

"""
当前模块名: PyDBPool (数据库连接池文件)
依赖py文件: Logger.py(日志模块)
更新时间: 2018年5月29日10:08:56  修改批量插入实现 实现python批量插入api
"""

# 声明全局日志对象
logger = Logger()

# 公司测试库
mysqlInfo = {
    "host": '192.168.5.222',
    "user": 'root',
    "passwd": '000000',
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

"""
实例化时需要指定数据库类型,默认是SQLserver数据库
"""


class PyDBPool:
    """
    数据库连接池处理类
    """
    __pool = None

    def __init__(self, dbtype='mssql') -> None:
        self.conn = PyDBPool.getDBConn(self, dbtype.lower())
        self.cursor = self.conn.cursor()

    @staticmethod
    def getDBConn(self, dbtype):
        if dbtype == 'mysql':
            if PyDBPool.__pool is None:
                __pool = PooledDB(creator=pymysql, mincached=1, maxcached=20, host=mysqlInfo['host'],
                                  user=mysqlInfo['user'], passwd=mysqlInfo['passwd'], db=mysqlInfo['dbname'],
                                  port=mysqlInfo['port'], charset=mysqlInfo['charset'])
                logger.info("Create Mysql database connection pool succeed")
                return __pool.connection()
        elif dbtype == 'mssql':
            if PyDBPool.__pool is None:
                __pool = PooledDB(creator=pymssql, mincached=1, maxcached=20, host=sqlServerInfo['host'],
                                  user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                                  database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])
                logger.info("Create SQLserver database connection pool succeed")
                return __pool.connection()
        else:
            logger.info('Please enter the correct database type! MySQL or MSSQL')

    def update(self, sql):
        """
        更新 操作
        :param sql: 操作sql
        :return: 操作成功返回True,操作失败返回False
        """
        logger.info("update_sql = %s" % [sql])
        try:
            self.cursor.execute(sql.replace('None', 'null'))
            self.conn.commit()
            return True
        except Exception as e:
            logger.info(e)
            return False

    def delete(self, sql):
        """
       删除 操作
       :param sql: 操作sql
       :return: 操作成功返回True,操作失败返回False
       """
        logger.info("delete_sql = %s" % [sql])
        try:
            self.cursor.execute(sql.replace('None', 'null'))
            self.conn.commit()
            return True
        except Exception as e:
            logger.info(e)
            return False

    def insert(self, sql):
        """
       插入 操作
       :param sql: 操作sql
       :return: 操作成功返回True,操作失败返回False
       """
        logger.info("insert_sql = %s" % [sql])
        try:
            self.cursor.execute(sql.replace('None', 'null'))
            self.conn.commit()
            return True
        except Exception as e:
            logger.info(e)
            return False

    def insertBatch(self, batchList, tableName):
        """
        批量插入列表数据 列表形式-> [(),(),(),(),(),(),()]
        :param batchList: 嵌套列表
        :param tableName: 插入数据库的表明
        :return: 操作成功返回True,操作失败返回False
        """
        try:
            insertSql = "insert into %s values(%s)" % (tableName, ','.join(['%s' for n in range(len(batchList[0]))]))
            self.cursor.executemany(insertSql, batchList)
            self.conn.commit()
            return True
        except Exception as e:
            logger.info("批量插入过程异常:", e)
            return False

    def timeSelectCal(select):
        def wrapper(*args, **kwargs):
            starttime = time.time()
            result = select(*args, **kwargs)
            endtime = time.time()
            timeInterval = endtime - starttime
            logger.info('timeInterval = %s' % timeInterval)
            return result

        return wrapper

    @timeSelectCal
    def select(self, sql, fetch='all'):
        """
        数据库查询函数\n
        :param sql: 查询sql
        :param fetch: 取数据方式: 'one' 取单条数据; 'all' 取全部数据
        :return: 返回满足条件的数据集
        """
        logger.info("count = %s;sql = %s" % (self.count(sql), [sql]))

        try:
            self.cursor.execute(sql)
            if fetch == 'one':
                return self.cursor.fetchone()
            elif fetch == 'all':
                return self.cursor.fetchall()
        except Exception as e:
            logger.info("exception:%s" % e)

    def count(self, sql):
        """统计满足条件的sql结果集的行数"""
        sqlCount = re.sub(r".*select(.*)from\s+", 'select count(*) from ', sql, flags=re.I)
        self.cursor.execute(sqlCount)
        res = self.cursor.fetchone()
        if res is None:
            return 0
        else:
            return res[0]

    def close(self):
        """连接资源释放"""
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    dbpool = PyDBPool()
    print(dbpool)
    # todo
    dbpool.close()
