import numpy as np

import sklearn.cluster as skc
from sklearn import metrics
import matplotlib.pyplot as plt
from DBScan.OnlineCluster import online_times

# 为什么这里的打印没结果?  不是没输出，而是引用OnlineCluster这个文件的输出也全部打印了出来
print("start...")

online_times.append((24, 1234))
# print("online_times = ", online_times)

real_X = np.array(online_times).reshape(-1, 2)

print("real_X = ", real_X)

# X = real_X[:,0:1]  # 取第一列，按列展示
X = real_X[:, 0].reshape(-1, 1)  # 取第一列，按列展示  这两句的作用效果等价

# print("X = ", X)

print("样本总数 = ",len(X))

# 调用DBSCAN的方法进行训练

# DBSCAN是一个类，默认执行其构造方法，参数为传入初始化的参数。
# fit() 训练模型  这是一个类方法，返回一个类对象

db = skc.DBSCAN(eps = 0.1, min_samples = 20).fit(X)
print("db = ", db)

# labels为每个数据的标签簇
labels = db.labels_
print("labels = ", labels)

# 计算噪音的比例（标签标记为-1的占全部标签数的比例）
# noiseRatio = len(labels[labels[:] == -1]) / len(labels)
noiseRatio = len(list(labels[labels[:] == -1])) / len(labels)

print("噪音比例：", noiseRatio)

# 计算簇的个数
num_cluster = len(set(labels)) - (1 if -1 in labels else 0)
print("num_cluster = ", num_cluster)

# 打印各簇标号以及簇内数据
for n in range(num_cluster):
	print("culster_id = %d, culster_length = %d" % (n, len(X[labels == n].flatten())))
	print("cluster_data = ", X[labels == n].flatten())

# 评价聚类效果
print("轮廓系数 = ", metrics.silhouette_score(X, labels))

# 画直方图，分析实验结果

plt.hist(X, 25)
plt.show()
