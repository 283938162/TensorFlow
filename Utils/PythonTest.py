from ExcelProject.PyDBPool import PyDBPool

db = PyDBPool()
#
# list_date = ['2017-03-25', '2017-03-26']
# list_hour = [['00,01,03,04,05,06,07,12,15'], ['04,05,06,07']]
#
#
#
#
# sql = "select * from PROPERTIES_DB where TTIME in (%s) limit 2"%(','.join((map(lambda x: repr(x), list_date))))
# sql2 = "select * from PROPERTIES_DB where THOUR in (%s) limit 2"%(','.join((map(lambda x: repr(x), list_hour))))
#
# result = db.select(sql2)
# print(result)

# result = db.select("select INSTR('MySQL INSRT','SQL')")
# print(result)

# list = [('zhansan', 3), ('lisi', 4), ('wangwu', 2), ('zhaoliu', 1), ('guiqi', 5)]
# print(list)
#
# print(sorted(list))

result5 = (('2017-03-26', '7:', 117, '建议处理BBU光模块收发异常告警', 'BBU光模块收发异常告警', 1),
           ('2018-03-26', '2:', 118, '建议处理BBU IR接口异常告警', 'BBU IR接口异常告警', 2),
           ('2017-03-26', '2:', 118, '建议处理BBU IR接口异常告警', 'BBU IR接口异常告警', 1),
           ('2017-03-26', '1:', 119, '建议处理BBU IR光模块收发异常告警', 'BBU IR光模块收发异常告警', 1),
           ('2017-03-26', '1:', 119, '建议处理BBU IR光模块收发异常告警', 'BBU IR光模块收发异常告警', 1),
           ('2017-03-26', 'AllDay', 761, '建议设置参数B2事件的本系统判决门限小于等于-117dbm', 'B2事件的本系统判决门限参数不规范', 0),
           ('2017-03-26', 'AllDay', 761, '建议设置参数B2事件的本系统判决门限小于等于-117dbm', 'B2事件的本系统判决门限参数不规范', 0),
           ('2017-03-26', 'AllDay', 761, '建议设置参数B2事件的本系统判决门限小于等于-117dbm', 'B2事件的本系统判决门限参数不规范', 0),
           ('2017-03-26', 'AllDay', 761, '建议设置参数B2事件的本系统判决门限小于等于-117dbm', 'B2事件的本系统判决门限参数不规范', 0),
           ('2017-03-26', 'AllDay', 761, '建议设置参数B2事件的本系统判决门限小于等于-117dbm', 'B2事件的本系统判决门限参数不规范', 0))

# print(sorted(result5, key=lambda x: x[2]))

a = ('a','b')
print()

