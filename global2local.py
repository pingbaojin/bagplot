import math

# 地球半径（米）
R = 6371000

# 经纬度误差转化为x,y误差
def haversine(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度坐标点之间的距离。
    :param lat1: 第一个点的纬度 (十进制度数)
    :param lon1: 第一个点的经度 (十进制度数)
    :param lat2: 第二个点的纬度 (十进制度数)
    :param lon2: 第二个点的经度 (十进制度数)
    :return: 两点之间的距离（公里）
    """
    # 将十进制度数转化为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    计算从点1到点2的初始方位角。
    :param lat1: 第一个点的纬度 (十进制度数)
    :param lon1: 第一个点的经度 (十进制度数)
    :param lat2: 第二个点的纬度 (十进制度数)
    :param lon2: 第二个点的经度 (十进制度数)
    :return: 从点1到点2的初始方位角（度）
    """
    # 将十进制度数转换为弧度
    lat1, lat2 = map(math.radians, [lat1, lat2])
    delta_lon = math.radians(lon2 - lon1)
    # 使用公式计算方位角
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    initial_bearing = math.atan2(y, x)
    # 将弧度转换为度，并调整范围至0-360度
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def calculate_relative_coordinates(lat1, lon1, lat2, lon2):
    """
    计算目标点相对于初始点的相对坐标 (dx, dy)。
    :param lat1: 初始点的纬度 (十进制度数)
    :param lon1: 初始点的经度 (十进制度数)
    :param lat2: 目标点的纬度 (十进制度数)
    :param lon2: 目标点的经度 (十进制度数)
    :return: 目标点相对于初始点的相对坐标 (dx, dy)（公里）
    """
    distance = haversine(lat1, lon1, lat2, lon2)
    bearing = calculate_bearing(lat1, lon1, lat2, lon2)
    
    # 将方位角转换为弧度
    bearing_rad = math.radians(bearing)
    
    # 计算相对坐标
    dx = distance * math.cos(bearing_rad)
    dy = distance * math.sin(bearing_rad)
    
    return dx, dy
