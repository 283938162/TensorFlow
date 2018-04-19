from sklearn.datasets import make_blobs
from matplotlib import pyplot

# 画布上所有的样本数
data, target = make_blobs(n_samples = 10, n_features = 2, centers = 3)


print(data)

print(target)
# 在2D图中绘制样本，每个样本颜色不同
pyplot.scatter(data[:, 0], data[:, 1], c = target);
pyplot.show()
