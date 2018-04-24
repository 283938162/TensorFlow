import numpy as np  # 科学计算包
import operator  # 运算符模块,k-近邻算法执行排序操作时将使用这个模块提供的函数


# 创建数据集和标签
def createDataSet():
    group = np.array([[1.0, 1.1], [1.0, 1.0], [0, 0], [0, 0.1]])
    labels = ['A', 'A', 'B', 'B']

    print(group, labels)


createDataSet()
