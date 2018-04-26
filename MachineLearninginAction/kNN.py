import numpy as np  # 科学计算包
import operator  # 运算符模块,k-近邻算法执行排序操作时将使用这个模块提供的函数

'''
参考：
https://www.aliyun.com/jiaocheng/463312.html

https://blog.csdn.net/qq_27755195/article/details/53213982

'''


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


# 作用：判断某一数据集最近（欧氏距离）的k个点的类别数目，通过多数表决决定输入Inx的类别
# Args：inX : 进行判断的数据，矩阵格式，1行
#       dataSet: 训练集
#       labels:训练集标签
#       k:最近的k个点
# return: 投票数目最多的类别


def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]  # shape 返还行长度，列长度 类似于R的dim
    diffMat = np.tile(inX, (dataSetSize, 1)) - dataSet  # tile 类似 rep操作， 代码 (x0-x1),(y0-y1)
    sqDiffMat = diffMat ** 2  # 开方 (x0-x1)^2,(y0-y1)^2
    sqDistances = sqDiffMat.sum(axis=1)  # 按行求和  (x0-x1)^2+(y0-y1)^2
    distances = sqDistances ** 0.5  # 开根号  sqrt((x0-x1)^2+(y0-y1)^2) # 求欧式距离
    sorteDistIndicies = distances.argsort()  # 类似于order操作 返还排序后的下标
    classCount = {}  # 变量声明 dist格式
    for i in range(k):  # 最近K个点的类别结果
        voteIlabel = labels[sorteDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
    sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)  # 多数表决
    return sortedClassCount[0][0]  # 返还投票最多的类别


# res = classify0([0, 0], group, labels, 3)
#
# print('res = ', res)


def file2matrix(filename):
    fr = open(filename)
    arrayOLines = fr.readlines()
    numberOfLines = len(arrayOLines)
    returnMat = np.zeros((numberOfLines, 3))  # 初始化一个numberOfLines行 3列的矩阵，全部用0填充
    classLabelVector = []
    index = 0  # 行索引
    # 解析文件数据到列表
    for line in arrayOLines:
        line = line.strip()
        listFromLine = line.split('\t')
        returnMat[index, :] = listFromLine[
                              0:3]  # 矩阵的'逗号'与'冒号'的用法  https://blog.csdn.net/Strive_0902/article/details/78225691
        classLabelVector.append(int(listFromLine[-1]))
        index += 1
    return returnMat, classLabelVector


datingDataMat, datingLabels = file2matrix('datingTestSet.txt')

print('datingDataMat: \n', datingDataMat)
print('datingLabels: \n', datingLabels)


# import matplotlib.pyplot as plt
#
# fig =plt.figure()
# ax = fig.add_subplot(111)
# ax.scatter(datingDataMat[:,0],datingDataMat[:,1],15.0*np.array(datingLabels),15.0*np.array(datingLabels))
# plt.show()


# 归一化特征值
def autoNorm(dataSet):
    minVals = dataSet.min(0)  # 找出每一列特征值的最小值 放到minVals 是一个1 * 3 的矩阵
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    normDataSet = np.zeros(np.shape(dataSet))
    m = dataSet.shape[0]
    d = np.tile(minVals, (m, 1))  # 矩阵minval,横向复制m次,纵向复制1次

    print('d :\n', d)

    normDataSet = dataSet - d

    dd = np.tile(ranges, (m, 1))

    print('dd :\n', dd)
    normDataSet = normDataSet / dd
    return normDataSet, ranges, minVals


# normMat, ranges, minVals, maxVals = autoNorm(datingDataMat)
# print('normMat :\n', normMat)
# print('ranges :\n', ranges)
# print('minVals :\n', minVals)
# print('maxVals :\n', maxVals)


def datingClassTest():
    hoRatio = 0.1  # 设置测试集比例
    datingDataMat, datingLabels = file2matrix('datingTestSet.txt')  # 数据集读取
    normMat, ranges, minVals = autoNorm(datingDataMat)  # 标准化数据
    m = normMat.shape[0]
    numTestVecs = int(m * hoRatio)  # 测试集长度
    errorCount = 0.0
    classifierResultAll = []  # 变量声明，list格式
    for i in range(numTestVecs):
        classifierResult = classify0(normMat[i, :], normMat[numTestVecs:m, :], datingLabels[numTestVecs:m], 3)
        classifierResultAll.append(classifierResult)
        print("the classifier came back with :%d, the real answer is : %d" % (classifierResult, datingLabels[i]))
        if (classifierResult != datingLabels[i]):
            errorCount += 1
    print("the total error rate is : %f" % (errorCount / float(numTestVecs)))


datingClassTest()
