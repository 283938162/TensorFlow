from ExcelProject.PyDBPool import PyDBPool

dbpool = PyDBPool('mssql')

num = dbpool.update("update manager_task_detail set cellquestion = '系统未发现影响小区性能的原因。333' WHERE TASK_DETAIL_ID = 1")


print(num)



# print(re)
# print('type1 =',re[0][0])
# print('type2 = ',re[0][1])
#
# if re[0][1] is None:
#     print("None")
# elif re[0][1] == '':
#     print('NULL')
# else:
#     print('other')

# 测试set

# reasonSuggestMerge = [{('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:10']},
#                       {('邻区干扰影响切换', '建议进行负载均衡参数调整'): ['2017-03-26:08']},
#                       {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:05,17,22']},
#                       {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-28:16,17,18']},
#                       {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:11']},
#                       {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-28:12']},
#                       {('互调干扰', '建议处理同频单向邻区'): ['2017-03-26:03,04,05,06,07,08,09,10']}]


reasonSuggestMerge = [{('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:10']},
                      {('邻区干扰影响切换', '建议进行负载均衡参数调整'): ['2017-03-26:08']},
                      {('邻区干扰影响切换1111', '建议进行负载均衡参数调整'): ['2017-03-27:08']},
                      {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:05,17,22']},
                      # {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-28:16,17,18']},
                      {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-26:11']}]
# {('疑似邻区存在隐性故障', '低空大气波导效应、天线挂高过高、发射功率过大等原因导致'): ['2017-03-28:12']}]





# def getMergeDate(reasonSuggestMerge):
#     d = dict()
#     # d = {}  两种声明字典的结果一样
#     for i in reasonSuggestMerge:
#         dateList = []
#         key = list(i.keys())[0]
#         print(key)
#         value = i[key]
#         print(value)
#         datehour = i[key][0].split(':')
#         print('datehour = ', datehour)
#         print('date = ', datehour[0])
#
#         if key not in d:
#             d[key] = i[key]
#             dateList += datehour
#         else:  # 相同的key  value合并  [data1:hour1;date2:hour2...]
#             for i in range(len(d[key])):
#                 if datehour[0] in d[key][i]:
#                     d[key] += datehour[1:]
#                     print('d[key][] :', d[key][0])
#
#             datetime = ','.join(d[key])
#             print('datetime =', datetime)
#
#             a = []
#             a.append(datetime)  # append 没有返回值~~~
#             d[key] = a
#
#     return d
#
# print(getMergeDate(reasonSuggestMerge))

# ['2017-03-26:05,17,22', '2017-03-26:11']

# str = "'2017-03-26:05,17,22'"
#
# print('2017-03-26' in str)

# #  None  NULL
#
# a = ''
# print(a.strip() == '') # True
# print(a.strip() is None)  #False
#
# re = dbpool.select(
#     "select cellquestion,cellproject,cellsuggest,Type_pro from manager_task_detail where TASK_DETAIL_ID = %d" % (4379))
# print(re)


# tablePiCell = dbpool.select("select * from PI_CELL  where (PI55 + PI56) = 0 and pi378 >=0 limit 1;")
# for x in tablePiCell:
#     pi378 = float(x[393])
#     print('pi378:',pi378)
#     print(x[12])
#     print(x[5])

# replace
# cellquestion = '建议处理相关小区故障,建议砍掉！'
#
# print(cellquestion.replace('建议砍掉','建议马上砍掉'))

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
