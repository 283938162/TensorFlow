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


# 使用csv包打开,返回的是一个二维列表
# with open(filepath, 'r', encoding='UTF-8') as f:
#     reader = csv.reader(f)
#     print(list(reader))

