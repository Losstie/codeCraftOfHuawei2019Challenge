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
import Map
import Cross
import Road
import Car

Route = namedtuple("Route","carid,startTime,roadId") # roadId 为列表
ROAD_STATE = namedtuple("RoadState","length,speed,channel,start,to,isDuplex,isCongestion,roadState_st,roadState_ts") # 根据channel和length可计算道路负荷

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




