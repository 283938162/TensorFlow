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


import time

date = time.strftime('%Y-%m-%d', time.localtime())

print(date)

print(date+'.log')
