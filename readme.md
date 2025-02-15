# 程序说明
## 1.plotbag.py
根据**2025-01-17-11-46-58.bag**和**20130110.bag**数据生成

fig1 经纬度对比分开

fig2 经纬度对比合并

fig3 经纬度误差

fig4 rtk轨迹曲线

并将3张图片保存到**./fig**文件夹下

运行代码
```
cd /home/mars_ugv/docker_ws/20130110
python3 extract_bag_to_excel.py
```
## 2.extract_bag_to_excel.py
根据**2025-01-17-11-46-58.bag**和**20130110.bag**数据生成excel文件(包括合并文件，rtk和odom数据)

运行代码
```
cd /home/mars_ugv/docker_ws/20130110
python3 extract_bag_to_excel.py
```

## 3.listdir.py
从指定文件夹中获取所有文件名，对文件名进行排序，并将排序后的文件名保存到一个文本文件中

## 4.rtkpos_real.py
从ROS bag文件中读取GPS和Odometry数据，计算相对坐标，并进行插值处理。具体步骤如下：

打开并读取ROS bag文件中的GPS和Odometry数据。

使用Haversine公式和方位角公式计算经纬度之间的距离和方位角。

计算目标点相对于初始点的相对坐标 (dx, dy)。

对低频率数据进行线性插值，使其时间戳与高频率数据对齐。

计算四元数和位姿变换矩阵。
运行代码
```
cd /home/mars_ugv/docker_ws/20130110
python3 rtkpos_real.py 1357847238.555790901.pcd 1357847240.565296888.pcd
```
