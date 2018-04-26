from ExcelProject.PyDBPool import PyDBPool

dbpool = PyDBPool('mysql')
tablePiCell = dbpool.select("select * from PI_CELL  where (PI55 + PI56) = 0 and pi378 >=0 limit 1;")
for x in tablePiCell:
    pi378 = float(x[393])
    print('pi378:',pi378)
    print(x[12])
    print(x[5])
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

# a = ('a','b')
# print()


# a = 'zz'
# b = 'zz'
#
# print(a == b)

#
# dd = {'a': 'A', 'c': 'C'}
# print(dd)
#
#
# l = list(dd.keys())
# print(l)


# 修改元组
#
# a = (('a','b'),('c','d'))
# print(a)
# for i in a:
#     item = list(i)
#     print(item)
#     item[0] = 'A'
#
# print(a)


#  沿axis = 1方向复制
# import numpy as np
#
# y = np.array([1, 2, 3]).reshape(-1, 1)
# x = np.array([1, 2, 3])
# print('x= \n',x)
#
#
# print('np.tile(x, 2) = \n',np.tile(x, 2))
# print('np.tile(x, (2,1)) = \n',np.tile(x, (2,1))) # 复制2行1列  也就是说此时列不变，行复制
# print('np.tile(x, (2,2)) = \n',np.tile(x, (2,2))) # 复制2行2列
# # print(np.tile(y, 4))
# # print(np.tile(y, 4) * 2)
# # print(np.tile(y, 4) ** 2)
# # print(np.tile(y, 4) ** 3)
#
#
# kn = 'SFXN'
# if kn in ('SFXN','SFLH'):
#     print("存在")
# else:
#     print('不存在')