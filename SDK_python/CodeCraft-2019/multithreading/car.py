# -*- coding: utf-8 -*-
"""
Created on 2019/3/14

@author: Evan Chen
"""

import nx

class Car():
    def __init__(self, car_id, loc, dest, v_max, sche_time):

        self.loc = int(loc)
        self.dest = int(dest)
        self.v_max = int(v_max)
        self.car_id = int(car_id)
        self.sche_time = int(sche_time)
        self.real_time = int(sche_time)


        self.path = list([self.loc])
        self.v = self.v_max
        self.lane_left = 0

        self.is_head = True
        self.lane_id = 0
        self.road_id = None
        self.lane_dis = 0
        self.access_dis = 0
        self.next_car = self
        self.behind_car = self
        self.stat = 'wait'
        self.signal = None

        self.arrived = False
        self.graph = None
        self.before_cross_id = int(loc)
        self.next_cross_id = None

    def __str__(self):
        return """ car_id:{}, loc:{}, road_id:{}, lane_id:{}, is_header:{}, stat:{},befor_cross_id:{}, next_cross_id:{}, car_v:{}, lane_dis:{}, access_dis:{}, lane_left:{}, next_car_id:{}, behind_car_id:{}, arrived:{}
        """.format(self.car_id, self.loc, self.road_id, self.lane_id, self.is_head, self.stat, self.before_cross_id,
                   self.next_cross_id,
                   self.v, self.lane_dis,
                   self.access_dis, self.lane_left, self.next_car.car_id, self.behind_car.car_id, self.arrived)

    @property
    def has_reached(self):

        return True if self.loc == self else False

    def update_stat(self):

        can_run_a_moment = self.access_dis >= self.v * 1
        if can_run_a_moment:  # 1
            self.stat = 'finial'
            self.lane_dis += self.v
            self.lane_left -= self.v
            self.access_dis -= self.v

            if self.behind_car.is_head is not True:
                self.behind_car.access_dis += self.v
        else:
            if self.is_head is True:
                self.stat = 'wait'  # 2
                if self.next_cross_id is None:
                    self.update_route()
            else:
                if self.next_car.stat == 'finial':  # 3
                    self.stat = 'finial'
                else:
                    self.stat = 'wait'  # 4

    def run_to_edge_test(self):
        self.stat = 'finial'
        self.path.pop(-1)
        self.next_cross_id = None

        if self.behind_car.car_id != self.car_id:
            self.behind_car.access_dis += self.access_dis


            self.behind_car.update_stat()
            self.behind_car.schedule_behind_car()

        self.lane_dis += self.lane_left
        self.access_dis = 0
        self.lane_left = 0

    def update_route(self):

        if self.before_cross_id != self.loc and (self.loc, self.before_cross_id) in self.graph.in_edges:
            w = self.graph[self.loc][self.before_cross_id]['weight']
            self.graph[self.loc][self.before_cross_id]['weight'] = 1000
        path = nx.dijkstra_path(self.graph, source=self.loc, target=self.dest, weight='weight')
        if self.before_cross_id != self.loc and (self.loc, self.before_cross_id) in self.graph.in_edges:
            self.graph[self.loc][self.before_cross_id]['weight'] = w

        if len(path) != 1:
            self.next_cross_id = path[1]
            self.path.append(self.next_cross_id)
        else:
            self.next_cross_id = path[0]
    # def update_route(self):
    #
    #     cross = self.cross_dict[self.loc]
    #     candidate_cross = set()
    #     for road in cross.roads_dict.values():
    #         if self.loc == road.cross_1:
    #             candidate_cross.add(road.cross_2)
    #         if self.loc == road.cross_2 and road.two_way:
    #             candidate_cross.add(road.cross_1)
    #     forbid = {self.next_cross_id, self.before_cross_id}
    #     candidate_cross -= forbid
    #     candidate_cross = list(candidate_cross)
    #     s_cross_id = None
    #     if len(candidate_cross) != 0:
    #         choose = [(self.before_cross_id,c) for c in candidate_cross]
    #         dir_ls = list(map(lambda x: cross.direct_dict[x] if x is not None else 'None',choose))
    #         if "straight" in dir_ls:
    #             s_cross_id = candidate_cross[dir_ls.index("straight")]
    #     if s_cross_id is not None:
    #         w_s = self.graph[self.loc][s_cross_id]["weight"]
    #         self.graph[self.loc][s_cross_id]["weight"] = w_s * 0.8
    #
    #     if self.before_cross_id != self.loc and (self.loc, self.before_cross_id) in self.graph.in_edges:
    #         w = self.graph[self.loc][self.before_cross_id]['weight']
    #         self.graph[self.loc][self.before_cross_id]['weight'] = 1000
    #
    #     path = nx.dijkstra_path(self.graph, source=self.loc, target=self.dest, weight='weight')
    #     if self.before_cross_id != self.loc and (self.loc, self.before_cross_id) in self.graph.in_edges:
    #         self.graph[self.loc][self.before_cross_id]['weight'] = w
    #     if s_cross_id is not None:
    #         self.graph[self.loc][s_cross_id]["weight"] = w_s
    #
    #     if len(path) != 1:
    #         self.next_cross_id = path[1]
    #         self.path.append(self.next_cross_id)
    #     else:
    #         self.next_cross_id = path[0]

    def run_out_current_road(self):

        if self.behind_car.car_id == self.car_id:
            return

        self.behind_car.is_head = True
        self.behind_car.access_dis += self.access_dis + 1
        self.behind_car.next_car = self.next_car
        self.next_car.behind_car = self.behind_car

        self.behind_car.update_stat()
        self.behind_car.schedule_behind_car()

    def schedule_behind_car(self):

        head_car_id = self.car_id
        current_car = self.behind_car
        while current_car.car_id != head_car_id:
            if current_car.stat == 'finial':
                break
            current_car.update_stat()
            current_car = current_car.behind_car
