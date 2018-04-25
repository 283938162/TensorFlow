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
    return group, labels


group, labels = createDataSet()

'''
inX 用于分类的输入向量
dataSet 输入的训练样本集
label 标签向量
k  用于选择最近邻居的数目

'''



def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]  # 矩阵行数
    print('矩阵行数 = ', dataSetSize)

    print(np.tile(inX, (dataSetSize, 1)))  # tile 复制数组

    diffMat = np.tile(inX, (dataSetSize, 1)) - dataSet

    print('diffMat =', diffMat)

    sqDiffMat = diffMat ** 2  # 矩阵平方

    print('sqDiffMat =', sqDiffMat)
    sqDistances = sqDiffMat.sum(axis=1)

    print('sqDistances = ', sqDistances)
    distances = sqDistances ** 0.5 # 开根号
    print('distances = ', sqDistances)

    sortedDistIndicies = distances.argsort()


    classCount =  {}

    for i in range(k):
        votelabel = labels[sortedDistIndicies[i]]
        classCount[votelabel] = classCount.get(votelabel,0) + 1


    # 计算完所有点之间的距离之后,对数据按照从小到大的次序排序  然后确定前k个距离最小的元素所在的主要分类
    # key=operator.itemgetter(1) 按照元组的第二个元素进行排序
    sortedClassCount = sorted(classCount.items(),key=operator.itemgetter(1),reverse=True)

    return sortedClassCount[0][0]




res = classify0([0, 0], group, labels, 3)

print('res = ',res)