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

    def __init__(self, G, roads, crosses):
        """
        :param G: networkx 的图形表示
        :param roads: 所有的道路对象信息
        :param commander: 每一个路口对应的Commander
        """
        self.moment = 0
        self.roads = list(roads)
        self.crosses = list(sorted(crosses, key=lambda x: x.id))

        # 维护全局动态图
        self.graph = G
        # 未到达车辆总数
        self.cars_in_traffic = reduce(lambda y, z: y + z, map(lambda x: len(x.magic_garage[0]), self.crosses))

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

            # 将所有的小车状态标为等待行驶，开始调度道路
            for road in self.roads:
                road.run_moment(self.graph)

            # 循环调度待行驶车辆与路口
            while True:
                # [(当前路口是否存在未调度车辆：{True, False} , 本次运行抵达该路口有多少辆),..,..]
                status = [cross.run_a_time() for cross in self.crosses]

                # 统计到达路口的车辆
                car_arrived_cross = reduce(lambda z, y: z + y, map(lambda x: x[1], status))
                self.cars_in_traffic -= car_arrived_cross

                # 判断是否需要循环调度
                has_car_in_wait = reduce(lambda z, y: z or y, map(lambda x: x[0], status))
                if not has_car_in_wait:
                    break

                # 这里需要添加死锁检测机制
                # 有向图存在权重全部为0的环，且两次调度后车辆状态未变化，则发生死锁现象
                # TODO

            # 调度存储于cross中的车辆
            for cross in self.crosses:
                cross.run_car_in_magic_garage(self.moment)

        e = datetime.now()
        print('调度所有小车到达终点，总共运行：' + str(self.moment) + '时刻！')
        print('调度程序总共运行：{}s'.format((e - s).seconds))

    def update_graph(self):
        """
        根据道路运行情况，动态更新道路状况
        道路的权值即为当前道路可通行的最大速度
        :return:
        """
        for road in self.roads:
            i, j = road.corss_1 - 1, road.corss_2 - 1
            self.graph[i][j] = road.current_v_max(road.corss_1)
            if road.two_way:
                i, j = j, i
                self.graph[i][j] = road.current_v_max(road.corss_2)
