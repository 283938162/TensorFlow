from math import *
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import numpy as np


def get_distance(array_1, array_2):
    lon_a = array_1[0]
    lat_a = array_1[1]
    lon_b = array_2[0]
    lat_b = array_2[1]
    radlat1 = radians(lat_a)
    radlat2 = radians(lat_b)
    a = radlat1 - radlat2
    b = radians(lon_a) - radians(lon_b)
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radlat1) * cos(radlat2)*pow(sin(b/2),2)))
    earth_radius = 6378137
    s = s * earth_radius
    return s


def create_coordinate_list():
    result = []
    # 第1个聚类簇，3个点在500米范围内
    point_11 = [116.501146, 39.9915]
    point_12 = [116.501452,39.991002]
    point_13 = [116.501685,39.990491]

    # 第2个聚类簇，2个点在500米范围内
    point_21 = [116.528509,39.995549]
    point_22 = [116.530808,39.99389]

    # 噪音点
    point_31 = [116.419131,40.024949]

    # 第3个聚类簇，2个点在500米范围内
    point_41 = [116.51913,39.972384]
    point_42 = [116.520747,39.972025]

    # 噪音点
    point_51 = [116.53075,39.883273]

    result.append(point_11)
    result.append(point_12)


    result.append(point_21)
    result.append(point_22)

    result.append(point_31)

    result.append(point_41)
    result.append(point_42)

    # 此处加入第1个聚类簇的第3个点
    result.append(point_13)

    result.append(point_51)

    return result


def main():
    # 模拟坐标数据
    coordinate_list = create_coordinate_list()
    X = np.array(coordinate_list)

    # DBSCAN聚类
    dbscan = DBSCAN(eps=500, min_samples=2, metric=get_distance).fit(X)
    labels = dbscan.labels_

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print('n_clusters = ',n_clusters)

    plt.scatter(X[:,0],X[:,1],c=dbscan.labels_)
    plt.show()

    # 输出[ 0  0  1  1 -1  2  2  0 -1]
    print(dbscan.labels_)


if __name__ == '__main__':
    main()