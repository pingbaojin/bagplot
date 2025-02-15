# import numpy as np
# from scipy.spatial.transform import Rotation as R
# import pandas as pd

# # 读取Excel文件中的'Sheet1'工作表
# df = pd.read_excel('merged_output.xlsx', sheet_name='Sheet1')
# print(df.head())

# time1=1
# time2=2

# # print(df.loc[time1, ['q_w','q_x','q_y','q_z']])

# # 定义四元数
# quaternion1 = np.array(df.loc[time1, ['q_w','q_x','q_y','q_z']])  # 第一个位置的四元数
# quaternion2 = np.array(df.loc[time2, ['q_w','q_x','q_y','q_z']])  # 第二个位置的四元数

# # 定义局部坐标
# P1 = np.array(df.loc[time1, ['true_x','true_y','true_z']])  # 第一个位置的局部坐标
# P2 = np.array(df.loc[time2, ['true_x','true_y','true_z']])  # 第二个位置的局部坐标

# # 四元数转换为旋转矩阵
# rotation_matrix1 = R.from_quat(quaternion1).as_matrix()
# rotation_matrix2 = R.from_quat(quaternion2).as_matrix()

# # 计算平移向量
# T = P2 - np.dot(rotation_matrix2.T, P1)

# # 组合旋转和平移矩阵
# M = np.eye(4)
# M[:3, :3] = rotation_matrix2
# M[:3, 3] = T

# print("time1:",df.loc[time1, 'timestamp'],"  time2:",df.loc[time2, 'timestamp'])
# print("旋转矩阵 R2:")
# print(rotation_matrix2)
# print("平移向量 T:")
# print(T)
# print("变换矩阵 M:")
# print(M)

import numpy as np

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

# 定义两个载体的局部坐标和四元数
p_A = np.array([1, 2, 3])  # 载体A的局部坐标
q_A = Quaternion(0.707, 0.707, 0, 0)  # 载体A的四元数

p_B = np.array([4, 5, 6])  # 载体B的局部坐标
q_B = Quaternion(0.707, 0, 0.707, 0)  # 载体B的四元数

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

print("位姿变换矩阵 T_B_A:")
print(T_B_A)