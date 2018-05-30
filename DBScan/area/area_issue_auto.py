# -*- coding: cp936 -*-
import os, sys, time
import numpy as np
from scipy.spatial.distance import pdist, squareform, euclidean
from sklearn.cluster import DBSCAN
from sklearn import metrics
import matplotlib.pyplot as plt
from PyDBPool import PyDBPool
from Logger import Logger


def cur_file_dir():
    path = os.path.abspath(sys.argv[0])
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        path = os.path.dirname(path)
        return path


sep = os.sep
appPath = cur_file_dir()
indir = appPath + sep + 'data' + sep
outDir = appPath + sep + 'out' + sep
##if not os.path.isdir(outDir):
##    os.makedirs(outDir)
if not os.path.isdir(indir):
    os.makedirs(indir)


def loadfile(s):
    olist = []
    try:
        with open(s, 'r') as fp:
            for line in fp:
                testline = line.replace('\n', '').replace('\r', '')
                olist.append(testline)
    except:
        pass;
    return olist


def calcu_location(location_lon, location_lat, r=1000):
    lat_range = 180 / np.pi * r / 1000 / 6371.137
    lon_range = lat_range / np.cos(location_lat * np.pi / 180)
    max_lat = float('%.9f' % (location_lat + lat_range))
    min_lat = float('%.9f' % (location_lat - lat_range))
    max_lon = float('%.9f' % (location_lon + lon_range))
    min_lon = float('%.9f' % (location_lon - lon_range))
    range_xy = {}
    range_xy['location_lat'] = {'min': min(min_lat, max_lat), 'max': max(min_lat, max_lat)}
    range_xy['location_lon'] = {'min': min(min_lon, max_lon), 'max': max(min_lon, max_lon)}
    return range_xy


def eps_lonlat(x1, y1, r=500):
    range1 = calcu_location(x1, y1, r)
    x_dist = euclidean((y1, x1), (y1, range1['location_lon']['max']))
    y_dist = euclidean((y1, x1), (range1['location_lat']['max'], x1))
    print(x_dist, y_dist)
    return (x_dist + y_dist) / 2.0


def haversine2(lonlat1, lonlat2):
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """
    r = 6371137
    print
    lonlat1, lonlat2
    # 将十进制度数转化为弧度
    lon1, lat1 = lonlat1
    lon2, lat2 = lonlat2
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a)) * r
    return c


# c = haversine2((110.0123, 23.32435), (129.1344, 25.5465))
# print(c)


def loadSample():
    olist = []
    harr = []
    Harrup = []
    try:
        with open(indir + 'cc.txt', 'r') as fp:
            hline = fp.readline().replace('\n', '').replace('\r', '')
            harr = hline.split('\t')
            Harrup = [x.upper() for x in harr]
            if "AREA_ID" not in Harrup:
                Harrup.append("AREA_ID")
                harr.append("area_id")
            idindex = Harrup.index("AREA_ID")
            lonindex = Harrup.index("LON")
            latindex = Harrup.index("LAT")

            hlen = len(harr)
            for line in fp:
                testline = line.replace('\n', '').replace('\r', '')
                tarr = testline.split("\t")
                tarr.extend([""] * (hlen - len(tarr)))
                olist.append(tarr)
    except:
        pass;
    return olist, lonindex, latindex


# dbpool = PyDBPool()
# def get_olist(type1, type2, ttime):
#     olist = dbpool.select(
#         "SELECT DISTINCT cast(NULL AS VARCHAR(200)) AS area_id,p.DEF_CELLNAME,p.def_cellname_chinese,s.LATITUDE AS lat,s.LONGITUDE AS lon,cast(0 AS INT) AS is_area_evaluated FROM PROPERTIES_DB p JOIN SITE_INFO s ON p.DEF_CELLNAME = s.DEF_CELLNAME WHERE p.type1 = '%s' AND p.type2 = '%s' AND p.ttime = '%s' AND ISNUMERIC(s.LATITUDE) = 1 AND ISNUMERIC(s.LONGITUDE) = 1" % (
#             type1, type2, ttime))
#     return [list(i) for i in olist]
#
# type1 = 'MR'
# type2 = '覆盖'
# ttime = '2015-12-04'
# olist = get_olist(type1, type2, ttime)
# # print()
# print(np.array(olist))
# dbpool.close()


def cal_cluster(olist, lonindex, latindex, min_point=6, min_dist=500):
    start1 = time.time()
    print(len(olist))
    narr = np.array(olist)
    X = np.stack([narr[:, lonindex], narr[:, latindex]], axis=-1)
    X = X.astype(np.float64)

    x1 = X[:, 0].mean()  # 所有经度的均值
    y1 = X[:, 1].mean()  # 所有维度的均值

    print(x1, y1)

    eps_fix = eps_lonlat(x1, y1, min_dist)
    print("eps:", eps_fix)

    y_db = DBSCAN(eps=eps_fix, min_samples=min_point).fit(X)
    labels = y_db.labels_

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print('Estimated number of clusters: %d' % n_clusters_)  # estimated  估计的 预计的
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels))  # 轮廓系数（Silhouette Coefficient）

    print("run cost:", time.time() - start1)
    plt.scatter(X[:, 0], X[:, 1], c=labels)
    plt.show()
    return labels


if __name__ == "__main__":
    optarr = sys.argv[:]

    if len(optarr) >= 6:
        X_lable = cal_cluster(optarr[1], optarr[2], optarr[3], optarr[4], optarr[5])
    else:
        olist, lonindex, latindex = loadSample()
        X_lable = cal_cluster(olist, lonindex, latindex, 5, 500)

        if len(X_lable):
            with open("tmpout_%s.txt" % time.strftime("%Y%m%d_%H%M%S", time.localtime()), "w") as fp:
                for item in X_lable:
                    fp.write("%s\n" % item)
