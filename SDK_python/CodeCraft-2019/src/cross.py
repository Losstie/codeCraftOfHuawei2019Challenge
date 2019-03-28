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

        has_wait_car, arrived_cars_num, conflict_car_ls = self.__run(all_queues_num, road_queues, current_moment)
        return has_wait_car, arrived_cars_num, conflict_car_ls

    def __run(self, all_queues_num, road_queues, current_moment):
        arrived_cars_num = 0
        finished_lane_ls = list()
        conflict_lane_ls = list()
        conflict_car_ls = list()

        first_order_car = [q[0] for _, q in road_queues]
        has_movable_car = True
        while has_movable_car:
            for idx, road_queue in enumerate(road_queues):
                road_id, queue = road_queue

                if idx in conflict_lane_ls + finished_lane_ls:
                    continue

                if len(queue) == 0:
                    finished_lane_ls.append(idx)
                    continue

                del_cars = list()
                for ix, car in enumerate(queue):
                    if car.stat == 'finial':
                        del_cars.append(car)
                        continue

                    if self.id == car.dest:
                        car.arrived = True

                        arrived_cars_num += 1
                        self.magic_garage[1].append(car)
                        del_cars.append(car)
                        first_order_car[idx] = None

                        car.run_out_current_road()
                        self.roads_dict[road_id].pull_a_car(car, self.id, is_arrived=True)
                        continue

                    first_order_car[idx] = car

                    if self.has_conflict(idx, first_order_car):
                        break
                    else:
                        # next_road = None
                        # next_cross = car.next_cross_id
                        # for road in self.roads_dict.values():
                        #     if next_cross in [road.cross_1, road.cross_2]:
                        #         next_road = road
                        next_road = self.next_road_dict[car.next_cross_id]
                        is_success, info = next_road.push_a_car(car, self.id)
                        if is_success:
                            del_cars.append(car)
                            self.roads_dict[road_id].pull_a_car(car, self.id)
                        elif info == 'road limit':
                            car.run_to_edge_test()
                            del_cars.append(car)
                        else:
                            conflict_car_ls.append(car.car_id)
                            conflict_lane_ls.append(idx)
                            first_order_car[idx] = None
                            break

                for car in del_cars:
                    queue.remove(car)

                if len(queue) == 0:
                    finished_lane_ls.append(idx)
                    first_order_car[idx] = None

            finished_lane_num = len(finished_lane_ls)
            conflict_lane_num = len(conflict_lane_ls)
            if finished_lane_num + conflict_lane_num == all_queues_num:
                has_movable_car = False
            else:
                has_movable_car = True

        has_wait_car = True if len(conflict_lane_ls) != 0 else False
        return has_wait_car, arrived_cars_num, conflict_car_ls

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
    def run_car_in_magic_garage(self, moment):

        _sum = 0
        wait_start_car = list()
        for car in self.magic_garage[0]:
            if car.sche_time <= moment:
                wait_start_car.append(car)
            else:
                break
        wait_start_car.sort(key=lambda x: x.car_id)

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
