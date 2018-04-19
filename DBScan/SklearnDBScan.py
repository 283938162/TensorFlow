# 在scikit-learn中，DBSCAN算法类为sklearn.cluster.DBSCAN。
# https://blog.csdn.net/haiyang_duan/article/details/77978932

import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.cluster import DBSCAN

'''
make_blobs函数是为聚类产生数据集
产生一个数据集和相应的标签
n_samples:表示数据样本点个数,默认值100
n_features:表示数据的维度，默认值是2
centers:产生数据的中心点，默认值3
cluster_std：数据集的标准差，浮点数或者浮点数序列，默认值1.0
center_box：中心确定之后的数据边界，默认值(-10.0, 10.0)
shuffle ：洗乱，默认值是True
random_state:官网解释是随机生成器的种子
'''

X1, y1 = datasets.make_circles(n_samples = 5000, factor = .6, noise = .05)
X2, y2 = datasets.make_blobs(n_samples = 1000, n_features = 2, centers = [[1.2, 1.2]],
							 cluster_std = [[.1]], random_state = 9)

# 默认是 axis = 0，也就是说对0轴的数组对象进行纵向的拼接（纵向的拼接沿着axis= 1方向）；注：一般axis = 0，就是对该轴向的数组进行操作，操作方向是另外一个轴，即axis=1。
# 对数组进行纵向拼接
# X = np.concatenate((X1, X2))
# print("X[:, 0] = ", X[:, 0])
# print("X[:, 1] = ", X[:, 1])
# print("X = ", X)

# X[:, 0], 取第一列
# X[:, 1]，取第二列


# X[:, 0], X[:, 1]  是长度相同的数组序列
# maker 散点的形状参数
# plt.scatter(X[:, 0], X[:, 1], marker = 'o')
# plt.show()


# 使用DBSCAN效果,我们先不调参，直接用默认参数，看看聚类效果结果数据全部是一类
# y_pred = DBSCAN().fit_predict(X)
# plt.scatter(X[:, 0], X[:, 1], c=y_pred)
# plt.show()


# 没有使用x2,y2
# y_pred = DBSCAN(eps = 0.1, min_samples = 9).fit_predict(X1)
# plt.scatter(X1[:, 0], X1[:, 1], c = y_pred)
# plt.show()

'''
怎么办？看来我们需要对DBSCAN的两个关键的参数eps和min_samples进行调参！
从上图我们可以发现，类别数太少，我们需要增加类别数，那么我们可以减少ϵ-邻域的大小，
默认是0.5，我们减到0.1看看效果。
'''

# scatter 参数  https://blog.csdn.net/qiu931110/article/details/68130199

# def fit_predict(self, X, y=None, sample_weight=None)
print(X1)
y_pred = DBSCAN(eps = 0.1, min_samples = 9).fit_predict(X1)


# print("y_pred = ",y_pred)  预测测试数据对应的簇

plt.scatter(X1[:, 0], X1[:, 1], c = y_pred)
plt.show()
