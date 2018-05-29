import pymssql

'''dbo
https://www.cnblogs.com/malcolmfeng/p/6909293.html
https://www.jianshu.com/p/80b81a68fd72
'''

sqlServerInfo = {
    "host": '120.25.238.73',
    "user": 'web',
    "passwd": 'pass@word1',
    "dbname": 'ROSAS_HN',
    "charset": 'utf8'

    # "host": '39.108.231.238',
    # "user": 'aliyun',
    # "passwd": 'liu@2014',
    # "dbname": 'DBTest',
    # "port": 3306,
    # "charset": 'utf8'
}

#

conn = pymssql.connect(host=sqlServerInfo['host'], user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                       database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])

conn1 = pymssql.connect(host=sqlServerInfo['host'], user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                        database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])
print(conn)

cursor = conn.cursor()
cursor1 = conn1.cursor()

# sql = "select pd.TYPE3 FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '1-20799-1-133' and pd.TTIME in ('2016-02-01','2016-02-02');"
# sql = "select top 10 * from dbo.DBTest"

#  5	中国  	123  将 1 3 拼接更新到2

# 难道默认是流式鼠标?


cursor.execute(
    "select top 10 convert(nvarchar(255),reason) as reason,convert(nvarchar(255),level_r) as level_r from dbo.import_reason",
    'many')
cursor1.execute(
    "select top 10 convert(nvarchar(255),TYPE3) as TYPE3,convert(nvarchar(255),LEVEL_R) as LEVEL_R from dbo.properties_db",
    'many')

re = cursor.fetchmany(10)
re1 = cursor1.fetchmany(3)

print('re = ', re)
print('re1 = ', re1)

# re1 = cursor.fetchone()
#
# re2 = cursor.fetchone()
#
# re3 = cursor.fetchone()
# print()


# while True:
#     re1 = cursor.fetchmany(2)
#     # print(len(re1))
#     if len(re1) > 0:
#         print(re1)
#     else:
#         break

# i = 1
# result = cursor.fetchone()
# print('result = ',result)
#
# while result:
#     r = cursor.fetchone()
#     print('row ' + str(i), r)
#     i += 1
#
conn.close()
conn1.close()
#
