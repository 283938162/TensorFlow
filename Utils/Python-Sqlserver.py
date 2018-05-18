import pymssql

'''dbo
https://www.cnblogs.com/malcolmfeng/p/6909293.html

'''

sqlServerInfo = {
    "host": '120.25.238.73',
    "user": 'web',
    "passwd": 'pass@word1',
    "dbname": 'ROSAS_HN',
    "charset": 'utf8'
}

#

conn = pymssql.connect(host=sqlServerInfo['host'], user=sqlServerInfo['user'], password=sqlServerInfo['passwd'],
                       database=sqlServerInfo['dbname'], charset=sqlServerInfo['charset'])
print(conn)

cursor = conn.cursor()

# sql = "select pd.TYPE3 FROM PROPERTIES_DB as pd where pd.DEF_CELLNAME = '1-20799-1-133' and pd.TTIME in ('2016-02-01','2016-02-02');"
# sql = "select top 10 * from dbo.DBTest"
sql = "insert into DBTest values(%d,'%s',%d)" % (10,'aa', 12)

print('sql = ',sql)
num=cursor.execute(sql)


print(num)
#
# result = cursor.fetchone()
#
# print(result)
#
