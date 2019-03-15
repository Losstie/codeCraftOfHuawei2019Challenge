# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""
from math import ceil


class Road():
    def __init__(self, roud_id, length, v, lane_num, cross_1, cross_2, two_way):
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
        self.v = v
        self.len = int(length)
        self.cross_1 = int(cross_1)
        self.cross_2 = int(cross_2)
        self.road_id = int(roud_id)
        self.lane_num = int(lane_num)
        self.two_way = True if int(two_way) == 1 else False
        self.num_moment = 0  # 当前所处时刻

        # 初始化车道对象, cross_id -> di_lane, 对应出口为cross_id的所有车道
        self.di_lanes_dict = dict()
        self.di_lanes_dict[self.cross_2] = DiLane(self.road_id, lane_num, self.len, v)
        if self.two_way:
            self.di_lanes_dict[self.cross_1] = DiLane(self.road_id, lane_num, self.len, v)

    def run_moment(self, graph):
        """
        运动一个时刻，改变所有道路上的小车状态
        """
        for lanes in self.di_lanes_dict.values():
            lanes.run(graph)


class DiLane():
    """
    单个方向车道类
    """

    def __init__(self, road_id, lane_num, lane_len, v_max):
        """
        :param lane_num:  车道数量
        :param v_max:  车道最高限速
        """
        self.road_id = road_id
        self.lane_len = lane_len
        self.lanes = [list() for _ in lane_num]  # (priority, car)
        self.v_max = v_max

        self.driveable_lane_id = 0  # 当前可行的车道id
        self.driveable_lane_dis = 0  # 当前可行车道上，可行驶的距离
        self.priority = 0  # 该道路走最后一辆小车的优先级

    def push_a_car(self, car):
        """ 按照优先级顺序，将一辆小车放入车道中, 并且更新小车信息 """
        car.stat = 'finial'
        driveable_lane = self.lanes[self.driveable_lane_id]

        car.v = min(car.v_max, self.v_max)
        car.road_id = self.road_id
        car.lane_id = self.driveable_lane_id
        car.lane_dis = self.driveable_lane_dis - 1
        car.next_car = None if len(driveable_lane) == 0 else driveable_lane[0]
        car.lane_left = self.lane_len if car.next_car is None else car.next_car.lane_dis - (car.lane_dis + 1)

        car.behind_car = None
        car.next_road_id = None
        car.next_cross_id = None
        driveable_lane.insert(0, car)

    def pull_a_car(self, car):
        """ 选择一辆车，将一辆小车从车道中拿出，并更新身后小车信息 """
        car.behind_car.lane_left += car.lane_left + 1
        car.behind_car.next_car = None
        self.lanes[car.lane_id].pop(-1)

    def accessable(self, car):
        """
        判断小车是否可进入，并更新：
        self.driveable_lane_id， self.driveable_lane_dis
        :param car: 需要进入的小车
        :return: True or False, info
        """
        v2 = min(car.v, self.v_max)
        for idx, lane in enumerate(self.lanes):
            last_car = lane[0]
            driveable_dis = self.lane_len if len(lane) == 0 else last_car.lane_dis
            s2 = v2 - car.lane_dis
            if s2 <= 0 or s2 > driveable_dis:
                if last_car.stat == 'wait':
                    return False, 'cart wait'
            self.driveable_lane_id = idx
            self.driveable_lane_dis = s2
            return True, 'access'
        return False, 'road limit'

    def current_v_max(self):
        """
        第一条可行驶车道上，最后一辆车的速度
        用于计算图中边的权重
        :return:
        """
        pass

    def run(self, graph):
        for car in [c for lane in self.lanes for c in reversed(lane)]:
            car.stat = 'wait'  # 将所有小车标记为待行驶状态
            car.updata_stat(graph)

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
        # [(idx, lane)], idx 为lane 中参与优先级评选小车的下标
        lanes_not_empty = list(map(lambda x: (len(x) - 1, x), filter(lambda x: len(x) != 0, self.lanes)))
        time_consume = [(idx, ceil(l[car_idx].lane_left / l[car_idx].v), l[car_idx])
                        for idx, car_idx, l in enumerate(lanes_not_empty)]
        compared_car_num = len(lanes_not_empty)
        while compared_car_num != 0:
            lane_idx, tc, car = min(time_consume, key=lambda x: (x[1], x[0]))
            # 更新车道中参与优先级评比的小车信息
            if lanes_not_empty[lane_idx][0] -1 < 0:
                compared_car_num -= 1
                time_consume[lane_idx][1] = 100
            else:
                lanes_not_empty[lane_idx][0] -= 1
                car_idx, l = lanes_not_empty[lane_idx]
                updaed_lan_left = l[car_idx].lane_left + car.lane_left +1
                time_consume[lane_idx] = (lane_idx, ceil(updaed_lan_left/ l[car_idx].v), l[car_idx])
            sche_q.append(car)
        return sche_q
