# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""
from math import ceil


class Road():
    def __init__(self, roud_id, length, v_limit, lane_num, cross_1, cross_2, two_way):

        self.v_limit = int(v_limit)
        self.len = int(length)
        self.cross_1 = int(cross_1)
        self.cross_2 = int(cross_2)
        self.road_id = int(roud_id)
        self.lane_num = int(lane_num)
        self.two_way = True if int(two_way) == 1 else False

        self.graph = None

        self.di_roads = list()
        self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))
        if self.two_way:
            self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))

    def run_moment(self):

        # self.update_graph()
        for di_road in self.di_roads:
            di_road.run()

    def update_graph(self):

        self.graph[self.cross_1][self.cross_2]['weight'] = self.di_roads[0].di_rweight_in_graph
        if self.two_way:
            self.graph[self.cross_2][self.cross_1]['weight'] = self.di_roads[1].di_rweight_in_graph

    def push_a_car(self, car, cross_id, from_garage=False):

        di_road = self.get_di_road(cross_id, 'import')


        run_dist = min(self.v_limit, car.v_max) - car.lane_left
        if run_dist <= 0:
            return False, 'road limit'

        is_success, info = di_road.push(car, run_dist, from_garage=from_garage)
        if is_success:
            car.stat = 'finial'
            car.road_id = self.road_id
            car.next_cross_id = None
            car.lane_left = self.len - run_dist
            car.v = min(car.v_max, self.v_limit)
            car.before_cross_id = car.loc
            car.loc = self.cross_2 if cross_id == self.cross_1 else self.cross_1
        return is_success, info
    def check_a_car(self, car, cross_id):
        di_road = self.get_di_road(cross_id, 'import')
        run_dist = min(self.v_limit, car.v_max) - car.lane_left
        if run_dist<=0:
            return False
        else:
            may_dead_lock = di_road.check(car, run_dist)
            return may_dead_lock

    def pull_a_car(self, car, cross_id, is_arrived=False):
        """
        :param car:
        :param cross_id:
        :return:
        """
        di_road = self.get_di_road(cross_id, 'export')
        di_road.pull(car, is_arrived=is_arrived)

    def get_di_road(self, cross_id, direct='export'):

        if direct == 'export':
            if cross_id == self.cross_2:
                return self.di_roads[0]
            else:
                if self.two_way:
                    return self.di_roads[1]
                return None
        else:
            if cross_id == self.cross_1:
                return self.di_roads[0]
            else:
                if self.two_way:
                    return self.di_roads[1]
                return None

    def weight_in_graph(self, cross_id):
        if cross_id == self.cross_1:
            return self.di_roads[0].di_rweight_in_graph
        else:
            return self.di_roads[1].di_rweight_in_graph

    def __str__(self):
        return 'cross_1:{}, cross_2:{}, two_way:{}'.format(self.cross_1, self.cross_2, self.two_way)


