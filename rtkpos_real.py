import sys
sys.path.append('/opt/ros/noetic/lib/python3/dist-packages')

import rosbag
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.ticker as ticker

# 打开bag文件
bag = rosbag.Bag('/home/mars_ugv/docker_ws/20130110/2025-01-17-11-46-58.bag')
velodyne = rosbag.Bag('/home/mars_ugv/docker_ws/data/20130110.bag')

# 创建列表来保存数据
timestamps = []
x = []
y = []
q_x = []
q_y = []
q_z = []
q_w = []

# 解算出的数据保存
print(bag)
print()

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

# 轨迹真值数据保存

# 创建列表来保存数据
timestamps_true = []
x_true = []
y_true = []
z_true = []
rtk_lat_true = []
rtk_long_true = []
rtk_alt_true = []
startflag = 1

print(velodyne)
for topic, msg, t in velodyne.read_messages(topics=['gps_rtk_fix']):
# for topic, msg, t in velodyne.read_messages(topics=['gps_fix']):
    # 假设消息类型为std_msgs/Float64
    if startflag==1:
        startflag=0
        time0_true = t.to_sec()
        lat0 = msg.latitude
        long0 = msg.longitude
        alt = msg.altitude
        # timestamps_true.append(t.to_sec()-time0)
        # x_true.append(0)
        # y_true.append(0)
        
        continue
    timestamps_true.append(t.to_sec())
    lat = msg.latitude
    long = msg.longitude

    # x1, y1, z1 = latlon_to_enu(lat, long, lat0, long0)
    x1, y1=calculate_relative_coordinates(lat0, long0, lat, long)
    x_true.append(y1)
    y_true.append(x1)
    z_true.append(alt)
    rtk_lat_true.append(lat)
    rtk_long_true.append(long)
    rtk_alt_true.append(alt)

startflag = 1
# 读取消息
for topic, msg, t in bag.read_messages(topics=['/Odometry']):
    if startflag==1:
        startflag=0
        time0 = t.to_sec()
    # 假设消息类型为std_msgs/Float64
    timestamps.append(t.to_sec()-time0+time0_true)
    x.append(msg.pose.pose.position.x)
    y.append(msg.pose.pose.position.y)
    q_x.append(msg.pose.pose.orientation.x)
    q_y.append(msg.pose.pose.orientation.y)
    q_z.append(msg.pose.pose.orientation.z)
    q_w.append(msg.pose.pose.orientation.w)

# 关闭bag文件
bag.close()
velodyne.close()

import sys
from scipy.spatial.transform import Rotation as R
import pandas as pd


def main(df_list):
    if len(sys.argv) < 2:
        print("Usage: python script.py <arg1> [arg2] ...")
        return
    for i, arg in enumerate(sys.argv[1:]):
        print(f"Arg {i}: {arg}")
        arg = arg.replace(".pcd", "")
        data = {'timestamp': arg}

        # 局部坐标
        # 示例数据
        # 对低频率数据进行插值，使其时间戳与高频率数据相同
        fx = interp1d(timestamps_true, x_true, kind='linear',bounds_error=False, fill_value='extrapolate')
        fy = interp1d(timestamps_true, y_true, kind='linear',bounds_error=False, fill_value='extrapolate')
        fz = interp1d(timestamps_true, z_true, kind='linear',bounds_error=False, fill_value='extrapolate')
        x_true_interpolated = fx(arg)
        y_true_interpolated = fy(arg)
        z_true_interpolated = fz(arg)
        print(f"time  {arg}: x {x_true_interpolated} y {y_true_interpolated} z {z_true_interpolated}")
        data['x'] = x_true_interpolated
        data['y'] = y_true_interpolated
        data['z'] = z_true_interpolated

        # 四元数
        fqx = interp1d(timestamps, q_x, kind='linear',bounds_error=False, fill_value='extrapolate')
        fqy = interp1d(timestamps, q_y, kind='linear',bounds_error=False, fill_value='extrapolate')
        fqz = interp1d(timestamps, q_z, kind='linear',bounds_error=False, fill_value='extrapolate')
        fqw = interp1d(timestamps, q_w, kind='linear',bounds_error=False, fill_value='extrapolate')
        fqx_interpolated = fqx(arg)
        fqy_interpolated = fqy(arg)
        fqz_interpolated = fqz(arg)
        fqw_interpolated = fqw(arg)
        print(f"time  {arg}: fqx {fqx_interpolated} fqy {fqy_interpolated}")
        print(f"time  {arg}: fqz {fqz_interpolated} fqw {fqw_interpolated}")
        data['fqx'] = fqx_interpolated
        data['fqy'] = fqy_interpolated
        data['fqz'] = fqz_interpolated
        data['fqw'] = fqw_interpolated

        df_list.append(data)

# 定义四元数类
class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def conjugate(self):
        """返回四元数的共轭"""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def multiply(self, other):
        """四元数乘法"""
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)

    def to_rotation_matrix(self):
        """将四元数转换为旋转矩阵"""
        w, x, y, z = self.w, self.x, self.y, self.z
        return np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]
        ])
    

if __name__ == "__main__":
    df_list = []
    main(df_list)

    # 定义四元数
    q_A = Quaternion(df_list[0]['fqw'],df_list[0]['fqx'],df_list[0]['fqy'],df_list[0]['fqz']) 
    q_B = Quaternion(df_list[1]['fqw'],df_list[1]['fqx'],df_list[1]['fqy'],df_list[1]['fqz']) 


    # 定义局部坐标
    p_A = np.array([df_list[0]['x'],df_list[0]['y'],df_list[0]['z']]) 
    p_B = np.array([df_list[1]['x'],df_list[1]['y'],df_list[1]['z']]) 


    # 计算相对位置
    p_B_A = p_B - p_A

    # 计算相对姿态
    q_A_inv = q_A.conjugate()
    q_B_A = q_A_inv.multiply(q_B)

    # 将相对姿态四元数转换为旋转矩阵
    R_B_A = q_B_A.to_rotation_matrix()

    # 组合成4x4的位姿变换矩阵
    T_B_A = np.eye(4)
    T_B_A[:3, :3] = R_B_A
    T_B_A[:3, 3] = p_B_A

    print("time1:",df_list[0]['timestamp'],"  time2:",df_list[1]['timestamp'])
    print("旋转矩阵 R_B_A:")
    print(R_B_A)
    print("平移向量 p_B_A:")
    print(p_B_A)

    print("位姿变换矩阵 T_B_A:")
    print(T_B_A)

    # input("按任意键继续...")



