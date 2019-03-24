# -*- coding: utf-8 -*-
"""
Created on 2019/3/13 下午1:55

@author: Evan Chen
"""
from datetime import datetime
from functools import reduce
import time


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
            print('moment: ', self.moment)
            # 将所有的小车状态标为等待行驶，开始调度道路
            for road in self.roads:
                road.run_moment()

            # 循环调度待行驶车辆与路口
            pre_conflict_crosses = list()
            has_car_in_wait = True
            while has_car_in_wait:
                # [(当前路口是否存在未调度车辆：{True, False} , 本次运行抵达该路口有多少辆, 发生冲突的车辆id),..,..]
                status = [cross.run_a_time(self.moment) for cross in self.crosses]

                # 统计到达路口的车辆
                car_arrived_cross = reduce(lambda z, y: z + y, map(lambda x: x[1], status))
                self.cars_in_traffic -= car_arrived_cross

                # 判断是否需要循环调度
                has_car_in_wait = reduce(lambda z, y: z or y, map(lambda x: x[0], status))

                # 这里需要添加死锁检测机制
                # 上一次冲突路口和当前冲突路口一致说明发生死锁
                conflict_crosses = list(map(lambda x: x[0], filter(lambda x: x[1][0] is True, enumerate(status))))
                if self.is_lock(pre_conflict_crosses, conflict_crosses):
                    car_id_ls = reduce(lambda x, y: x + y, map(lambda x: x[2], status))
                    self.re_route_path(car_id_ls)
                pre_conflict_crosses = conflict_crosses

            # 调度存储于cross中的车辆
            for cross in self.crosses:
                cross.run_car_in_magic_garage(self.moment)

        self.get_path()

        e = datetime.now()
        print('调度所有小车到达终点，总共运行：' + str(self.moment) + '时刻！')
        print('调度程序总共运行：{}s'.format((e - s).seconds))

    def is_lock(self, pre, new):
        """
        判断调度是否发生死锁
        若前一次冲突路口的id 和 当前冲突离开的 id序列完全一致，则说明发生死锁现象
        :param pre:
        :param new:
        :return:
        """
        if len(pre) != len(new) or len(pre) ==0:
            return False

        for idx in range(len(pre)):
            if pre[idx] != new[idx]:
                return False
        return True

    def re_route_path(self, car_id_ls):
        """
        为发生冲突的小车重新 随机 规划路线
        道路不能为当前道路，也不能为发生冲突的道路
        若只有当前道路或发生冲突的道路可行，则不改变其路径
        :param car_id_ls:
        :return:
        """
        car_dict = dict([(car.car_id, car) for car in self.cars])
        cross_dict = dict([(cross.id, cross) for cross in self.crosses])
        for car_id in car_id_ls:
            c_car = car_dict[car_id]
            cross_id = c_car.loc
            cross = cross_dict[cross_id]

            #获得该路口连接的其他路口
            candidate_cross = set()
            for road in cross.roads_dict.values():
                if cross.id == road.cross_1:
                    candidate_cross.add(road.cross_2)
                if road.two_way:
                    candidate_cross.add(road.cross_1)

            forbid = {c_car.next_cross_id, c_car.before_cross_id}
            candidate_cross -= forbid
            if len(candidate_cross) == 0:
                continue

            # 重新规划道路
            c_car.next_cross_id = candidate_cross.pop()