class DiRoad():

    def __init__(self, lane_num, lane_len, v_max):

        self.car_num = 0
        self.lane_len = lane_len
        self.lane_num = lane_num
        self.highest_prior_cars = [None for _ in range(self.lane_num)]
        self.v_max = v_max

    def pull(self, car, is_arrived=False):
        self.car_num -= 1

        idx = self.highest_prior_cars.index(car)
        new_hp_car = car.behind_car if car.behind_car.car_id != car.car_id else None
        if new_hp_car is not None:
            new_hp_car.is_head = True
        self.highest_prior_cars[idx] = new_hp_car

        if is_arrived:
            return

        next_road_hp_car = car
        while next_road_hp_car.next_car.car_id != car.car_id:
            next_road_hp_car = next_road_hp_car.next_car
        car.behind_car = next_road_hp_car

    def push(self, car, run_dist, from_garage=False):

        lane_mark, last_car, _hp_car = 0, None, None
        is_success, info = False, 'road limit'
        for lane_id, hp_car in enumerate(self.highest_prior_cars):
            if hp_car is None:
                lane_mark = lane_id
                is_success = True
                info = 'suceess'
                _hp_car = None
                break
            _hp_car = hp_car
            last_car = hp_car.next_car
            if run_dist <= last_car.lane_dis:
                lane_mark = lane_id
                is_success = True
                info = 'suceess'
                break
            else:
                if last_car.stat == 'wait':
                    is_success = False
                    info = 'other'
                    break

        if not is_success:
            return is_success, info

        if not from_garage:
            car.run_out_current_road()

        car.lane_id = lane_mark
        car.lane_dis = run_dist - 1
        if _hp_car is None:
            car.access_dis = self.lane_len - run_dist
            car.next_car = car
            _hp_car = car
        else:
            car.access_dis = _hp_car.next_car.lane_dis - car.lane_dis - 1
            car.next_car = last_car
            _hp_car.next_car = car
            last_car.behind_car = car
            if from_garage:
                car.behind_car = _hp_car

        self.car_num += 1

        _hp_car.is_head = True
        _hp_car.next_car.is_head = False if _hp_car.next_car.car_id != _hp_car.car_id else True
        self.highest_prior_cars[lane_mark] = _hp_car
        return is_success, info
    def check(self, car, run_dist):
        will_dead_lock = False
        last_car, _hp_car = None, None
        for lane_id, hp_car in enumerate(self.highest_prior_cars):
            if hp_car is None:
                will_dead_lock = False
                _hp_car = None
                break
            _hp_car = hp_car
            last_car = hp_car.next_car
            if run_dist <= last_car.lane_dis:
                will_dead_lock = False
                break
            else:
                if last_car.stat == 'wait':
                    will_dead_lock = True
                    break
        return will_dead_lock


    def run(self):
        for hp_car in self.highest_prior_cars:
            if hp_car is None:
                continue

            hp_car.stat = 'wait'
            header_id = hp_car.car_id
            current_car = hp_car.behind_car
            while current_car.car_id != header_id:
                current_car.stat = 'wait'
                current_car = current_car.behind_car

            hp_car.update_stat()
            hp_car.schedule_behind_car()

    @property
    def scheduler_queue(self):

        sche_q = list()
        lane_ls = [(idx, car) for idx, car in enumerate(self.highest_prior_cars)]
        header_car_id = [(idx, None) if car is None else (idx, car.car_id) for idx, car in lane_ls]

        while sum(map(lambda x: 1 if x[1] is not None else 0, lane_ls)) != 0:
            not_none = filter(lambda x: x[1] is not None, lane_ls)
            idx, car = min(not_none, key=lambda x: (ceil(x[1].lane_left / x[1].v), x[0]))
            if car.stat == 'finial':
                lane_ls[idx] = (idx, None)
            elif car.behind_car.car_id == header_car_id[idx][1]:
                sche_q.append(car)
                lane_ls[idx] = (idx, None)
            else:
                sche_q.append(car)
                lane_ls[idx] = (idx, car.behind_car)

        return sche_q

    # @property
    # def scheduler_queue_test(self):
    #     sche_q = list()
    #     lane_ls,header_car_id,consume = list(),list(),list()
    #     offset = 0
    #     for idx, car in enumerate(self.highest_prior_cars):
    #         if car is None:
    #             offset += 1
    #             continue
    #         new_idx = idx - offset
    #         lane_ls.append(new_idx)
    #         header_car_id.append((new_idx, car.car_id))
    #         consume.append((new_idx, ceil(car.lane_left / car.v), car))
    #
    #     while len(lane_ls) != 0:
    #         idx, _, car = min(consume, key=lambda x: (x[1], x[0]))
    #         if car.stat == 'finial':
    #             consume[idx] = (idx, 1000, None)
    #             lane_ls.pop()
    #         elif car.behind_car.car_id == header_car_id[idx][1]:
    #             sche_q.append(car)
    #             consume[idx] = (idx, 1000, None)
    #             lane_ls.pop()
    #         else:
    #             sche_q.append(car)
    #             next_car = car.behind_car
    #             consume[idx] = (idx, ceil(next_car.lane_left / next_car.v), next_car)
    #
    #     return sche_q
    @property
    def scheduler_queue_test(self):
        """优化后的函数"""
        sche_q = list()
        for lane_id, car in enumerate(self.highest_prior_cars):
            if car is None:
                continue
            if car.stat == 'finial':
                continue
            sche_q.append((car, lane_id))
            behind_car = car.behind_car
            head_id = car.car_id
            while behind_car.car_id != head_id:
                sche_q.append((behind_car, lane_id))
                behind_car = behind_car.behind_car
        sche_q.sort(key=lambda x: (x[0].lane_left, x[1]))
        sche_q = list(map(lambda x: x[0], sche_q))
        return sche_q

    @property
    def di_rweight_in_graph(self):

        return self.car_num / (self.lane_len * self.lane_num)*0.92 +  self.lane_len/100* 0.08 # +self.lane_len/self.v_max
