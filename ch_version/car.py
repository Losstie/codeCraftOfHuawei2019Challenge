# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:18

@author: Evan Chen
"""
import networkx as nx


class Car():
    def __init__(self, car_id, loc, dest, v_max, sche_time):
        """
        :param car_id: 小车唯一标识
        :param lo: 小车当前所处路口
        :param dest: 目的地
        :param v: 小车最大速度
        :param sche_time: 计划出发时间
        :param moment: 所处时间片段
        """
        # 固定属性
        self.loc = int(loc)
        self.dest = int(dest)
        self.v_max = v_max
        self.car_id = car_id
        self.sche_time = sche_time
        self.real_time = sche_time  # 小车实际出发时间

        # 动态属性
        self.path = list()  # 记录经过的路径
        self.v = self.v_max  # 当前小车速度
        self.moment = 0  # 小车所处时间片段
        self.road_id = 0  # 小车所在道路
        self.lane_id = 0  # 小车所处车道
        self.lane_dis = 0  # 小车在当前车道上的位置
        self.lane_left = 6  # 小车在当前车道的可行驶距离
        self.stat = 'wait'  # 标志小车在某个时间片的状态

        self.next_car = None  # 小车前方车辆，若为None，则前方没有车
        self.behind_car = None  # 小车后方车辆，若为None，则前方没有车
        self.next_cross_id = None  # 小车在下一个路口会选择道路, None表示不出路口
        self.next_road_id = None  # 小车在下一个路口会选择道路, None表示不出路口

    def set_v(self, limit):
        """
        根据道路状况修改小车行进速度
        :param limit: 前方车辆速度 or 道路最高限速
        :return:
        """
        self.v = min(self.v_max, limit)

    @property
    def has_reached(self):
        """
        是否到达目的地
        """
        return True if self.loc == self else False

    def update_stat(self, graph):
        """
        运动一个时刻，改变所有道路上的小车状态
        调度顺序：从出口处向入口处调度，总共有四种情况：
        1.前方无阻挡车辆，且不出路口，则运行至终止位置，小车状态标记为：终止
        2.前方无阻挡车辆，需要出路口，则将小车状态标记为：等待行驶
        3.前方有阻挡车辆，阻挡车辆的状态为终止状态，则将小车行驶至阻挡车辆后面，将小车状态标记为：终止
        4.前方有阻挡车辆，阻挡车辆的状态为待行驶状态，则将小车状态标志为：等待行驶
        :return:
        """
        can_run_a_moment = self.lane_left > self.v * 1
        if self.next_car is None:
            if can_run_a_moment:
                self.stat = 'finial'  # 1
                self.lane_dis += self.v
                self.lane_left -= self.v
                if not self.behind_car is None:
                    self.behind_car.lane_left += self.v
            else:
                # 即将出路口
                self.stat = 'wait'  # 2
                self.update_route(graph)
        else:
            if can_run_a_moment:
                self.stat = 'finial'  # 1
                self.lane_dis += self.v
                self.lane_left -= self.v
                if not self.behind_car is None:
                    self.behind_car.lane_left += self.v

            elif self.next_car.stat == 'finial':  # 3
                self.stat = 'finial'
                next_lane_dis = self.next_car.lane_dis - 1
                delta_dis = next_lane_dis - self.lane_dis
                self.lane_dis = next_lane_dis
                if not self.behind_car is None:
                    self.behind_car.lane_left += delta_dis
            else:
                self.stat = 'wait'  # 4

    def run_to_edge(self):
        """将小车开至车道边缘, 并调度同一条道路之后的小车"""
        car = self
        behind_car = self.behind_car
        while True:
            self.stat = 'finial'
            car.lane_dis += car.lane_left
            car.lane_left = 0
            if behind_car.stat == 'finial' or behind_car.stat is None:
                break
            car = behind_car
            behind_car = car.behind_car

    def update_route(self, graph, update=True):
        """
        根据动态图,更新下一条经过的道路
        """
        path = nx.dijkstra_path(graph, source=self.loc, target=self.dest, weight='weight')
        self.next_cross_id = path[1]

        # 更新图
        if update:
            graph[self.loc][self.next_cross_id]['weight'] = self.v
