# -*- coding: utf-8 -*-
"""
Created on 2019/3/13 下午1:55

@author: Evan Chen
"""
from datetime import datetime
from functools import reduce


class Scheduler():
    """
    存储全局行驶信息，负责总调度
    """

    def __init__(self, cars, roads, crosses):
        """
        :param G: networkx 的图形表示
        :param roads: 所有的道路对象信息
        :param commander: 每一个路口对应的Commander
        """
        self.moment = 0
        self.cars = cars
        self.roads = list(roads)
        self.crosses = list(sorted(crosses, key=lambda x: x.id))

        # 未到达车辆总数
        self.cars_in_traffic = reduce(lambda y, z: y + z, map(lambda x: len(x.magic_garage[0]), self.crosses))

    def get_path(self):
        for car in self.cars:
            print(car.car_id, car.sche_time, car.real_time, car.path)

    def run(self):
        """
        根据算法确定每个小车的运行路线
        :return:
        """
        s = datetime.now()
        # 一次循环执行一个时间片段内小车调度
        # 知道所有小车到达所有目的地
        while self.cars_in_traffic != 0:
            self.moment += 1
            print(self.moment)
            # 将所有的小车状态标为等待行驶，开始调度道路
            for road in self.roads:
                road.run_moment()

            # 循环调度待行驶车辆与路口
            has_car_in_wait = True
            while has_car_in_wait:
                # [(当前路口是否存在未调度车辆：{True, False} , 本次运行抵达该路口有多少辆),..,..]
                status = [cross.run_a_time(self.moment) for cross in self.crosses]

                # 统计到达路口的车辆
                car_arrived_cross = reduce(lambda z, y: z + y, map(lambda x: x[1], status))
                self.cars_in_traffic -= car_arrived_cross

                # 判断是否需要循环调度
                has_car_in_wait = reduce(lambda z, y: z or y, map(lambda x: x[0], status))

                # 这里需要添加死锁检测机制
                # 有向图存在权重全部为0的环，且两次调度后车辆状态未变化，则发生死锁现象
                # TODO

            # 调度存储于cross中的车辆
            for cross in self.crosses:
                cross.run_car_in_magic_garage(self.moment)

        self.get_path()

        e = datetime.now()
        print('调度所有小车到达终点，总共运行：' + str(self.moment) + '时刻！')
        print('调度程序总共运行：{}s'.format((e - s).seconds))
