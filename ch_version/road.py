# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""
from math import ceil
import time


class Road():
    def __init__(self, roud_id, length, v_limit, lane_num, cross_1, cross_2, two_way):
        """
        :param roud_id: 道路唯一标识
        :param length: 道路长度
        :param v: 道路最高限速
        :param lane_num: 道路的单向车道数目
        :param cross_1: 与道路连通的交叉口 1，单向道路中也表示起始点
        :param corss_2: 与道路连通的交叉口 2，单向道路中也表示终止点
        :param two_way: 道路是否为双向道路
        """
        # 固定属性
        self.v_limit = int(v_limit)
        self.len = int(length)
        self.cross_1 = int(cross_1)
        self.cross_2 = int(cross_2)
        self.road_id = int(roud_id)
        self.lane_num = int(lane_num)
        self.two_way = True if int(two_way) == 1 else False

        # 全局动态图
        self.graph = None

        # 存储单向道路信息
        self.di_roads = list()
        self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))
        if self.two_way:
            self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))

    def run_moment(self):
        """
        运动一个时刻，改变所有道路上的小车状态
        """
        self.update_graph()
        for di_road in self.di_roads:
            di_road.run()

    def update_graph(self):
        """
        更新全局动态图
        :return:
        """
        self.graph[self.cross_1][self.cross_2]['weight'] = self.di_roads[0].di_rweight_in_graph
        if self.two_way:
            self.graph[self.cross_2][self.cross_1]['weight'] = self.di_roads[1].di_rweight_in_graph
        # self.graph[self.cross_1][self.cross_2]['weight'] = 1
        # if self.two_way:
        #     self.graph[self.cross_2][self.cross_1]['weight'] = 1

    def push_a_car(self, car, cross_id, from_garage=False):
        """
        针对需要进入的车， 改变其道路相关属性
        调用该函数时，小车一定可以进入该道路
        :param car:
         :return: True or False, info {'road limit', 'other'}
        """
        di_road = self.get_di_road(cross_id, 'import')

        # 小车若进入该道路，则需要行驶的距离
        # 若需要行驶的距离小于0，则将小车行驶至车道路口，等待下次进入该路口
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

    def pull_a_car(self, car, cross_id, is_arrived=False):
        """
        :param car:
        :param cross_id:
        :return:
        """
        di_road = self.get_di_road(cross_id, 'export')
        di_road.pull(car, is_arrived=is_arrived)

    def get_di_road(self, cross_id, direct='export'):
        """
        获取单向道路信息
        direct=='export', cross_id 为单向道路的出口
        direct=='import', cross_id 为单向道路的入口
        :return:
        """
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


class DiRoad():
    """
    单个方向道路类
    """

    def __init__(self, lane_num, lane_len, v_max):
        """
        :param lane_num:  车道数量
        :param v_max:  车道最高限速
        """
        self.car_num = 0 # 该单向道路上的小车数量
        self.lane_len = lane_len
        self.lane_num = lane_num
        self.highest_prior_cars = [None for _ in range(self.lane_num)]  # 存放每条车道优先级最高的车, 每个元素包含一个双向循环链表
        self.v_max = v_max

    def pull(self, car, is_arrived=False):
        self.car_num -= 1
        # 小车即将行驶进入下一个路口，这里调整当前道路优先级最高的车辆
        idx = self.highest_prior_cars.index(car)
        new_hp_car = car.behind_car if car.behind_car.car_id != car.car_id else None
        if new_hp_car is not None:
            new_hp_car.is_head = True
        self.highest_prior_cars[idx] = new_hp_car

        if is_arrived:
            return

        # 封闭下一条道路的双向循环链表
        next_road_hp_car = car
        while next_road_hp_car.next_car.car_id != car.car_id:
            next_road_hp_car = next_road_hp_car.next_car
        car.behind_car = next_road_hp_car

    def push(self, car, run_dist, from_garage=False):
        """
         判断小车是否可进入，若可进入则更新小车状态
         若不可进入，则返回失败信息
        :param car: 需要进入的小车
        :param run_dist: 进入当前道路需要行驶的最小距离
        :return: True or False, info
        """
        lane_mark, last_car, _hp_car = 0, None, None
        is_success, info = False, 'road limit'
        for lane_id, hp_car in enumerate(self.highest_prior_cars):
            if hp_car is None:  # 讲道理，车单位时间内，应该不会直接通过整个路段
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
        if _hp_car is None:  # 该车道没有车行驶
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

        self.car_num +=1
        # 确定优先级最高的车辆 is_head = True 后来的车辆 is_head = False
        _hp_car.is_head = True
        _hp_car.next_car.is_head = False if _hp_car.next_car.car_id != _hp_car.car_id else True
        self.highest_prior_cars[lane_mark] = _hp_car
        return is_success, info

    def run(self):
        # 调度每一个车道中的小车
        for hp_car in self.highest_prior_cars:
            if hp_car is None:
                continue

            # 将每一辆小车标记为 wait 状态
            hp_car.stat = 'wait'
            header_id = hp_car.car_id
            current_car = hp_car.behind_car
            while current_car.car_id != header_id:
                current_car.stat = 'wait'
                current_car = current_car.behind_car

            if hp_car.car_id == 10951:
                print('在原路直行：', hp_car)

            # 开始调度
            hp_car.update_stat()
            hp_car.schedule_behind_car()

            current_car = hp_car.next_car
            # if hp_car.car_id == 10951:
            #     print('在原路直行：', hp_car)
            while current_car.car_id != hp_car.car_id:
                if current_car.car_id == 10951:
                    print('在原路直行：', current_car)
                current_car = current_car.next_car

    @property
    def scheduler_queue_test(self):
        """
        按照优先级生成该车道调度序列，优先级生成策略：
        从每一个车道拿出优先级最高的小车进行优先级排序
        最快到达路口的则放入调度队列，从原车道继续拿出最高优先级的小车
        继续与其他车道优先级最高的小车进行评比，直到所有车道进入调度序列
        :return:
        """
        sche_q = list()
        lane_ls = [(idx, car) for idx, car in enumerate(self.highest_prior_cars)]
        header_car_id = [(idx, None) if car is None else (idx, car.car_id) for idx, car in lane_ls]

        while sum(map(lambda x: 1 if x[1] is not None else 0, lane_ls)) != 0:
            # 速度最快的优先级最高，若同一时刻到达，则车道编号小的先到达
            not_none = filter(lambda x: x[1] is not None, lane_ls)
            idx, car = min(not_none, key=lambda x: (ceil(x[1].lane_left / x[1].v), x[0]))
            if car.stat == 'finial':
                lane_ls[idx] = (idx, None)
            elif car.behind_car.car_id == header_car_id[idx][1]:  # 没有小车排在该小车之后
                sche_q.append(car)
                lane_ls[idx] = (idx, None)
            else:
                sche_q.append(car)
                lane_ls[idx] = (idx, car.behind_car)

        return sche_q

    @property
    def di_rweight_in_graph(self):
        """
        该条道路，最后一辆车的行驶均速
        用于计算图中边的权重
        :return:
        """
        # wait_car_num = 0
        # for car in self.highest_prior_cars:
        #     if car is None:
        #         continue
        #     if car.stat == 'wait':
        #         wait_car_num += 1
        #     current_car = car.behind_car
        #     while current_car.car_id != car.car_id:
        #         if current_car.stat == 'wait':
        #             wait_car_num +=1
        #         current_car = current_car.behind_car

        #return self.lane_len
        #return wait_car_num
        return self.car_num
