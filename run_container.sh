#!/bin/bash

# 容器名称
CONTAINER_NAME="fastlio2"

# #pcd文件
# PCD1="1357847482.206832885.pcd" 
# PCD2="1357847485.112730026.pcd"

#pcd文件
PCD1="1357847482.206832885.pcd" 
PCD2="1357847485.112730026.pcd"

xhost +
# 检查容器是否已经存在
if [ "$(docker ps -q -f name=^${CONTAINER_NAME}$)" ]; then
    echo "容器 ${CONTAINER_NAME} 已经在运行。"
else
    if [ "$(docker ps -aq -f status=exited -f name=^${CONTAINER_NAME}$)" ]; then
        echo "容器 ${CONTAINER_NAME} 已存在但已停止，正在重新启动..."
        docker start ${CONTAINER_NAME}
        # 等待容器启动完成
        # echo "等待容器启动完成..."
        # sleep 5
    fi
fi


# 确保脚本具有可执行权限
docker exec -it ${CONTAINER_NAME} bash -c "chmod +x /home/mars_ugv/docker_ws/20130110/rtkpos_real.py"

# 在容器中运行Python程序
echo "正在容器中运行Python程序..."
docker exec -it ${CONTAINER_NAME} bash -c "cd /home/mars_ugv/docker_ws/20130110 && python3 rtkpos_real.py ${PCD1} ${PCD2}"

# 停止容器
docker stop ${CONTAINER_NAME}

echo ""
echo "运行ubuntu20.04图像配准程序"
# 容器名称
CONTAINER_NAME="ubuntu20.04"

# 检查容器是否已经存在
if [ "$(docker ps -q -f name=^${CONTAINER_NAME}$)" ]; then
    echo "容器 ${CONTAINER_NAME} 已经在运行。"
else
    if [ "$(docker ps -aq -f status=exited -f name=^${CONTAINER_NAME}$)" ]; then
        echo "容器 ${CONTAINER_NAME} 已存在但已停止，正在重新启动..."
        docker start ${CONTAINER_NAME}
        # 等待容器启动完成
        # echo "等待容器启动完成..."
        # sleep 5
    fi
fi

# 在容器中运行Python程序
echo "正在容器中运行Python程序..."
docker exec -it ${CONTAINER_NAME} bash -c "cd /catkin_ws/3D-Registration-with-Maximal-Cliques/Linux/Release && ./MAC --pbjdemo ${PCD1} ${PCD2}"

# 停止容器
docker stop ${CONTAINER_NAME}