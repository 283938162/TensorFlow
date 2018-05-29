import pymysql
import pymssql
import time
import sys
import re

from DBUtils.PooledDB import PooledDB

'''
python object
http://www.runoob.com/python/python-object.html
'''

# 阿里云 测试数据
mysqlInfo = {
    "host": '39.108.231.238',
    "user": 'aliyun',
    "passwd": 'liu@2014',
    "dbname": 'DBTest',
    "port": 3306,
    "charset": 'utf8'
}

# 公司测试库
# mysqlInfo = {
#     "host": '192.168.5.222',
#     "user": 'root',
#     "passwd": '000000',
#     "dbname": 'ROSAS',
#     "port": 3306,
#     "charset": 'utf8'
# }


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
    def __init__(self, dbclassify='mysql') -> None:
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
                __pool = PooledDB(creator=pymysql, mincached=1, maxcached=10, host=mysqlInfo['host'],
                                  user=mysqlInfo['user'], passwd=mysqlInfo['passwd'], db=mysqlInfo['dbname'],
                                  port=mysqlInfo['port'], charset=mysqlInfo['charset'])
                print("mysql数据库连接池创建成功！")
                return __pool.connection()
        elif dbclassify == 'mssql':
            if PyDBPool.__pool is None:
                __pool = PooledDB(creator=pymssql, mincached=1, maxcached=20, host=sqlServerInfo['host'],
                                  user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                                  database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])
                print("SqlServer数据库连接池创建成功！")
                return __pool.connection()
        else:
            print('请输入正确的数据库类型！mysql 或者 mssql')

    # 连接资源释放
    def close(self):
        self.cursor.close()
        self.conn.close()

    # 统计表记录数
    def count(self, sql):
        sqlCount = re.sub(r".*select(.*)from\s+", 'select count(*) from ', sql)
        count = self.select(sqlCount)[0][0]

        print('count = ', count)
        return count

    # 插入/更新/删除sql
    def update(self, sql):
        """
        插入/更新/删除 操作统一通过update函数来实现,
        :param sql: 操作sql
        :return: 操作成功返回True,操作失败返回False
        """
        print("sql = ", [sql])
        try:
            self.cursor.execute(sql.replace('None', 'null'))
            if sql[0] == 'd':
                print("数据删除成功！")
            elif sql[0] == 'i':
                print("数据插入成功！")
            elif sql[0] == 'u':
                print("更新操作执行成功！")
            self.conn.commit()

            return True
        except Exception as e:
            print(e)
            return False

    # 批量插入[[],[],[],[]...]
    def insertBatch(self, batchList, tableName):
        """
        批量插入列表数据 列表形式-> [[],[],[],[]...]
        :param batchList: 嵌套列表
        :param tableName: 插入数据库的表明
        :return: 操作成功返回True,操作失败返回False
        """
        try:
            for row in batchList:
                insertSql = "insert into %s values(%s)" % (tableName, str(row)[1:][:-1])
                self.update(insertSql.replace('None', 'null'))
            return True
        except Exception as e:
            print("批量插入过程异常:", e)
            return False

    def timeCal(select):
        def wrapper(*args, **kwargs):
            starttime = time.time()
            result = select(*args, **kwargs)
            endtime = time.time()
            timeInterval = endtime - starttime
            print('timeInterval: ', timeInterval)
            return result

        return wrapper

    # 查询(1) 查询记录数 (2) sql Noe查询返回满足条件的所有记录  (3) 查询返回满足条件的所有记录
    # fetch 三种方式 count  one  all
    # 默认返回单条记录
    # 每select many 一次 创建一个流式游标 https://www.cnblogs.com/baiyangcao/p/pymssql_basic.html
    @timeCal  # 先临时查询所有
    def select(self, sql, fetch='all'):
        print('select_sql = ', [sql])

        if fetch == 'one':
            self.cursor.execute(sql)
            return self.cursor.fetchone()

        elif fetch == "many":  # 对表切片时 返回流式游标
            self.cursor.execute(sql)
            return self.cursor

        elif fetch == 'all':
            self.cursor.execute(sql)
            return self.cursor.fetchall()

    #
    # def sqlserver(param):
    #     dbpool = PyDBPool('mssql')
    #     mssqlRes = dbpool.select("select * from ROSAS_HN.dbo.manager_task_detail where TASK_DETAIL_ID = 3510")
    #     print(mssqlRes)
    #     dbpool.dispose()
    #     return mssqlRes

    # step  切片大小
    # sql 查询数据的sql
    def tableSlice(self, sql, step=2):
        """
        :param tableName: 查询表表名
        :param sql: 查询数据库sql
        :param step: 切片大小(每次查询取多少人条),默认取1000条
        :return: loopNums 循环次数  cursor流动游标
        """
        sqlCount = re.sub(r".*select(.*)from\s+", 'select count(*) from ', sql)
        count = self.select(sqlCount)
        loopNums = int((count / step) + 1)
        self.cursor.execute(sql)
        return loopNums, self.cursor


