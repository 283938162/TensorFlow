# rsDict = {}
#
# rs = 'a'
#
# rsDict[rs] = 'A0'  # 这一句即完成了赋key 也完成了 赋value
#
# print(rsDict)
# print(rsDict[rs])  # 不用使用java中的get  直接dict[key] 就可以直接取值
#
# if rs not in rsDict:
#     print("not in")
# else:
#     print('in')


# tl = ['2016-02-01:19,20,21,22,23', '2016-02-01', '2016-02-02:00,01', '2016-02-02:02,03', '2016-02-02:04,05,06'];

# not in
# if '2016-02-01' in tl:  # 最小粒度是单个元素
#     print('in')
# else:
#     print('not in')

# for x in tl:
#     if '2016-02-01' in x:  # 最小粒度是单个元素
#         print('in')
#     else:
#         print('not in')


# import time
#
# date = time.strftime('%Y-%m-%d', time.localtime())
#
# print(date)
#
# print(date+'.log')


# print(int(3.2)) # 向下取证

# num = 5
# for i in range(0,5):
#     print(i)


# sql = 'select count(*) from emp'
# print('count(*)' or 'count(1)' in sql)
# print('count(*)' in sql or 'count(1)' in sql)


# import sys
#
# print(sys.getsizeof(1))
# print(sys.getsizeof("abc"))

"""
正则 替换
"""

# import re
#
# sql = 'select ID,name from emp where  ...'
# # 正则替换成 sql = 'select count(*) from emp where ...'
#
# sqlCount = re.sub(r'.*select(.*)from\s+', 'select count(*) from', sql)
#
# print('s = ', sqlCount)

# pda = []
#
# pda.append(['a',12])
#
# print(pda)


# 去壳
# listStr = ['40', '试试', '12']
# list = [40, '试试', 12]  # 如果list中有int类型 拼接出错
# print(','.join(listStr))  # 40,试试,12 , 而且这种去壳也不行 单引号去掉了 不能保持原貌
# # print(','.join(list))  # TypeError: sequence item 0: expected str instance, int found
#
# print(type(list))
# print(type(str(list)))
# print((str(list)[1:][:-1]))

#
# file = open('pdc.txt','r+')
# lines = []
# for line in file:
#     lines.append(line.strip('\n')) # Python strip() 方法用于移除字符串头尾指定的字符（默认为空格）。
# print(','.join(lines)) # 字符串连接


# def getMtdHours(fault_datehour):
#     list_hours = []
#     date_hours = fault_datehour.split(';')
#     for y in date_hours:
#         hours = y.split(':')[1]
#         for h in hours.split(","):
#             list_hours.append(int(h))
#     print('list_hours = ', list_hours)






# getMtdHours('2015-12-04:08,09,14;2015-12-05:14,15')

#
# hours = []
# sh = '08,09,14,14,15'
# print(hours)

#
# h = '09,18,19,16,13,15,10,14,20,17,21,11'
#
# a = [int(i) for i in h.split(",")]
# print(a)
#
# b= [8,9,10]
#
# print(list(set(a).intersection(set(b))))


# pdo = []
#
# pdo.append(['a',2])
#
# print(pdo)

tt = [[45,None, 14],[46,None,17]]
# t = if
# print(t)

# for i in tt if len(tt) > 0:



# Rsrp =  -120
# if Rsrp is not None and Rsrp < -110:
#     print('Hello')


# tt = []

ori = 'hi'+':'
a = 2

if  a<3:
    ori+='zhang'

if a > 3:
    ori = ori + "ZHANG"

print(ori)

