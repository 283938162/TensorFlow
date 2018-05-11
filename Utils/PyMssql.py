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
sql = "SELECT count(*) as count FROM pi_cell WHERE (CONVERT(FLOAT, pi55) + CONVERT(FLOAT, pi56)) = 0 AND CONVERT(FLOAT, pi378) >= 0"

# cursor.execute(sql)
#
# result = cursor.fetchone()
#
# print(result)