if __name__ == '__main__':
    dbpool = PyDBPool('mssql')
    print(dbpool)

    # dbpool1 = PyDBPool('mssql')
    # print(dbpool1)
    #
    # if dbpool.update("insert into nfj"):
    #     print("操作成功!")

    """
    批量插入
    """
    # None 不能入库  数据库对应的是NULL
    # batchList = [[433, '试试', 12], [444, '事宜', 13], [455, None, 14]]
    # batchList = [[45, None, 14], [46, None, 17]]
    # dbpool.insertBatch(batchList, 'tt')

    # sql = "select ID,DEF_C        ELLNAME from PROPERTIES_DB limit 1000"
    # t1 = time.time()
    # print(dbpool.select(sql, 'one'))
    # t2 = time.time()
    # print('t2 - t1 = ', (t2 - t1))

    # dbpool.select()  使用装饰器测试
    # print(dbpool.select(sql, 'one'))  # timeInterval:  0.03125286102294922

    """
        切片1
    """
    # step = 1000
    # loopNums, cursor = dbpool.tableSlice(sql, step)
    #
    # for i in range(0, loopNums):
    #     stepList = []
    #     for x in range(0, step):
    #         stepList.append(cursor.fetchone())
    #     print("list: " + str(i) + ": ", stepList)

    # time.sleep(1)
    # stepList  todo

    """
    切片2
    """
    # sql = "select top 100000 * from dbo.manager_task_detail"
    # cursor = dbpool.select("select top 100000 TYPE3,LEVEL_R from dbo.properties_db", 'many')
    # while True:
    #     re = cursor.fetchmany(10000)
    #     if len(re) > 0:
    #         print(len(re))
    #         print(re)
    #         # re todo
    #     else:
    #         break

    """
       多表关联未切片测试  1000 条  过滤出6条
    """

    # tableIR = dbpool.select("select top 1000 reason,level_r from dbo.import_reason")
    # tablePD = dbpool.select("select top 1000 TYPE3,LEVEL_R from dbo.properties_db")
    #
    # irList = []
    # for ir in tableIR:
    #     irReason = ir[0]
    #     irLevelR = ir[1]
    #
    #     for pd in tablePD:
    #         pdType3 = pd[0]
    #         pdLevelR = pd[1]
    #
    #         if (irReason == pdType3) and (irLevelR == pdLevelR):
    #             irList.append(ir)
    #
    # print(len(irList))

    # result = dbpool.select("select top 10 ir.reason,pd.TYPE3 ,ir.level_r ,pd.LEVEL_R from dbo.import_reason as ir inner join properties_db as pd on ir.reason = pd.TYPE3 and ir.level_r = pd.LEVEL_R")
    # print(result)

    """
    单表切片 测试
    """
    # tableIRCursor = dbpool.select(
    #     "select top 10 convert(nvarchar(255),reason) as reason,convert(nvarchar(255),level_r) as level_r from dbo.import_reason",
    #     'many')
    #
    # while True:
    #     tableIR = tableIRCursor.fetchmany(2)
    #     if len(tableIR) > 0:
    #         print('tableIR = ', tableIR)
    #     else:
    #         break

    """
    多表关联切片测试
    
    流动游标只能有一个!!! 第二个会覆盖第一个的结果!!!
    一个连接一次只能有一个游标的查询处于活跃状态 ,一个连接即使创建多个游标对象也是无效的!
    
    https://www.cnblogs.com/baiyangcao/p/pymssql_basic.html
    
    cursor就是一个Cursor对象，这个cursor是一个实现了迭代器（def__iter__()）和生成器（yield）的MySQLdb对象，
    这个时候cursor中还没有数据，只有等到fetchone()或fetchall()的时候才返回一个元组tuple，才支持len()和index()操作，
    这也是它是迭代器的原因。但同时为什么说它是生成器呢？因为cursor只能用一次，即每用完一次之后记录其位置，
    等到下次再取的时候是从游标处再取而不是从头再来，而且fetch完所有的数据之后，这个cursor将不再有使用价值了，
    即不再能fetch到数据了。
    
    
    python读取几千万行的大表内存问题
    https://blog.csdn.net/luckyzhou_/article/details/69061621
    
    
    """
    # tableIRCursor = dbpool.select(
    #     "select top 10 convert(nvarchar(255),reason) as reason,convert(nvarchar(255),level_r) as level_r from dbo.import_reason",
    #     'many')
    # tablePDCursor = dbpool1.select(
    #     "select top 10 convert(nvarchar(255),TYPE3) as TYPE3,convert(nvarchar(255),LEVEL_R) as LEVEL_R from dbo.properties_db",
    #     'all')
    #
    # print('tableIRCursor', tableIRCursor)
    # print('tablePDCursor', tablePDCursor)
    #
    # print(tableIRCursor == tablePDCursor)
    #
    # print('tableIR = ', tableIRCursor.fetchmany(5))
    # print('tableIR = ', tableIRCursor.fetchmany(2))
    # print('tablePD = ', tablePDCursor.fetchmany(2))
    # print('tablePD = ', tablePDCursor.fetchmany(1))

    #     irList = []
    #
    #     indexinner = 1
    #     indexouter = 1
    #
    #     while True:
    #         tableIR = tableIRCursor.fetchmany(2)
    #         if len(tableIR) > 0:
    #             print('外层IR = ', tableIR)
    #             for ir in tableIR:
    #                 irReason = ir[0]
    #                 irLevelR = ir[1]
    #                 print('----indexouter = ', indexouter)
    #
    #                 while True:
    #                 # 内层循环完成一次  游标归零 没有类似api   cursor 完成一次遍历 就被废弃了
    #                     scroll(0,'absolute')
    #
    #                 # !!!
    #                     tablePD = tablePDCursor.fetchall()
    #                     if len(tablePD) > 0:
    #                         # print('内层pd = ', tablePDCursor)
    #                         for pd in tablePD:
    #                             print('indexinner = ', indexinner)
    #                             pdType3 = pd[0]
    #                             pdLevelR = pd[1]
    #
    #                             if (irReason == pdType3) and (irLevelR == pdLevelR):
    #                                 print('----------------------flag')
    #                                 irList.append(ir)
    #                             indexinner += 1
    #                     else:
    #                         break
    #
    #             indexouter += 1
    #         else:
    #             break
    #
    # print(len(irList))

    # print(dbpool.select("select top 10 TYPE3,LEVEL_R from dbo.properties_db"))

    # irCursor = dbpool.select("select top 100 * from dbo.import_reason",'many')

    # while True:
    #     re = dbpool.select("select top 10000 * from dbo.manager_task_detail", 'many').fetchmany(100)
    #     if len(re) > 0:
    #         print(re)
    #         # re todo
    #     else:
    #         break

    # while True:
    #     print(re)

    # insertSql = "insert into tt(name,age) values ('zansa',12)"
    # updateSql = "update tt set name  = 'lisi' where id = 33"
    # deleteSql = "delete from tt where id = 31"
    #
    # updateMtdSql = "update manager_task_detail set cellquestion = '系统未发现影响小区性能的原因。',cellproject = '需继续观察指标，或优化建议方案：需继续观察指标，或现场测试及对基站硬件进行排查。',Type_pro='None' where TASK_DETAIL_ID = 1"
    #
    # num = dbpool.update(updateSql)
    # print('受影响条数 num = ', num)

    # todo
    # 释放资源
    dbpool.close()
# dbpool1.close()
