import numpy as np
from sklearn.cluster import KMeans

'''
参考：https://blog.csdn.net/sinat_26917383/article/details/70240628
'''

# data = np.random.rand(5,3) #生成一个随机数据 样本大小为5 特征值为3
# # print(data)
#
# '''
# [[0.97895197 0.35583222 0.29280155]
#  [0.05193036 0.51650113 0.01832644]
#  [0.51376281 0.77874941 0.68607259]
#  [0.39123533 0.02091023 0.91121361]
#  [0.25295689 0.29918377 0.47303775]]
# '''
#
# # 构造一个聚类数为3的聚类器
# estimator = KMeans(n_clusters=3)
#
# estimator.fit(data)
#
# # 获取聚类标签
# label_pred =  estimator.labels_
#
# print(label_pred)
#
# # 获取聚类中心点
# centroids = estimator.cluster_centers_
#
# print(centroids)
#
# # estimator.inertia_代表聚类中心均值向量的总和
#
# inertia = estimator.inertia_
# print(inertia)
#
# # 预测测试结果
# test_data = np.random.rand(2,3)
# print(test_data)
# reslut = estimator.predict(test_data)
# print(reslut)


# 案例二

