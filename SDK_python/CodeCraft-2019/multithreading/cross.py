# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 涓婂崍10:19

@author: Evan Chen
"""
from utils import direct_relat_other, direct_relat_other_test


class Cross():

    def __init__(self, cross_id, road_1, road_2, road_3, road_4):

        self.id = int(cross_id)
        self.num_moment = 0

        roads = [road_1, road_2, road_3, road_4]
        road_not_none = filter(lambda x: x is not None, roads)
        road_sorted_not_none = sorted(road_not_none, key=lambda x: x.road_id)
        self.roads_dict = dict(map(lambda x: (x.road_id, x), road_sorted_not_none))

        self.direct_dict = direct_relat_other_test(self.id, enumerate(roads, 1))

        # next_cross_id --> next_road
        self.next_road_dict = self.init_next_road_dict()

        self.magic_garage = [list(), list()]

    def run_a_time(self, current_moment):

        export_road = list()
        for road in self.roads_dict.values():
            di_road = road.get_di_road(self.id, direct='export')
            if di_road is None:
                continue
            export_road.append((road.road_id, di_road))

        road_queues = list(
            filter(lambda x: len(x[1]) != 0, map(lambda x: (x[0], x[1].scheduler_queue_test), export_road)))
        all_queues_num = len(road_queues)

        if all_queues_num == 0:
            return False, 0, []

        has_wait_car, arrived_cars_num, conflict_car_ls = self.__run_test(all_queues_num, road_queues, current_moment)
        return has_wait_car, arrived_cars_num, conflict_car_ls

    def __run_test(self, all_queues_num, road_queues, current_moment):
        arrived_cars_num = 0
        conflict_car_ls = list()
        has_car_wait = False
        road_queues = list(filter(lambda x:len(x[1])!=0,road_queues))
        has_movable_car = True
        while has_movable_car:
            first_order_car = [q[0] for _, q in road_queues]
            _filter_finial_car = list(filter(lambda x:x.stat=='finial',first_order_car))
            if len(_filter_finial_car)!=0:
                for idx,car in enumerate(first_order_car):
                    if car.stat == 'finial':
                        road_queues[idx][1].remove(car)
                        # if the queue have no car
                        road_queues = list(filter(lambda x: len(x[1]) != 0, road_queues))
                        all_queues_num = len(road_queues)
                    else:
                        continue
            else:
                for car in first_order_car:
                    if car.dest == self.id:
                        continue
                    else:
                        next_road = self.next_road_dict[car.next_cross_id]
                        will_dead_lock = next_road.check_a_car(car, self.id)
                        if will_dead_lock:
                            conflict_car_ls.append(car.car_id)
                if len(conflict_car_ls) != 0:
                    return True,arrived_cars_num,conflict_car_ls
                else:
                    aim_cross = [car.next_cross_id for car in first_order_car]
                    dir_ls = list(map(lambda x: self.direct_dict[x] if x is not None else 'None',
                                      [(car.before_cross_id,
                                        car.next_cross_id) if car is not None and car.next_cross_id == a else None
                                       for car,a
                                       in zip(first_order_car,aim_cross)]))
                    def convert_to_int(x):
                        if x =='straight':
                            return 3
                        elif x== 'left':
                            return 2
                        elif x=='right':
                            return 1
                        else:
                            return 0
                    for i,c in enumerate(first_order_car):
                        c.signal = dir_ls[i]
                    first_order_car = sorted(first_order_car,key=convert_to_int,reverse=True)
                    will_drive_car = first_order_car.pop(0)
                    road_id = will_drive_car.road_id

                    if will_drive_car.dest == self.id:
                        arrived_cars_num += 1
                        for idx, queue in road_queues:
                            if idx == road_id:
                                queue.remove(will_drive_car)
                        road_queues = list(filter(lambda x:len(x[1])!=0,road_queues))
                        all_queues_num = len(road_queues)
                        self.magic_garage[1].append(car)
                        will_drive_car.run_out_current_road()
                        self.roads_dict[road_id].pull_a_car(will_drive_car, self.id, is_arrived=True)
                    else:
                        next_road = self.next_road_dict[will_drive_car.next_cross_id]
                        is_success, info = next_road.push_a_car(will_drive_car, self.id)
                        if is_success:
                            for idx, queue in road_queues:
                                if idx == road_id:
                                    queue.remove(will_drive_car)
                            road_queues = list(filter(lambda x:len(x[1])!=0,road_queues))
                            all_queues_num = len(road_queues)
                            self.roads_dict[road_id].pull_a_car(will_drive_car, self.id)
                        elif info == 'road limit':
                            will_drive_car.run_to_edge_test()
                            for idx, queue in road_queues:
                                if idx == road_id:
                                    queue.remove(will_drive_car)
                            road_queues = list(filter(lambda x:len(x[1])!=0,road_queues))
                            all_queues_num = len(road_queues)
            if all_queues_num == 0:
                has_movable_car = False
        return has_car_wait,arrived_cars_num,conflict_car_ls











    def has_conflict(self, idx, first_order_car):

        aim_cross = first_order_car[idx].next_cross_id
        dir_ls = list(map(lambda x: self.direct_dict[x] if x is not None else 'None',
                          [(car.before_cross_id,
                            car.next_cross_id) if car is not None and car.next_cross_id == aim_cross else None for car
                           in first_order_car]))

        aim_car_dir = dir_ls[idx]
        dir_ls.pop(idx)
        while 'None' in dir_ls: dir_ls.remove('None')

        if aim_car_dir == 'straight':
            return False
        elif 'straight' in dir_ls:
            return True
        elif aim_car_dir == 'left':
            return False
        elif 'left' in dir_ls:
            return True
        else:
            return False

    # def run_car_in_magic_garage(self, moment):

    #   _sum = 0
    #   for car in self.magic_garage[0]:
    #      if car.sche_time <= moment:
    #         if car.next_cross_id is None:
    #            car.update_route()

    #       next_road = self.next_road_dict[car.next_cross_id]
    #      is_success, info = next_road.push_a_car(car, self.id, from_garage=True)
    #     if is_success:
    #        car.real_time = moment
    #       self.magic_garage[0].remove(car)
    #       _sum += 1
    #  else:
    #     continue
    # else:
    #    continue
    # return _sum
    def run_car_in_magic_garage(self, moment,per_cwnd):

        _sum = 0
        wait_start_car = list()
        for car in self.magic_garage[0]:
            if car.sche_time <= moment and _sum<per_cwnd:
                wait_start_car.append(car)
                _sum+=1
            else:
                break
        wait_start_car.sort(key=lambda x: x.car_id)
        _sum = 0
        for car in wait_start_car:
            if car.next_cross_id is None:
                car.update_route()

            next_road = self.next_road_dict[car.next_cross_id]
            is_success, info = next_road.push_a_car(car, self.id, from_garage=True)
            if is_success:
                car.real_time = moment
                self.magic_garage[0].remove(car)
                _sum += 1
            else:
                continue
        return _sum
    def run_car_in_magic_garage_test(self, moment, per_cwnd):
        _sum = 0
        wait_start_car = list()
        if per_cwnd == 0:
            return _sum

        for car in self.magic_garage[0]:
            if car.sche_time <= moment:
                wait_start_car.append(car)
            else:
                break
        # wait_start_car.sort(key=lambda x: x.car_id)
        nums = len(wait_start_car)
        if nums == 0:
            return _sum
        wait_start_car.sort(key=lambda x: x.v_max,reverse=True)

        if nums >= per_cwnd:
            start_car = wait_start_car[:per_cwnd]
        else:
            start_car = wait_start_car

        start_car.sort(key=lambda x:x.car_id)

        for car in start_car:
            if car.next_cross_id is None:
                car.update_route()

            next_road = self.next_road_dict[car.next_cross_id]
            is_success, info = next_road.push_a_car(car, self.id, from_garage=True)
            if is_success:
                car.real_time = moment
                self.magic_garage[0].remove(car)
                _sum += 1
            else:
                continue
        return _sum

    def init_next_road_dict(self):
        """
        next_cross_id --> next_road
        :return:
        """
        next_road_dict = dict()
        for road in self.roads_dict.values():
            key = road.cross_2 if self.id == road.cross_1 else road.cross_1
            next_road_dict[key] = road
        return next_road_dict

    def __str__(self):
        return 'Commander at {}'.format(self.id)
