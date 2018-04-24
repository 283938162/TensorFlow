# -*- coding:utf-8 -*-

import numpy as np
from sklearn.cluster import KMeans

'''
https://blog.csdn.net/linzch3/article/details/76038172?fps=1

'''


def loadData(filePath):
    fr = open(filePath, 'r+', encoding='utf-8')
    lines = fr.readlines()  # 将所有数据 每行作为一个元素 放到一个list列表里面
    # print(lines)

    retData = []
    retCityName = []

    for line in lines:
        cityName = line.strip().split(',')[0]
        data = line.strip().split(',')[1:]
        # print(cityName)
        retCityName.append(cityName)
        # print(data)
        retData.append((data))

    return retCityName, retData


filePath = 'city.txt'
retCityName, retData = loadData(filePath)

print(retCityName)
print(retData)

km = KMeans(n_clusters=4)

# 为啥么每次运行label的值不一样,额，只是顺序不一样而已！！！
label = km.fit_predict(retData)
label2 = km.fit(retData)
label3 = label2.predict(retData)
label = km.fit_predict(np.array(retData))  # 等价于上面的

print(label)
print(label2)
print(label3)
# print(label)
# print(label1)

expense = np.sum(km.cluster_centers_, axis=1)

print("cluster_centers_ :", km.cluster_centers_)
print("expense :", expense)

CityCluster = [[], [], [], []]

for i in range(len(retCityName)):
    CityCluster[label[i]].append(retCityName[i])

# print(CityCluster)

# 输出各个簇的平均消费数和对应城市名称

for i in range(len(CityCluster)):
    print("Expense:%.2f" % expense[i])
    print("cluster_id:%d, citys:%s" % (i, CityCluster[i]))

# 预测结果 (预测的很准确)

# 以北京记录作为测试数据
X = ['2959.19', '730.79', '749.41', '513.34', '467.87', '1141.82', '478.42', '457.64']

res = label2.predict(np.array(X).reshape(1, -1))
print(res)
