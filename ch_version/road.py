# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""
from math import ceil


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

        # 存储单向道路信息
        self.di_roads = list()
        self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))
        if self.two_way:
            self.di_roads.append(DiRoad(self.lane_num, self.len, self.v_limit))

    def run_moment(self):
        """
        运动一个时刻，改变所有道路上的小车状态
        """
        for di_road in self.di_roads:
            di_road.run()

    def push_a_car(self, car, cross_id):
        """
        针对需要进入的车， 改变其道路相关属性
        调用该函数时，小车一定可以进入该道路
        :param car:
         :return: True or False, info {'road limit', 'other'}
        """
        di_road = self.get_di_road(cross_id, 'import')

        # 小车若进入该道路，则需要行驶的距离
        # 若需要行驶的距离小于0，则将小车行驶至车道路口，等待下次进入该路口
        run_dist = self.v_limit - car.access_dis
        if run_dist <= 0:
            return False, 'road limit'

        is_success, info = di_road.push(car, run_dist)
        if is_success:
            # car.loc = self.cross_1 if cross_id == self.cross_1 else self.cross_2
            car.stat = 'finial'
            car.next_cross_id = None
            car.lane_left = self.len - run_dist
            car.v = min(car.v_max, self.v_limit)
        return is_success, info

    def pull_a_car(self, car, cross_id):
        """
        :param car:
        :param cross_id:
        :return:
        """
        di_road = self.get_di_road(cross_id, 'export')
        di_road.pull(car)

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
        self.lane_len = lane_len
        self.lane_num = lane_num
        self.highest_prior_cars = [None for _ in range(self.lane_num)]  # 存放每条车道优先级最高的车, 每个元素包含一个双向循环链表
        self.v_max = v_max

    def pull(self, car):
        """
        将小车从该车道拿出
        :param car:
        :return:
        """
        # 更新当前车道优先级最高的车辆
        idx = self.highest_prior_cars.index(car)
        self.highest_prior_cars[idx] = car.behind_car

        # 封闭下一条道路的双向循环链表
        car_id = car.car_id
        current_car = car.next_car
        while current_car.car_id != car_id:
            current_car = current_car.next_car
        car.behind_car = current_car

    def push(self, car, run_dist):
        """
         判断小车是否可进入，若可进入则更新小车状态
         若不可进入，则返回失败信息
        :param car: 需要进入的小车
        :param run_dist: 进入当前道路需要行驶的最小距离
        :return: True or False, info
        """
        lane_mark, last_car = 0, None
        is_success, info = False, 'road limit'
        for lane_id, hp_car in enumerate(self.highest_prior_cars):
            if hp_car is None: # 讲道理，车单位时间内，应该不会直接通过整个路段
                lane_mark = lane_id
                is_success = True
                info = 'suceess'
                break
            last_car = hp_car.next_car
            if run_dist <= last_car.lane_dis:
                lane_mark = lane_id
                hp_car.next_car = car
                is_success = True
                last_car = hp_car
                info = 'suceess'
                break
            else:
                if last_car.stat == 'wait':
                    is_success = False
                    info = 'other'
                    break

        if not is_success:
            return is_success, info

        car.run_out_current_road()

        if last_car is None:
            car.access_dis = self.lane_len - run_dist
            last_car = car
        else:
            car.access_dis = car.next_car.lane_dis - car.lane_dis - 1

        car.lane_dis = run_dist - 1
        car.next_car = last_car
        hp_car = last_car.behind_car
        hp_car.next_car = car
        last_car.behind_car = car

        self.highest_prior_cars[lane_mark] = hp_car
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

            # 开始调度
            hp_car.update_stat()
            hp_car.schedule_behind_car()

    @property
    def scheduler_queue(self):
        """
        按照优先级生成该车道调度序列，优先级生成策略：
        从每一个车道拿出优先级最高的小车进行优先级排序
        最快到达路口的则放入调度队列，从原车道继续拿出最高优先级的小车
        继续与其他车道优先级最高的小车进行评比，直到所有车道进入调度序列
        :return:
        """
        sche_q = list()
        lane_ls = [(idx, car) for idx, car in enumerate(self.highest_prior_cars)]
        # print(self.highest_prior_cars)
        while sum(map(lambda x: 1 if not x[1] is None else 0, lane_ls)) != 0:
            # 速度最快的优先级最高，若同一时刻到达，则车道编号小的先到达
            not_none = filter(lambda x: not x[1] is None, lane_ls)
            idx, car = min(not_none, key=lambda x: (ceil(x[1].lane_left / x[1].v), x[0]))
            if car.stat == 'finial':
                lane_ls[idx] = (idx, None)
                continue

            lane_ls[idx] = (idx, car.next_car)
            sche_q.append(car)

            if car.next_car.car_id == car.car_id:
                lane_ls[idx] = (idx, None)
                continue

        # print('sche_q:', sche_q)
        if len(sche_q) !=0 :
            print( '' )
        return sche_q

    @property
    def di_rweight_in_graph(self):
        """
        该条道路，最后一辆车的行驶均速
        用于计算图中边的权重
        :return:
        """
        # all_v = sum([car.next_car.v for car in self.highest_prior_cars])
        # lane_num = len(self.highest_prior_cars)
        # return all_v / lane_num
        return self.lane_len