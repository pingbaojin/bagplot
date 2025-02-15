# import os

# # 替换为你的目标文件夹路径
# folder_path = '/home/mars_ugv/docker_ws/data/pcd20130110'

# # 获取文件夹下的所有文件和文件夹名称
# all_items = os.listdir(folder_path)

# # 过滤出文件名
# file_names = [item for item in all_items if os.path.isfile(os.path.join(folder_path, item))]

# # 输出文件名
# for file_name in file_names:
#     print(file_name)


import os

# 替换为你的目标文件夹路径
folder_path = '/home/mars_ugv/docker_ws/data/pcd20130110'
output_file = 'pcd20130110.txt'  # 输出文件名

# 获取文件夹下的所有文件名
file_names = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

# 对文件名进行排序
file_names.sort()

# 将排序后的文件名写入txt文件
with open(output_file, 'w', encoding='utf-8') as f:
    for file_name in file_names:
        f.write(file_name + '\n')

print(f"文件名已排序并保存到 {output_file}")