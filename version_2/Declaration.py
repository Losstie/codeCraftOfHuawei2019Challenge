#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: SDK_python
@file:Declaration.py
@author: dujiahao
@create_time: 2019/3/11 21:08
@description:
"""
import re
from collections import namedtuple
import numpy as np

Route = namedtuple("Route","carid,startTime,roadId") # roadId 为列表
ROAD_STATE = namedtuple("RoadState","length,speed,channel,start,to,isDuplex,isCongestion,roadState_st,roadState_ts") # 根据channel和length可计算道路负荷

# 路口类声明
class Cross:
    def __init__(self,id,roadId_1,roadId_2,roadId_3,roadId_4):
        self.id = id # 路口id
        self.roadIdList = self.orderRoad(roadId_1,roadId_2,roadId_3,roadId_4) # 道路ID从小到大排序后的道路列表，元素为字典
        self.garageParkingCar = [] # 装载车库中待启动行驶的车辆对象
        self.waitingCar = 0 # 该路口等待行驶车辆数量
    def orderRoad(self,roadId_1,roadId_2,roadId_3,roadId_4):
        """
        将道路按ID从小到大排序
        :param roadId_1:
        :param roadId_2:
        :param roadId_3:
        :param roadId_4:
        :return: 列表，每个元素为一个字典 属性： id position
        """
        r = [{"id":roadId_1,"position":0},
             {"id":roadId_2,"position":1},
             {"id":roadId_3,"position":2},
             {"id":roadId_4,"position":3}]
        for i in range(4):
            for j in range(4-i-1):
                if int(r[i]["id"])>int(r[i+j+1]["id"]):
                    tmp = r[i+j+1]
                    r[i+j+1] = r[i]
                    r[i] = tmp

        return r

# 道路类声明
class Road:
    def __init__(self,id,length,speed,channel,oriented_f,oriented_t,isDuplex):
        self.id = id # 道路id
        self.length = length # 道路长度
        self.speed = speed # 道路限速
        self.oriented_f = oriented_f # 道路朝向，起点
        self.oriented_t = oriented_t # 道路朝向，终点
        self.isDuplex = isDuplex
        self.numbersOfCar = 0
        channels = [None] * channel
        for ch in range(channel):
            channels[ch] = [None]*length
        self.channels_st = channels
        if isDuplex == 1:
            self.channels_ts = [list(x) for x in channels]
    def caculateRateOfBlocked(self,oritention):
        """计算道路拥堵率"""
        num = 0
        pass

# 地图类声明
class Map:
    def __init__(self,roadPath,crossPath):
        # map 邻接矩阵 路口A--经由道路（对象）--路口B
        # road 道路总表  key: roadId value:Road对象
        # cross 路口列表 存储路口对象
        self.map,self.roads,self.cross = self.initMap(roadPath,crossPath)

    def initMap(self,roadPath,crossPath):

        with open(crossPath, 'r') as f:
            crossData = f.readlines()
        cross_num = len(crossData)-1
        cross = [None]*cross_num

        for i in range(cross_num+1):
            if i == 0:
                continue
            else:
                temp1 = re.sub('[\n()]', '', crossData[i])
                temp2 = temp1.split(",")
                cross[i-1] = Cross(temp2[0],temp2[1],temp2[2],temp2[3],temp2[4])
        map = np.zeros((cross_num,cross_num))
        roads = {}
        with open(roadPath, 'r') as f:
            road = f.readlines()
        for i in range(len(road)):
            if i == 0:
                continue
            else:
                temp1 = re.sub('[\n()]', '', road[i])
                temp2 = [int(x) for x in temp1.split(",")]

                oriented_f = temp2[4]
                oriented_t = temp2[5]

                if temp2[6] ==1:
                    map[oriented_f - 1, oriented_t - 1] = str(temp2[0])
                    map[oriented_t - 1, oriented_f - 1] = str(temp2[0])
                roads[str(temp2[0])] = Road(str(temp2[0]),temp2[1],temp2[2],temp2[3],str(temp2[4]),str(temp2[5]),temp2[6])
        # print(cross[0].id,cross[0].roadIdList)
        return map,roads,cross

# 记录仪类声明
class Recording:
    def __init__(self):
        self.carHistoryBlockedRoads = {}
    def recordingCarHistory(self,car):
        """
        行车记录仪
        :param car: 车辆对象
        :return:历史行车遭遇等待的路线，及路线上多损耗的时间
        """
        pass

# 车辆类声明
class Car:
    def __init__(self,id,startCross,aimCross,speed,planTime):
        self.id = id
        self.startCross = startCross
        self.aimCross = aimCross
        self.speed = speed
        self.planTime = planTime # 车辆计划出发时间
        self.realTime = planTime # 车辆实际出发时间

        self.locateAtRoad = {"roadId":None,"roadTerminal":None}
        self.roadSt = None # 所处道路的终点路口
        self.route = [] # 车辆行驶路线
        self.isArrival = 0 #是否到达目的地
        self.state = None # 车辆状态  终止状态 termination 等待行驶状态 waiting
        self.signal = None #  straight left right
        self.abnormalTermination = 0 # 是否由于前车终止而终止，0为否 1 为是
    def isBlocking(self,currentSpeed,currentPosition,channel):
        """
        判断前方是否有车辆阻挡，有就返回阻挡车辆的位置（所处的索引），没有就返回 0
        :param currentSpeed: 车辆行驶速度
        :param currentPosition: 车辆目前位置
        :param channelLength: 车道长度
        :param road: 所处道路
        :return: int
        """
        pointer = currentPosition
        # 是否检查完
        isCheckOver = False
        while(not isCheckOver):
            x = pointer -currentPosition
            # 如果目前移动位置达到单位行驶距离或者到了出口则返回0 说明没有阻挡
            if x == currentSpeed or pointer>len(channel)-1:
                return 0
            # 否则检查是否目前指针指向有无车辆，有车返回其位置
            elif channel[pointer]!=None:
                return pointer
            # 无车继续循环 指针加一
            else:
                pointer = pointer+1

    def getDirection(self,roads,cross):
        """
        获得汽车路口行驶方向
        :param roads: 
        :param cross: 
        :return: 
        """""
        locateRoadId = self.locateAtRoad['id']
        nextRoadId = self.route(self.route.index(locateRoadId)+1)

        for i in range(4):
            if cross[i]['id'] == -1:
                continue
            else:
                if cross[i]['id'] == locateRoadId:
                    x = cross[i]['position']
                elif cross[i]['id'] == nextRoadId:
                    y = cross[i]['position']
                else:
                    continue
        # 计算方向
        if abs(x - y) == 2:
            return 'D'
        elif (y - x == 1) or (y-x == -3):
            return 'L'
        elif (y - x == -1) or (y - x == 3):
            return 'R'


    def judgeGoThroughCrossDirection(self,scheduleCenter):
        """
        判断在过道路时候是直走还是左转或者右转
        :param scheduleCenter: 调度中心
        :return:
        """
        pass

    def judgeIsOrNotLocateAtCross(self,scheduleCenter):
        """
        判断是否处于要变换道路的路口
        :param scheduleCenter: 调度中心
        :return:
        """
        pass
    def judgeDrivingSpeedAndDistance(self,scheduleCenter):
        """
        判断行驶速度和能够形式的距离
        :param scheduleCenter: 调度中心
        :return:
        """
        pass
    def routePlan(self,scheduleCenter):
        """
        路径规划
        :return:
        """
        pass

    def updateCarstate(self,scheduleCenter):
        """
        更新车辆状态
        :param scheduleCenter: 调度中心
        :return:
        """
        pass


# 调度中心类声明
class Dispatchcenter:
    def __init__(self,roadPath,crossPath,carPath):

        self.map = self.initMap(roadPath,crossPath)
        self.carTable = self.initCarTable(carPath)

    def initMap(self,roadPath,crossPath):
        """
        初始化地图和道路
        :param roadPath: road.txt
        :param crossPath: cross.txt
        :return: map  type:matrix(n,n) road dict==>nametuple
        """
        mapCross = Map(roadPath,crossPath)
        return mapCross

    def initCarTable(self,carPath):
        """
        初始化汽车列表
        :param carPath:
        :return:
        """
        carTable = {}
        with open(carPath, 'r') as f:
            car = f.readlines()

        for i in range(len(car)):
            if i == 0:
                continue
            else:
                temp1 = re.sub('[\n()]', '', car[i])
                temp2 = [int(x) for x in temp1.split(',')]

                # 判断汽车属于哪个车库
                whichGarage = temp2[1]
                # 大前提必须是cross文件 id从上向下升序排列
                # 记录下车库中停车ID
                self.map.cross[whichGarage-1].garageParkingCar.append(str(temp2[0]))

                carTable[str(temp2[0])] = Car(id=str(temp2[0]),
                                              startCross=str(temp2[1]),
                                              aimCross=str(temp2[2]),
                                              speed=temp2[3],
                                              planTime=temp2[4])

        return carTable
    def checkConfig(self,car,crossId):
        """
        检测是否冲突
        :param car: 检测车辆
        :param crossId: 所处路口ID
        :return: bool
        """
        pass

    def arrangeOrderSetOffCar(self):
        """
        将车库中的车辆按照计划出发时间先后排序，如果时间相同，车辆ID小的在前面
        :return:
        """

        return

    def theCarStandMapSituation(self,car):
        """
        获取当前车辆所处的地图
        :param car:
        :return:
        """
        pass
        currentMap = None
        return currentMap

    def scheduling(self):
        """
        车辆调度
        同路口多条道路车辆调度按各条道路的ID升序进行调度车辆行驶，整个系统按路口升序循环调度
        系统调度先调度在路上行驶的车辆进行行驶，当道路上所有车辆全部不可再行驶后再调度等待上路行驶的车辆。
        调度等待上路行驶的车辆，按等待车辆ID升序进行调度，进入道路车道依然按车道小优先进行进入。
        :return:
        """
        timeLine = 0
        # 地图对象 包含cross roads map矩阵
        map = self.map

        flag = True
        while(flag):
            carTable = carTable
            # 首先遍历道路
            for roadId,road in map.roads.items():
                print("遍历道路%s" %roadId)
                if road.numbersOfCar == 0:
                    continue
                else:
                    channelLength = road.length
                    for channel in road.channels_st:
                        for position in range(channelLength):
                            # 如果该位置没有车则遍历下一个位置
                            if channel[position] == None:
                                continue
                            # 有车的话，就进行车辆调度
                            else:
                                # 该位置车辆对象
                                car = carTable[channel[position]]
                                # 汽车驶向的路口
                                crossIndex = int(car.locateAtRoad["roadTerminal"])
                                currentSpeed = min(car.speed,road.speed)
                                # 如果车经过行驶速度（前方没有车辆阻挡）可以出路口，那么标记为等待行驶装填
                                isBlocked = car.isBlocking(currentSpeed,position,channel)
                                if (currentSpeed+position>channelLength-1) and (not isBlocked):
                                    car.state = "waiting"
                                    # 汽车驶向的路口等待车辆数量加1
                                    map.cross[crossIndex-1].waitingCar = map.cross[crossIndex-1].waitingCar +1
                                # 如果车辆经过行驶速度（前方没有车辆阻挡）不能出路口，则车辆行驶其最大可行驶速度
                                elif (not isBlocked) and (currentSpeed+position<=channelLength-1):
                                    channel[currentSpeed+position] = channel[position]
                                    channel[position] = None
                                    car.state = "termination"
                                else:
                                    # 如果前面有阻挡车辆，则跟随其状态
                                    frontCarState = carTable[isBlocked].state
                                    if frontCarState == "waiting":
                                        map.cross[crossIndex-1].waitingCar = map.cross[crossIndex-1].waitingCar+1
                                    car.state = frontCarState
                    if road.isDuplex == 1:
                        for channel in road.channels_ts:
                            for position in range(channelLength):
                                # 如果该位置没有车则遍历下一个位置
                                if channel[position] == None:
                                    continue
                                # 有车的话，就进行车辆调度
                                else:
                                    # 该位置车辆对象
                                    car = carTable[channel[position]]
                                    # 汽车驶向的路口
                                    crossIndex = int(car.locateAtRoad["roadTerminal"])
                                    currentSpeed = min(car.speed, road.speed)
                                    # 如果车经过行驶速度（前方没有车辆阻挡）可以出路口，那么标记为等待行驶装填
                                    isBlocked = car.isBlocking(currentSpeed, position, channel)
                                    if (currentSpeed + position > channelLength - 1) and (not isBlocked):
                                        car.state = "waiting"
                                        # 汽车驶向的路口等待车辆数量加1
                                        map.cross[crossIndex - 1].waitingCar = map.cross[crossIndex - 1].waitingCar + 1
                                    # 如果车辆经过行驶速度（前方没有车辆阻挡）不能出路口，则车辆行驶其最大可行驶速度
                                    elif (not isBlocked) and (currentSpeed + position <= channelLength - 1):
                                        channel[currentSpeed + position] = channel[position]
                                        channel[position] = None
                                        car.state = "termination"
                                    else:
                                        # 如果前面有阻挡车辆，则跟随其状态
                                        frontCarState = carTable[isBlocked].state
                                        if frontCarState == "waiting":
                                            map.cross[crossIndex - 1].waitingCar = map.cross[
                                                                                       crossIndex - 1].waitingCar + 1
                                        car.state = frontCarState

            # 开始调度路口
            for c in range(len(map.cross)):
                while(map.cross[c].waitingCar!=0):
                    for r in map.cross[c].roadIdList:
                        # 此处r为字典 key : id , position
                        # 如果路口连接的道路id为-1（没路）或者连接道路不是驶向该路口，那么遍历下一条道路
                        if r['id'] == -1 or (map.roads[r['id']].oriented_t != c+1 and map.roads[r['id']].isDuplex!=1):
                            continue
                        else:
                            # 获得道路对象
                            road = map.roads[r['id']]
                            if road.oriented_t == c+1:
                                channels = road.channels_st
                            else:
                                channels = road.channels_ts
                            channelLength = road.length
                            """
                            -3-1- 行驶顺序
                            -4-2- 从路口开始最前面一排到最后面一排
                            """
                            for pointer in range(channelLength):
                                pass




