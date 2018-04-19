# DBSCAN是sciki−kearn提供的密度聚类算法模型，其原型为：
# class sklearn.cluster.DBSCAN(eps=0.5,min_samples=5,metric='euclidean',algorithm='auto',leaf_size=30,p=None,random_state=None)


# 导包
from sklearn import cluster
from sklearn.metrics import adjusted_rand_score
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn import mixture
from sklearn.svm.libsvm import predict
from sklearn.cluster import DBSCAN



# 产生数据
def create_data(centers, num = 100, std = 0.7):
	X, labels_true = make_blobs(n_samples = num, centers = centers, cluster_std = std)
	return X, labels_true


"""
    数据作图
"""


def plot_data(*data):
	X, labels_true = data
	labels = np.unique(labels_true)
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	colors = 'rgbycm'
	for i, label in enumerate(labels):
		position = labels_true == label
		ax.scatter(X[position, 0], X[position, 1], label = "cluster %d" % label),
		color = colors[i % len(colors)]

	ax.legend(loc = "best", framealpha = 0.5)
	ax.set_xlabel("X[0]")
	ax.set_ylabel("Y[1]")
	ax.set_title("data")
	plt.show()


# 测试函数
def test_DBSCAN(*data):
	X, labels_true = data
	clst = cluster.DBSCAN();
	predict_labels = clst.fit_predict(X)
	print("ARI:%s" % adjusted_rand_score(labels_true, predict_labels))
	print("Core sample num:%d" % len(clst.core_sample_indices_))


def test_DBSCAN_epsilon(*data):
	X, labels_true = data
	epsilons = np.logspace(-1, 1.5)
	ARIs = []
	Core_nums = []
	for epsilon in epsilons:
		clst = cluster.DBSCAN(eps = epsilon)
		predicted_labels = clst.fit_predict(X)
		ARIs.append(adjusted_rand_score(labels_true, predicted_labels))
		Core_nums.append(len(clst.core_sample_indices_))

	fig = plt.figure(figsize = (10, 5))
	ax = fig.add_subplot(1, 2, 1)
	ax.plot(epsilons, ARIs, marker = '+')
	ax.set_xscale('log')
	ax.set_xlabel(r"$\epsilon$")
	ax.set_ylim(0, 1)
	ax.set_ylabel('ARI')

	ax = fig.add_subplot(1, 2, 2)
	ax.plot(epsilons, Core_nums, marker = 'o')
	ax.set_xscale('log')
	ax.set_xlabel(r"$\epsilon$")
	ax.set_ylabel('Core_num')

	fig.suptitle("DBSCAN")
	plt.show()


if __name__ == '__main__':
	centers = [[1, 1], [1, 2], [2, 2], [10, 20]]
	X, labels_true = create_data(centers, 1000, 0.5)

	# print("X,labels_true = ",X,labels_true)
	#
	# test_DBSCAN_epsilon(X, labels_true)

