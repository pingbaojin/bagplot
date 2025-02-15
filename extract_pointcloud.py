import os
import rosbag
from sensor_msgs.msg import PointCloud2
import pcl

def extract_pointcloud(bag_file, topic, output_dir):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开bag文件
    bag = rosbag.Bag(bag_file, 'r')
    index = 0

    for topic, msg, t in bag.read_messages(topics=[topic]):
        # 获取时间戳
        timestamp = msg.header.stamp.to_sec()
        timestamp_str = f"{timestamp:.6f}"

        # 保存PCD文件
        pcd_file = os.path.join(output_dir, f"{timestamp_str}.pcd")
        pcl.save(msg, pcd_file)

        print(f"Saved {pcd_file} with timestamp {timestamp_str}")
        index += 1
        break

    bag.close()

if __name__ == "__main__":
    bag_file = "/home/mars_ugv/docker_ws/data/20130110.bag"  # ROS bag文件路径
    topic = "points_raw"  # 点云话题名称
    output_dir = "./pointcloud"  # 输出目录

    extract_pointcloud(bag_file, topic, output_dir)