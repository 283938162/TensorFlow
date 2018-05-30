import numpy as np
import sklearn.cluster as skc
from sklearn import metrics
import matplotlib.pyplot as plt

filePath = 'D:\WorkSpace\PycharmProjects\TensorFlow\DBScan\学生月上网时间分布-TestData.txt'
mac2id = dict()
online_times = []
f = open(filePath, encoding='utf-8')
for line in f:

    # 读取每条数据中的mac地址，
    # 开始上网时间，上网时长

    mac = line.split(',')[2]
    online_time = int(line.split(',')[6])
    start_time = int(line.split(',')[4].split(' ')[1].split(':')[0])

    # mac2id是一个字典：
    # key是mac地址
    # value是对应mac地址的上网时长以及开始上网时间（精度为小时）

    if mac not in mac2id:
        mac2id[mac] = len(online_times)
        online_times.append((start_time, online_time))
    else:
        online_times[mac2id[mac]] = [(start_time, online_time)]

# print("online_times = ",online_times)
# online_times.append((24,1234))
# -1:根据元素的个数自动计算此轴的长度
# X：上网时间
real_X = np.array(online_times).reshape((-1, 2))

print("real_X = ", real_X)
X = real_X[:, 0:1]

# 调用DBSCAN方法进行训练，
# labels为每个数据的簇标签   (什么是簇标签？)

db = skc.DBSCAN(eps=0.01, min_samples=20).fit(X)  # 0.01h  领域半径 不超过一小时
labels = db.labels_

# 打印数据被记上的标签，
# 计算标签为-1，即噪声数据的比例。

print('Labels:')
print(labels)

raito = len(labels[labels[:] == -1]) / len(labels)
print('Noise raito:', format(raito, '.2%'))

# 计算簇的个数并打印，评价聚类效果

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print('Estimated number of clusters: %d' % n_clusters_)  # estimated  估计的 预计的
print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels))  # 轮廓系数（Silhouette Coefficient）

# 打印各簇标号以及各簇内数据


# print("len(X) =", len(X))
# print("flatten(X) =", X.flatten())
# print("labels =",labels)
#
#
# print("X =", X)
# print("未知 = ",labels == 5)
# print("xxx = ",list(X[labels == 5]))
# print("xxxx = ",list(X[labels == 5].flatten()))


# 从样本数大到小的样本的数 依次输出
# 如何 取出第n个簇的数据呢？


for i in range(n_clusters_):
    print('Cluster ', i, ':')
    print(list(X[labels == i].flatten()))  # list的索引 labels == i 什么鬼

# 画直方图，分析实验结果

plt.hist(X, 24)
plt.show()
