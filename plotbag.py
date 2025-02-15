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

# 解算出的数据保存
print(bag)
print()
startflag = 1
# 读取消息
for topic, msg, t in bag.read_messages(topics=['/Odometry']):
    if startflag==1:
        startflag=0
        time0 = t.to_sec()
    # 假设消息类型为std_msgs/Float64
    timestamps.append(t.to_sec()-time0)
    x.append(msg.pose.pose.position.x)
    y.append(msg.pose.pose.position.y)

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
rtk_lat_true = []
rtk_long_true = []
startflag = 1

print(velodyne)
for topic, msg, t in velodyne.read_messages(topics=['gps_rtk_fix']):
# for topic, msg, t in velodyne.read_messages(topics=['gps_fix']):
    # 假设消息类型为std_msgs/Float64
    if startflag==1:
        startflag=0
        time0 = t.to_sec()
        lat0 = msg.latitude
        long0 = msg.longitude
        # timestamps_true.append(t.to_sec()-time0)
        # x_true.append(0)
        # y_true.append(0)
        
        continue
    timestamps_true.append(t.to_sec()-time0)
    lat = msg.latitude
    long = msg.longitude

    # x1, y1, z1 = latlon_to_enu(lat, long, lat0, long0)
    x1, y1=calculate_relative_coordinates(lat0, long0, lat, long)
    x_true.append(y1)
    y_true.append(x1)
    rtk_lat_true.append(lat)
    rtk_long_true.append(long)
    # x_true.append(long)
    # y_true.append(lat)


# 关闭bag文件
bag.close()
velodyne.close()


# 创建一个图形 经纬度对比（分开）
fig1 = plt.figure()

# 添加子图
fig1_ax1 = fig1.add_subplot(221)
fig1_ax2 = fig1.add_subplot(222)
fig1_ax3 = fig1.add_subplot(223)
fig1_ax4 = fig1.add_subplot(224)

# 在每个子图上绘制不同的内容
fig1_ax1.plot(timestamps, x, label='long_mea')
fig1_ax2.plot(timestamps, y, label='lat_mea')
fig1_ax3.plot(timestamps_true, x_true, label='long_true')
fig1_ax4.plot(timestamps_true, y_true, label='lat_true')

fig1_ax1.set_title('Figure 1: Longitude Estimated')
fig1_ax1.set_xlabel('Time/s')
fig1_ax1.set_xlabel('dis/m')
fig1_ax1.legend()
fig1_ax2.set_title('Figure 1: Latitude Estimated')
fig1_ax2.set_xlabel('Time/s')
fig1_ax2.set_xlabel('dis/m')
fig1_ax2.legend()
fig1_ax3.set_title('Figure 1: Longitude Real Value')
fig1_ax3.set_xlabel('Time/s')
fig1_ax3.set_xlabel('dis/m')
fig1_ax3.legend()
fig1_ax4.set_title('Figure 1: Latitude Real Value')
fig1_ax4.set_xlabel('Time/s')
fig1_ax4.set_xlabel('dis/m')
fig1_ax4.legend()

fig2 = plt.figure()

# 创建一个图形 经纬度对比（同一张图）
fig2_ax1 = fig2.add_subplot(121)
fig2_ax2 = fig2.add_subplot(122)


# 在每个子图上绘制不同的内容
fig2_ax1.plot(timestamps, x, linestyle='-',  color='blue', label='long_mea')
fig2_ax2.plot(timestamps, y, linestyle='-',  color='blue', label='lat_mea')
fig2_ax1.plot(timestamps_true, x_true, linestyle='--', color='red', label='long_true')
fig2_ax2.plot(timestamps_true, y_true, linestyle='--', color='red', label='lat_true')


fig2_ax1.set_title('Longitude Comparison')
fig2_ax1.set_xlabel('Time/s')
fig2_ax1.set_ylabel('distance/m')
fig2_ax1.legend()
fig2_ax2.set_title('Latitude Comparison')
fig2_ax2.set_xlabel('Time/s')
fig2_ax2.set_ylabel('distance/m')
fig2_ax2.legend()
fig2.subplots_adjust(wspace=0.4)
fig2.savefig('figure/Figure 2: Lat-Long Comp.png', dpi=300, bbox_inches='tight')

# 示例数据
# 对低频率数据进行插值，使其时间戳与高频率数据相同
fx = interp1d(timestamps_true, x_true, kind='linear',bounds_error=False, fill_value='extrapolate')
fy = interp1d(timestamps_true, y_true, kind='linear',bounds_error=False, fill_value='extrapolate')
x_true_interpolated = fx(timestamps)
y_true_interpolated = fy(timestamps)


# 计算绝对误差
absolute_error_x = np.abs(x - x_true_interpolated)
absolute_error_y = np.abs(y - y_true_interpolated)

# 误差曲线
fig3 = plt.figure()
# 添加子图
fig3_ax1 = fig3.add_subplot(121)
fig3_ax2 = fig3.add_subplot(122)
# fig3_ax1.plot(timestamps, absolute_error_x, linestyle='--', marker='o', color='red',label='long')
# fig3_ax2.plot(timestamps, absolute_error_y, linestyle='--', marker='o', color='red',label='lat')
fig3_ax1.plot(timestamps, absolute_error_x, linestyle='--',  color='red',label='long')
fig3_ax2.plot(timestamps, absolute_error_y, linestyle='--',  color='red',label='lat')
fig3_ax1.set_xlabel('Time/s')
fig3_ax1.set_ylabel('distance/m')
fig3_ax2.set_xlabel('Time/s')
fig3_ax2.set_ylabel('distance/m')
fig3_ax1.set_title('Longitude Error')
fig3_ax2.set_title('Latitude Error')
fig3_ax1.legend()  # 显示图例
fig3_ax2.legend()  # 显示图例
fig3.subplots_adjust(wspace=0.4)
fig3.savefig('figure/Figure 3: Lat-Long Err.png', dpi=300, bbox_inches='tight')


