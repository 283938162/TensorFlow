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

# -1:根据元素的个数自动计算此轴的长度
# X：上网时间
real_X = np.array(online_times).reshape((-1, 2))

print("real_X[:, 1:] =", real_X[:, 1:])  # real_X[:, 1:] 取出第二列数 按列展示

# X = real_X[:, 1:]
X = np.log(1 + real_X[:, 1:])  # 求arr以e为底的 展示更加合理

print('X =', X)

# 调用DBSCAN方法进行训练 ，
# labels为每个数据的簇标签

db = skc.DBSCAN(eps=0.6, min_samples=9).fit(X)  #
labels = db.labels_

print('Lables:')
print(labels)
raito = len(labels[labels[:] == -1]) / len(labels)
print('Noise raito:', format(raito, '.2%'))

# Number of cluster in lables, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
print('Silhouette Coefficient: %0.3f' % metrics.silhouette_score(X, labels))

# 统计每一个簇内的样本个数， 均值，标准差

for i in range(n_clusters_):
    print('Cluster ', i, ':')
    count = len(X[labels == i])
    mean = np.mean(real_X[labels == i][:, 1])
    std = np.std(real_X[labels == i][:, 1])
    print('\t number of sample: ', count)
    print('\t mean of sample  : ', format(mean, '.1f'))
    print('\t std of sample   : ', format(std, '.1f'))

plt.hist(X, 12)
plt.show()
