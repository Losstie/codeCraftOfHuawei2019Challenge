# -*- coding: utf-8 -*-
"""
Created on 2019/3/13 1:55

@author: Evan Chen
"""
from functools import reduce
import time

import random


class Scheduler():


    def __init__(self, graph, cars, roads, crosses):
        self.moment = 0
        self.cars = cars
        self.roads = list(roads)
        self.crosses = list(sorted(crosses, key=lambda x: x.id))

        self.car_dict = dict([(car.car_id, car) for car in self.cars])
        self.cross_dict = dict([(cross.id, cross) for cross in self.crosses])

        self.graph = graph
        self.cars_in_traffic = reduce(lambda y, z: y + z, map(lambda x: len(x.magic_garage[0]), self.crosses))


    def run(self):

        s = time.time()

        # slow star
        per_cwnd = 1
        ssh = 3
        control_nums_departures = len(self.crosses)//2.5
        occur_lock = False
        occur_lock_time = 0
        first_time = True
        inter_val = 3
        while self.cars_in_traffic != 0:
            self.moment += 1


            for road in self.roads:
                road.run_moment()

            pre_conflict_crosses = list()
            has_car_in_wait = True
            while has_car_in_wait:
                status = [cross.run_a_time(self.moment) for cross in self.crosses]
                car_arrived_cross = reduce(lambda z, y: z + y, map(lambda x: x[1], status))
                self.cars_in_traffic -= car_arrived_cross
                has_car_in_wait = reduce(lambda z, y: z or y, map(lambda x: x[0], status))
                conflict_crosses = list(map(lambda x: x[0], filter(lambda x: x[1][0] is True, enumerate(status))))

                if (self.moment-occur_lock_time)>inter_val and not first_time:
                    occur_lock = False
                    if per_cwnd<ssh:
                        per_cwnd += 1

                if self.is_lock(pre_conflict_crosses, conflict_crosses):
                    car_id_ls = reduce(lambda x, y: x + y, map(lambda x: x[2], status))
                    self.re_route_path(car_id_ls)
                    per_cwnd = 0
                    occur_lock = True
                    occur_lock_time = self.moment


                pre_conflict_crosses = [_ for _ in conflict_crosses]


            self.update_graph()

            nums_of_drive_out_garage = 0
            if not occur_lock:
                for cross in self.crosses:
                    if nums_of_drive_out_garage >= control_nums_departures:
                        break
                    nums_of_drive_out_garage += cross.run_car_in_magic_garage_test(self.moment,per_cwnd)
            if first_time:
                first_time = False

            # self.update_graph()

        # self.get_path()


    def update_graph(self):
        for road in self.roads:
            self.graph[road.cross_1][road.cross_2]['weight'] = road.weight_in_graph(road.cross_1)
            if road.two_way:
                self.graph[road.cross_2][road.cross_1]['weight'] = road.weight_in_graph(road.cross_2)

    def is_lock(self, pre, new):

        if len(pre) != len(new) or len(pre) == 0:
            return False

        for idx in range(len(pre)):
            if pre[idx] != new[idx]:
                return False
        return True

    def re_route_path(self, car_id_ls):

        for car_id in car_id_ls:
            c_car = self.car_dict[car_id]
            cross_id = c_car.loc
            cross = self.cross_dict[cross_id]

            candidate_cross = set()
            for road in cross.roads_dict.values():
                if cross_id == road.cross_1:
                    candidate_cross.add(road.cross_2)
                if cross_id == road.cross_2 and road.two_way:
                    candidate_cross.add(road.cross_1)

            forbid = {c_car.next_cross_id, c_car.before_cross_id}
            candidate_cross -= forbid
            if len(candidate_cross) == 0:
                continue

            c_car.path.pop(-1)
            candidate_cross_list = list(candidate_cross)
            random.seed(1024)
            visitedIndex = random.randint(0, len(candidate_cross_list) - 1)
            c_car.next_cross_id = candidate_cross_list.pop(visitedIndex)
            c_car.path.append(c_car.next_cross_id)


    def create_answer(self, path):
        road_dict = dict()
        for road in self.roads:
            road_dict[(road.cross_1, road.cross_2)] = road.road_id
            if road.two_way:
                road_dict[(road.cross_2, road.cross_1)] = road.road_id

        with open(path, 'w') as answer_file:
            for car in self.cars:
                paths = [str(road_dict[item]) for item in zip(car.path[:-1],car.path[1:])]
                ans_str = '({},{},{})\n'.format(str(car.car_id), str(car.real_time), ','.join(paths))
                answer_file.write(ans_str)
            answer_file.flush()

