import re
# 导入包，实例化对象
from geopy.geocoders import Nominatim

"""
baidu api 

https://blog.csdn.net/qq_23926575/article/details/72569995

https://blog.csdn.net/lianghq6/article/details/77776649
"""


def getCitynameByGeo(lat_lng):
    # 知道经纬度获取地址
    geolocator = Nominatim()
    location = geolocator.reverse(lat_lng)
    addr = location.address
    print(addr)

    cityname = re.split("[/,]", addr)[-5].strip()
    print(cityname)

    return addr, cityname


# 调用Geopy包进行处理-获取经纬度
def getLocationByGeo(cityname):
    # 知道地址获取经纬度
    geolocator = Nominatim()
    location2 = geolocator.geocode(cityname)
    lat = location2.latitude
    lng = location2.longitude
    return "%s  %s,%s" % (cityname, lat, lng)


# getCitynameByGeo((52.5094982, 13.3765983))

# geolocator = Nominatim()
# location = geolocator.reverse("52.509669, 13.376294")
# print(location)

#%%


from urllib.request import urlopen, quote
import json


def getlnglat(address):
    """根据传入地名参数获取经纬度"""
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'Ti4YbLTnbrA32UvN3QFt20fK79ufDmds'  # 浏览器端密钥
    address = quote(address)
    uri = url + '?' + 'address=' + address + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode()
    temp = json.loads(res)
    lat = temp['result']['location']['lat']
    lng = temp['result']['location']['lng']
    return lat, lng


# lat,lng = getlnglat('上海')
# print(lat)
# print(lng)

"""
上海
31.24916171001514
121.48789948569473
"""


def getcity(lat, lng):
    """根据传入的经纬度获取地名"""
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'Ti4YbLTnbrA32UvN3QFt20fK79ufDmds'  # 浏览器端密钥
    # address = quote(address)
    uri = url + '?' + 'location=' + str(lat) + ',' + str(lng) + '&output=' + output + '&ak=' + ak

    print('uri = ',uri)
    req = urlopen(uri)
    res = req.read().decode()
    temp = json.loads(res)
    location = temp["result"]["formatted_address"]  # 省，市，县
    info = temp["result"]["sematic_description"]  # 详细描述
    return location, info


# location, info = getcity(31.24916171001514,121.48789948569473)
# print(location)
# print(info)
