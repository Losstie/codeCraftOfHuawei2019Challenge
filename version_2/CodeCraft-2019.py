import logging
import sys


from Declaration import Cross,Road,Map,Car,Dispatchcenter,Recording


logging.basicConfig(level=logging.DEBUG,
                    filename='../../logs/CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')

# def schedulingSystem(scheduleTable,Map,Road,CarTable,NotArrivalCarTable):
#     """
#     调度系统
#     :param scheduleTable:调度时刻表
#     :param Map: 地图矩阵
#     :param Road: 道路
#     :param CarTable: 汽车
#     :param NotArrivalCarTable:未到达目的地车辆列表
#     :return:
#     """
#     timeLine = 0 # 初始化时刻表
#     # 初始化行驶中的汽车列表
#     drivingCar = []
#     comingSoonCar = []
#     while(len(NotArrivalCarTable)!=0):
#         # 优先运行已经在运行的车辆
#         if len(drivingCar)!=0:
#             for drive in drivingCar:
#                 if drive.judgeIsOrNotDriving(Map,Road):
#                     drive.updateCarstate(Map,Road)
#                 else:
#                     drive.signal = "waiting"
#
#         # 运行待启动的车辆
#         if len(comingSoonCar)!=0:
#             nums = len(comingSoonCar)
#             tmpSoonCar = comingSoonCar.copy()
#             for i in range(nums):
#                 if comingSoonCar[i].planTime > timeLine:
#                     break
#                 else:
#
#                     comingSoonCar[i].route = routePlanning(comingSoonCar[i],Map,Road)
#
#                     # 判断要走的路是否能走，不能就滞留列表 能走就更改车辆状态，加入行驶车辆
#                     if comingSoonCar[i].judgeIsOrNotDriving(Map,Road):
#                         comingSoonCar[i].updateCarstate(Map,Road)
#                         s = tmpSoonCar.pop(i)
#                         drivingCar.append(s)
#                     else:
#                         continue
#
#         comingSoonCar = tmpSoonCar.copy()
#
#         # 检测该时刻是否有需要的启动车辆,如果有加入待启动队列，出队使用list函数pop(0)
#         if str(timeLine) in scheduleTable:
#             # 该时刻下需要启动的车辆id列表
#             tempScheduleTable = scheduleTable[str(timeLine)]
#             # 初始化即将启动的汽车列表，装启动汽车对象
#             for t in tempScheduleTable:
#                 tt = CarTable[t]
#                 comingSoonCar.append(
#                     Car(tt.id, tt.startCross, tt.aimCross, tt.speed, tt.planTime, signal="waiting"))
#         # 时刻加一个时间片
#         timeLine=timeLine+1

    # return

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

    # SheduleSystem = Dispatchcenter(road_path,cross_path,car_path)
    # SheduleSystem.scheduling()



# to read input file
# process
# to write output file


if __name__ == "__main__":
     main()
