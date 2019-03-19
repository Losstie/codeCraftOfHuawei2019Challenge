# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:18

@author: Evan Chen
"""
import networkx as nx
from copy import deepcopy

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
        self.v_max = int(v_max)
        self.car_id = car_id
        self.sche_time = int(sche_time)
        self.real_time = int(sche_time)  # 小车实际出发时间

        # 动态属性
        self.path = list([self.loc])  # 记录经过的路径
        self.v = self.v_max  # 当前小车速度
        self.lane_left = 0  # 小车距离车道末端的距离

        self.road_id = None # 小车所处的道路id
        self.lane_dis = 0  # 小车在当前车道上的位置
        self.access_dis = 0  # 小车在当前车道的可行驶距离
        self.next_car = self  # 双向循环链表，小车前方车辆
        self.behind_car = self  # 双向循环链表，小车后方车辆
        self.stat = 'wait'  # 标志小车在某个时间片的状态

        self.graph = None
        self.before_cross_id = int(loc) # 小车之前所在路口
        self.next_cross_id = None  # 小车在下一个路口会选择道路, None表示不出路口

    def __str__(self):
        return """ car_id:{}, stat:{}, next_cross_id:{}, car_v:{}, lane_dis:{}, loc:{}, lane_left:{}, access_dis:{}, road_id:{}
        """.format(self.car_id, self.stat, self.next_cross_id, self.v, self.lane_dis, self.loc, self.lane_left, self.access_dis, self.road_id)

    @property
    def has_reached(self):
        """
        是否到达目的地
        """
        return True if self.loc == self else False

    def update_stat(self):
        """
        运动一个时刻，改变当前小车状态
        调度顺序：从出口处向入口处调度，总共有四种情况：
        1.前方无阻挡车辆，且不出路口，则运行至终止位置，小车状态标记为：终止
        2.前方无阻挡车辆，需要出路口，则将小车状态标记为：等待行驶
        3.前方有阻挡车辆，阻挡车辆的状态为终止状态，则将小车行驶至阻挡车辆后面，将小车状态标记为：终止
        4.前方有阻挡车辆，阻挡车辆的状态为待行驶状态，则将小车状态标志为：等待行驶
        :return:
        """
        can_run_a_moment = self.access_dis >= self.v * 1
        if self.next_car.car_id == self.car_id:
            if can_run_a_moment:
                self.stat = 'finial'  # 1
                self.lane_dis += self.v
                self.lane_left -= self.v
                self.access_dis -= self.v
                if self.behind_car.car_id != self.car_id :
                    self.behind_car.access_dis += self.v
            else:
                # 即将出路口
                self.stat = 'wait'  # 2
                self.update_route()
        else:
            if can_run_a_moment:
                self.stat = 'finial'  # 1
                self.lane_dis += self.v
                self.access_dis -= self.v
                self.lane_left -= self.v
                if self.behind_car.car_id != self.car_id:
                    self.behind_car.access_dis += self.v

            elif self.next_car.stat == 'finial':  # 3
                self.stat = 'finial'
                next_lane_dis = self.next_car.lane_dis - 1
                delta_dis = next_lane_dis - self.lane_dis
                self.lane_dis = next_lane_dis
                self.lane_left -= delta_dis
                self.access_dis = 0
                if self.behind_car.car_id != self.car_id:
                    self.behind_car.access_dis += delta_dis
            else:
                self.stat = 'wait'  # 4

    def run_to_edge(self):
        """将小车开至车道边缘, 并调度同一条道路之后的小车"""
        car = self
        behind_car = self.behind_car
        while True:
            self.stat = 'finial'
            car.lane_dis += car.access_dis
            car.access_dis = 0
            if behind_car.stat == 'finial' or behind_car.stat is None:
                break
            car = behind_car
            behind_car = car.behind_car

    def update_route(self):
        """
        根据动态图,更新下一条经过的道路
        """
        path = nx.dijkstra_path(self.graph, source=self.loc, target=self.dest, weight='weight')
        if len(path) != 1:
            self.next_cross_id = path[1]
            self.path.append(self.next_cross_id)

    def run_out_current_road(self):
        """
        小车进入其他道路，需要从双向循环链表中删除当前小车
        后面的小车仍处于代行驶状态的小车继续行驶
        :return:
        """
        if self.behind_car.car_id == self.car_id:
            return

        # 更改后面小车状态，准备开始调度后续待行驶小车
        self.behind_car.access_dis += self.access_dis + 1
        self.behind_car.next_car = self.next_car
        self.next_car.behind_car = self.behind_car

        # 遍历双向循环链表，调度后续处于等待行驶的小车
        self.behind_car.update_stat()
        self.behind_car.schedule_behind_car()

    def schedule_behind_car(self):
        """调度当前小车后面的所有小车"""

        # 遍历双向循环链表，调度后续处于等待行驶的小车
        head_car_id = self.car_id
        current_car = self.behind_car
        while current_car.car_id != head_car_id:
            if current_car.stat == 'finial':
                break
            current_car.update_stat()
            current_car = current_car.behind_car