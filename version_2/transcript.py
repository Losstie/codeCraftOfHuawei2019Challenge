import logging
import sys
from collections import namedtuple
import numpy as np
import re


ROAD_STATE = namedtuple("RoadState","length,speed,channel,start,to,isDuplex,isCongestion,roadState_st,roadState_ts") # 根据channel和length可计算道路负荷
CarIntro = namedtuple("CarIntro","startCross,aimCross,speed,planTime")

Route = namedtuple("Route","carid,startTime,roadId") # roadId 为列表
TIMELINE = 0

logging.basicConfig(level=logging.DEBUG,
                    filename='../../logs/CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')
class Car:
    def __init__(self,id,startCross,aimCross,speed,planTime,currentSpeed=0):
        self.id = id
        self.startCross = startCross
        self.aimCross = aimCross
        self.locateAtRoad = None
        self.roadSt = startCross+'-'+"-1"
        self.whichChannelOfRoad = None
        self.distanceEntryCross = None
        self.location = startCross
        self.speed = speed
        self.currentSpeed = currentSpeed
        self.planTime = planTime
        self.realTime = planTime
        self.route = []
        self.isArrival = 0

def initMap(roadPath,crossPath):
    """
    初始化地图
    input: cross.txt road.txt
    return: map  type:matrix(n,n) road dict==>nametuple
    """
    with open(roadPath,'r') as f:
        road = f.readlines()
    Road = {}
    for i in range(len(road)):
        if i ==0:
            continue
        else:
            temp1 = re.sub('[\n()]','',road[i])
            temp2 = [int(x) for x in temp1.split(",")]
            st = {}
            ts = {}
            if temp2[6] ==1:
                for k in range(temp2[3]):
                    st[str(k+1)] = []
                    ts[str(k+1)] = []
                st["perChannelMaxCap"] = temp2[1]
                ts["perChannelMaxCap"] = temp2[1]
            else:
                for k in range(len(temp2[3])):
                    st[str(k+1)] = []
                st["perChannelMaxCap"] = temp2[1]
            Road[str(temp2[0])] = ROAD_STATE(
                length=temp2[1],
                speed=temp2[2],
                channel=temp2[3],
                start=temp2[4],
                to=temp2[5],
                isDuplex=temp2[6],
                isCongestion=0,
                roadState_st=st,
                roadState_ts=ts,
            )
    with open(crossPath,'r') as f:
        cross = f.readlines()
    cross_num = len(cross)
    Map = np.zeros((cross_num-1,cross_num-1))
    for i in range(cross_num):
        if i==0:
            continue
        else:
            temp1 = re.sub('[\n()]', '', cross[i])
            temp2 = [int(x) for x in temp1.split(",")]
            for j in range(len(temp2)):
                if j==0:
                    continue
                if temp2[j] == -1:
                    continue
                else:
                    print(str(temp2[j]))
                    if Road[str(temp2[j])].start == i:
                        tmp = Road[str(temp2[j])].to
                        Map[i-1,tmp-1] = str(temp2[j])
                        if Road[str(temp2[j])].isDuplex ==1:
                            Map[tmp - 1, i-1] = str(temp2[j])
    return Map,Road

def initCarSchedule(carPath):
    """
    初始化汽车及调度时刻表
    :param carPath:
    :return: Car type dict-->nametuple
    """
    with open(carPath,'r') as f:
        car = f.readlines()
    Schedule = {} # key:time value:[car_id,car_id,...,car_id]
    CARINTRODUCTION = {}
    cars = []
    for i in range(len(car)):
        if i==0:
            continue
        else:
            temp1 = re.sub('[\n()]','',car[i])
            temp2 = [int(x) for x in temp1.split(',')]
            CARINTRODUCTION[str(temp2[0])] = CarIntro(
                startCross=str(temp2[1]),
                aimCross=str(temp2[2]),
                speed=temp2[3],
                planTime=temp2[4],
            )
            cars.append(str(temp2[0]))
            if str(temp2[4]) not in Schedule:
                Schedule[str(temp2[4])] = []
            else:
                Schedule[str(temp2[4])].append(str(temp2[0]))


    # print(Schedule)
    # print(CARINTRODUCTION)
    return Schedule,CARINTRODUCTION,cars

def currentCarState(mode=0,carId=None,practiceTime=None,locateRoad=None,carLocationAtRoad=None,currentSpeed=None,carState=None,travelDirection=None,isArrvial=None):
    """
    车辆状态实时更新
    param：
    mode:0 初始化车辆状态 1 更新车辆状态
    carId:更新车辆的id
    practiceTime：车辆实际出发时间
    locateRoad：所在路段
    carLocationAtRoad: 车辆在道路的位置
    travelDirection:车辆在道路中行驶方向
    currentSpeed：目前车辆速度
    isArrival:是否到达目的地
    carState: choice is at ["waiting","travel"]
    return: CarState type: nametuple
    """
    pass

def updateRoadState():
    "更新道路状态"
    pass

def updateMap():
    "更新地图，拥堵路段不可到达"
    pass

def routePlanning(car,CurrntMap):
    """
    路线规划  最短路径算法
    :param car: 车辆对象 type class
    :param CurrntMap: 实时地图  type matrix
    :return: route []
    """
    pass



def schedulingSystem(scheduleTable,Map,Road,CarTable,NotArrivalCarTable):
    """
    调度系统
    :param scheduleTable:调度时刻表
    :param Map: 地图矩阵
    :param Road: 道路
    :param CarTable: 汽车
    :param NotArrivalCarTable:未到达目的地车辆列表
    :return:
    """
    timeLine = 0 # 初始化时刻表
    # 初始化行驶中的汽车列表
    drivingCar = []
    while(len(NotArrivalCarTable)!=0):
        # 时刻加一个时间片
        timeLine=timeLine+1
        # 检测该时刻是否有需要的启动车辆
        if str(timeLine) in scheduleTable:
            # 该时刻下需要启动的车辆id列表
            tempScheduleTable = scheduleTable[str(timeLine)]
            # 初始化即将启动的汽车列表，装启动汽车对象
            comingSoonCar = []







    return

def outputResults(routesTable):
    """
    导出路径规划txt文件
    # (car_id,starTime,route....)
    :param routesTable: 每辆车的路径规划和出发时间
    :return: 
    """


def main():
    if len(sys.argv) != 5:
        logging.info('please input args: car_path, road_path, cross_path, answerPath')
        exit(1)

    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]

    logging.info("car_path is %s" % (car_path))
    logging.info("road_path is %s" % (road_path))
    logging.info("cross_path is %s" % (cross_path))
    logging.info("answer_path is %s" % (answer_path))

    globalMap,globalRoad = initMap(road_path,cross_path)
    SCHEDULETABLE,CARINTRODUCTION,CARS = initCarSchedule(car_path)
    routesTable=schedulingSystem(scheduleTable=SCHEDULETABLE,Map=globalMap,Road=globalRoad,CarTable=CARINTRODUCTION,NotArrivalCarTable=CARS)

# to read input file
# process
# to write output file


if __name__ == "__main__":
    main()