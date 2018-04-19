import numpy as np

# log
# 自然对数  e 为底  numpy的使用 np.e 表示e
online_times = [(22, np.e * np.e - 1), (12, np.e * np.e * np.e - 1)]
real_X = np.array(online_times)
print(real_X)

x = real_X[:,1:]
print(x)


xx = np.log(1+x)
print(xx)
#
# online_times =  [(22, 1558), (12, 40261)]
#
# online_times.append((24,1234))
# print(online_times)


# result = [[22, 1558], [12, 40261], [22, 1721], [23, 351], [16, 23564], [23, 1162], [7, 1162],[8, 1162],[22, 3540], [23, 641]]


# 如何获取指定个数元素？
# print(result)

# lables = [0, -1, 0, 1, -1]
#
# if lables == 0:
# 	print("Hello")

# x = np.array([[1, 2, 3], [4, 5, 6]])
# print(x)
# # print(x.reshape(-1,2))
#
#
# print(x.flatten())
#
#
# y = list([1,2,3,4])
# print(y)

# 定义矩阵
# A1 = np.array([1, 1])
# A11 = np.array([[1, 1]])
#
# # A2 = np.array([2, 0], [0, 2])    # 错误
#
# A2 = np.array(([2, 1], [2, 2]))
#
# B2 = np.array(([[22, 21], [22, 22]]))
# A3 = np.array(([3, 1], [3, 2], [3, 3]))

#  ValueError: all the input arrays must have same number of dimensions

# A = np.concatenate((A11, B2))
#
# print("A11 = ", A11)
# print("B2 = ", B2)
# print("A = ", A)
#
# print("A[:,0]", A[:, 0])
# print("A[:,1]", A[:, 1])

# print("A11 = ", A11)
# print("A2 = ", B2)
# print("A3 = ", A3)


# a = np.array([[1, 2], [3, 4]])
# b = np.array([[5, 6]])
# ab = np.concatenate((a, b), axis=0)
# ba = np.concatenate((a, b.T), axis=1)
# print(a)
# print(b)
#
# print(ab)
# print(ba)
