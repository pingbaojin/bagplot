#!/usr/bin/env python

import rosbag
import pandas as pd
from datetime import datetime
from global2local import *

# 定义要提取的 Topic 列表
TOPICS = ['/Odometry', 'gps_rtk_fix']  # 替换为实际的 Topic 名称

# 定义 bag 文件路径
BAG_FILE1 = '/home/mars_ugv/docker_ws/20130110/2025-01-17-11-46-58.bag'  # 替换为实际的 bag 文件路径
BAG_FILE2 = '/home/mars_ugv/docker_ws/data/20130110.bag'  # 替换为实际的 bag 文件路径

# 初始化空的 DataFrame 列表
df_list1 = []
df_list2 = []


def extract_data_from_bag(bag_file, df_list):
    """从 bag 文件中提取数据"""
    global startflag 
    bag = rosbag.Bag(bag_file)
    for topic, msg, t in bag.read_messages(topics=TOPICS):
        # 将时间戳转换为秒
        timestamp = t.to_sec()
        data = {'timestamp': timestamp}
        # 提取消息中的数据



        # 根据 Topic 类型提取数据
        if topic == 'gps_rtk_fix':
            
            data['latitude'] = msg.latitude  # 替换为实际的字段
            data['longitude'] = msg.longitude
            data['altitude'] = msg.altitude
            if startflag:
                startflag=False
                lat0 = msg.latitude
                long0 = msg.longitude
                timestamp0 = timestamp
                print(timestamp)                    
                continue
            x1, y1=calculate_relative_coordinates(lat0, long0, msg.latitude, msg.longitude)
            data['true_x'] = x1
            data['true_y'] = y1
            data['true_z'] = msg.altitude
            

        elif topic == '/Odometry':
            if startflag:
                startflag=False
                timestamp0 = timestamp
                print(timestamp)           
                continue
            data['pos_x'] = msg.pose.pose.position.x
            data['pos_y'] = msg.pose.pose.position.y
            data['pos_z'] = msg.pose.pose.position.z
            data['q_x'] = msg.pose.pose.orientation.x
            data['q_y'] = msg.pose.pose.orientation.y
            data['q_z'] = msg.pose.pose.orientation.z
            data['q_w'] = msg.pose.pose.orientation.w

        data['timestamp'] = timestamp-timestamp0
        data['data_time'] = t
        # print(t)
        # 将数据添加到 DataFrame 列表
        df_list.append(data)
    bag.close()

startflag = True
# 从第一个 bag 文件中提取数据
print(f"Processing {BAG_FILE1}...")
extract_data_from_bag(BAG_FILE1, df_list1)

startflag = True
# 从第二个 bag 文件中提取数据
print(f"Processing {BAG_FILE2}...")
extract_data_from_bag(BAG_FILE2, df_list2)

# 将数据列表转换为 DataFrame
df1 = pd.DataFrame(df_list1)
df2 = pd.DataFrame(df_list2)

# 按照时间戳排序
df1.sort_values(by='timestamp', inplace=True)
df2.sort_values(by='timestamp', inplace=True)

# 合并两个 DataFrame（按照时间戳对齐）
merged_df = pd.merge_asof(df1, df2, on='timestamp', direction='nearest')

# 保存为 Excel 文件
output_file = 'merged_output.xlsx'
merged_df.to_excel(output_file, index=False)
print(f"Merged data saved to {output_file}")

# 保存为 Excel 文件1
output_file = 'gps_rtk_fix.xlsx'
df2 = pd.DataFrame(df_list2)
df2.to_excel(output_file, index=False)
print(f"Merged data saved to {output_file}")

# 保存为 Excel 文件2
output_file = 'Odometry.xlsx'
df1 = pd.DataFrame(df_list1)
df1.to_excel(output_file, index=False)
print(f"Merged data saved to {output_file}")