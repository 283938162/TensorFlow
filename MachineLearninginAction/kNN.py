import numpy as np  # 科学计算包
import operator  # 运算符模块,k-近邻算法执行排序操作时将使用这个模块提供的函数


# 重构存储过程写业务代码
# 将存储过程中的serserver中的内置函数转换成mysql的函数，还要考虑内置函数与python语法的兼容。


# 创建数据集和标签
# 每组数据有两个特征值
# group矩阵
# 向量labels包含了每个数据点的标签信息 label包含的元素个数等于group矩阵的函数
def createDataSet():
    group = np.array([[1.0, 1.1], [1.0, 1.0], [0, 0], [0, 0.1]])
    labels = ['A', 'A', 'B', 'B']

    print(group, labels)
    return group,labels


group,labels = createDataSet()


def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]  # 矩阵行数
    print('矩阵行数 = ',dataSetSize)

    print(np.tile(inX, (dataSetSize, 1)))  # tile 复制数组

    diffMat = np.tile(inX, (dataSetSize, 1)) - dataSet

    print('diffMat =',diffMat)

    sqDiffMat = diffMat ** 2 # 矩阵平方
    




classify0([0,0],group,labels,3)