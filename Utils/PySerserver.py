import pymssql

'''
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

sql = "select * from ROSAS_HN.dbo.manager_task_detail where TASK_DETAIL_ID = 3510"

cursor.execute(sql)

result = cursor.fetchall()

print(result)