fig4 = plt.figure()


# 添加子图
fig4_ax1 = fig4.add_subplot(111)
# # 禁用科学计数法
# fig4_ax1.ticklabel_format(style='plain', axis='both')

# fig3_ax1.plot(timestamps, absolute_error_x, linestyle='--', marker='o', color='red',label='long')
# fig3_ax2.plot(timestamps, absolute_error_y, linestyle='--', marker='o', color='red',label='lat')
fig4_ax1.plot(rtk_long_true, rtk_lat_true, color='blue',  linestyle='--',label='RTK Ground Truth')
fig4_ax1.set_xlabel('long/°')
fig4_ax1.set_ylabel('lat/°')
fig4_ax1.set_title('RTK Ground Truth')

# 设置坐标轴格式化为实际数值
fig4_ax1.ticklabel_format(axis='y', style='plain', useOffset=False)

fig4_ax1.legend()  # 显示图例
# 保存图像并设置分辨率为 300 DPI
fig4.savefig('figure/Figure 4: RTK position.png', dpi=300, bbox_inches='tight')
plt.show()


# 打开文件
with open("output.txt", "w") as file:
    # 使用print函数将输出重定向到文件
    # 统计指标
    # 1min = 60s
    index = next((i for i, number in enumerate(timestamps) if number > 60), None)
    print(index,timestamps[index])
    print(f'Maximum Absolute Error 60s: {np.max(absolute_error_y[:index])}', file=file)
    print(f'MAE 60s: {np.mean(np.abs(absolute_error_y[:index]))}', file=file)
    print(f'MSE 60s: {np.mean(absolute_error_y[:index] ** 2)}', file=file)
    print(f'RMSE 60s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}', file=file)

    # 3min = 180s
    index = next((i for i, number in enumerate(timestamps) if number > 180), None)
    print(index,timestamps[index])
    print(f'Maximum Absolute Error 180s: {np.max(absolute_error_y[:index])}', file=file)
    print(f'MAE 180s: {np.mean(np.abs(absolute_error_y[:index]))}', file=file)
    print(f'MSE 180s: {np.mean(absolute_error_y[:index] ** 2)}', file=file)
    print(f'RMSE 180s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}', file=file)

    # 5min = 300s
    index = next((i for i, number in enumerate(timestamps) if number > 300), None)
    print(index,timestamps[index])
    print(f'Maximum Absolute Error 300s: {np.max(absolute_error_y[:index])}', file=file)
    print(f'MAE 300s: {np.mean(np.abs(absolute_error_y[:index]))}', file=file)
    print(f'MSE 300s: {np.mean(absolute_error_y[:index] ** 2)}', file=file)
    print(f'RMSE 300s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}', file=file)

    # 10min = 600s
    index = next((i for i, number in enumerate(timestamps) if number > 600), None)
    print(index,timestamps[index])
    print(f'Maximum Absolute Error 60s: {np.max(absolute_error_y[:index])}', file=file)
    print(f'MAE 600s: {np.mean(np.abs(absolute_error_y[:index]))}', file=file)
    print(f'MSE 600s: {np.mean(absolute_error_y[:index] ** 2)}', file=file)
    print(f'RMSE 600s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}', file=file)

# 统计指标
# 1min = 60s
index = next((i for i, number in enumerate(timestamps) if number > 60), None)
print(index,timestamps[index])
print(f'Maximum Absolute Error 60s: {np.max(absolute_error_y[:index])}')
print(f'MAE 60s: {np.mean(np.abs(absolute_error_y[:index]))}')
print(f'MSE 60s: {np.mean(absolute_error_y[:index] ** 2)}')
print(f'RMSE 60s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}')

# 3min = 180s
index = next((i for i, number in enumerate(timestamps) if number > 180), None)
print(index,timestamps[index])
print(f'Maximum Absolute Error 180s: {np.max(absolute_error_y[:index])}')
print(f'MAE 180s: {np.mean(np.abs(absolute_error_y[:index]))}')
print(f'MSE 180s: {np.mean(absolute_error_y[:index] ** 2)}')
print(f'RMSE 180s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}')

# 5min = 300s
index = next((i for i, number in enumerate(timestamps) if number > 300), None)
print(index,timestamps[index])
print(f'Maximum Absolute Error 300s: {np.max(absolute_error_y[:index])}')
print(f'MAE 300s: {np.mean(np.abs(absolute_error_y[:index]))}')
print(f'MSE 300s: {np.mean(absolute_error_y[:index] ** 2)}')
print(f'RMSE 300s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}')

# 10min = 600s
index = next((i for i, number in enumerate(timestamps) if number > 600), None)
print(index,timestamps[index])
print(f'Maximum Absolute Error 60s: {np.max(absolute_error_y[:index])}')
print(f'MAE 600s: {np.mean(np.abs(absolute_error_y[:index]))}')
print(f'MSE 600s: {np.mean(absolute_error_y[:index] ** 2)}')
print(f'RMSE 600s: {np.sqrt(np.mean(absolute_error_y[:index] ** 2))}')
