import csv
import pandas as pd

filepath = r'D:\WorkSpace\PycharmProjects\TensorFlow\DBScan\hotpic\test.csv'

"""
    小区名   房价均值
0  一品新筑  15667
1  丁香大楼  16000
2  万兆家园   5057

使用panda打开 能保持csv的原始格式,可以分为三部分
(1) 列名
(2) 索引
(3) 数据

"""

# 使用panda打开 能保持csv的原始格式
data = pd.read_csv(filepath)
print(data)

"""
访问数据
"""
# 按列
print(data['房价均值']) # 返回指定列数据+属性
print(data['房价均值'][0]) # 返回指定cell数据

# panda 怎么返回正行数据?


"""
查看数据
"""
print(data.head(2)) # 返回前两条数据

print(data.tail(2)) #  tail() 参数为空 返回全部 参数为 n 返回倒数n行的所有数据

"""
查看数据的index
"""

print(data.index) # RangeIndex(start=0, stop=3, step=1)
print(data.values) # [['一品新筑' 15667]
                     #['丁香大楼' 16000]
                     #['万兆家园' 5057]]


"""
查看数据概况
"""

print(data.describe())

"""
               房价均值
count      3.000000
mean   12241.333333
std     6224.042604
min     5057.000000
25%    10362.000000
50%    15667.000000
75%    15833.500000
max    16000.000000
"""

# 使用csv包打开,返回的是一个二维列表
# with open(filepath, 'r', encoding='UTF-8') as f:
#     reader = csv.reader(f)
#     print(list(reader))

