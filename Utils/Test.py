# # 集合间的赋值
# l = [1,2,3]
# ll = [4,5,6]
#
# print(l)
#
# l = ll
# print(l.clear())
# l.append(1)
# print(l)

# # 拼接
# lll = ['2017-03-26:10', '05,17,22', '11']
# #
# # print(','.join(lll))
#
# content = ','.join(lll)
#
# print(content)
#
# print(list(content))
#
#
# a = []
# a.append(content)
# print(a)

type1List = ['显性故障', '干扰', '容量']


# content = (','.join((map(lambda x: repr(x), ['显性故障', '干扰', '容量']))))
# print(content)


def getListInfo(bbb):
    d = locals()
    pname = list(d.keys())[0]

    print(pname)
    print('%s =  %s' % (pname, bbb))
    print('the length of %s  = %s' % (pname, len(bbb)))


getListInfo(type1List)
