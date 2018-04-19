import numpy as np
import matplotlib.pyplot as plt

'''
绘图
'''

# 产生测试数据

x = np.arange(1, 10)
y = x

fig = plt.figure()

# 添加子图   fig.add_subplot(xyz) 画布上分成 x*y 快 z 表示第z快画布
# xyz=111 默认铺满整个画布

ax1 = fig.add_subplot()

# 设置标题
ax1.set_title('Scatter Plot')

# 设置X轴标签
plt.xlabel('X')

# 设置Y轴标签
plt.ylabel('Y')

# 画散点图  marker  散点的形状  长江 o x
ax1.scatter(x, y, c = 'r', marker = 'o')

# 设置图标
plt.legend('Z')
# 显示所画的图
plt.show()
