import numpy as np
from sklearn import metrics
from sklearn.cluster import DBSCAN

from ExcelProject.PyDBPool import PyDBPool

dbpool = PyDBPool()

emp_sample = []

sql = "select empno,sal from emp where sal is not NULL"
result = dbpool.select(sql)

# print(result)

for row in result:
    emp = [];

    empno = row[0]
    sal = row[1]
    emp.append(empno)
    emp.append(int(sal))

    emp_sample.append(emp)

# print("empno = %s,sal=%.2f" % (empno, sal))

# print(emp_sample)
# print(emp_sample[:, 0])

# 对员工工资进行聚类
real_X = np.array(emp_sample)
X = real_X[:, 1:]
print(X)

db = DBSCAN(eps=5000, min_samples=4).fit(emp_sample)

lables = db.labels_
print("labes ：", lables)

noiseRatio = len(lables[lables[:] == -1]) / len(lables)
print("噪音比例：", noiseRatio)

# 计算簇的个数

num_cluster = len(set(lables)) - (1 if -1 in lables else 0)

print("num_cluster = ", num_cluster)
print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, lables))  # 轮廓系数（Silhouette Coefficient）

print("样本总数 = ", len(X))
for n in range(num_cluster):
    print("culster_id = %d, culster_length = %d" % (n, len(X[lables == n].flatten())))
    print("cluster_data = ", X[lables == n].flatten())

# plt.hist(X, 20)
# plt.show()


# 测试数据  预测  (预测结果出现了-1 说明有问题！！！)

rx = np.array([[1101, 10000], [1102, 30000], [1111, 15000]])

print("rx = ", rx)

rxx = rx[:, 1:]
print("rxx = ", rxx)

re = db.predict(rxx)
print("预测结果", )
print(re)

# 释放资源
dbpool.dispose()
