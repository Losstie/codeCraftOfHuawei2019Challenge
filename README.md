# codeCraftOfHuawei2019Challenge
华为2019软件精英挑战赛

## 运行说明
### 测试数据集
运行命令行：
```commandline
python CodeCraft-2019.py ../config_test/car_test.txt ../config_test/road_test.txt
 ../config_test/cross_test.txt ../config_test/answer_test.txt 
```

### 训练赛地图
 - config_1
 - config_2
 
### 新增地图

 - config_3
 - config_4

### 正式初赛地图

 - config_5
 - config_6
 
> 将config_*的文件复制到config中，使用命令行：

```commandline
python CodeCraft-2019.py ../config/car.txt ../config/road.txt
 ../config/cross.txt ../answer.txt 
```

## 代码说明

目前三个版本均为边走边规划，静等各位大神亮出思路。反思一波
### src version

> 设置每个路口尝试出车数量，动态调整窗口大小。map1可进700.正式赛超时三四分钟左右

### multithreading version

> 多线程版本，分割数据以分别规划。线下不超时。上去就超时了。。。

### 745map1

> 调整所有路口每轮次发车数量，使用TCP 拥塞控制乞丐版。最优达到745-map1.正式赛超时警告！