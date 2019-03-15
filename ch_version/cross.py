# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""
from utils import direct_relat_other


class Cross():
    """
    负责调度待行驶车辆
    """

    def __init__(self, cross_id, road_1, road_2, road_3, road_4):
        """
        :param cross_id: 路口唯一标识
        :param roud_1～4: Commander管理的四条道路实例对象, 若不存在道路，则为None
        """
        self.id = int(cross_id)
        self.num_moment = 0  # 当前所处时刻

        # 道路id升序调度
        roads = [road_1, road_2, road_3, road_4]
        road_not_none = filter(lambda x: x is not None, roads)
        road_sorted_not_none = sorted(road_not_none, key=lambda x: x.road_id)
        self.roads_dict = dict(map(lambda x: (x.road_id, x), road_sorted_not_none))

        # 道路行驶方向字典
        self.direct_dict = direct_relat_other(self.id, enumerate(roads, 1))

        # 神奇车库，未出发，已到达的车辆将会被放入
        self.magic_garage = [list(), list()]  # 待出行，已到达

    def push_into_garage(self, stat, *cars):
        if stat == 'active':
            # 待出发车辆仅会被初始化时放入
            self.magic_garage[0] = sorted(list(cars), key=lambda x: (x.sche_time, x.car_id))
        else:
            self.magic_garage[1] += list(cars)

    def run_a_time(self):
        """
        调度处于等待行驶状态的车辆，并且通过路口时符合交通规则
        每一个路口需要多次调度才可以运行一个时间片段
        :return: 1.当前路口是否存在未调度车辆：{True, False}  2.本次运行抵达该路口有多少辆
        """
        arrived_cars_num = 0
        # 完成全部调度的车道
        finished_lane_ls = list()
        # 无法调度的车道
        conflict_lane_ls = list()

        # 每条出口道路对应的调度序列
        export_lanes = [road.di_lanes_dict.get(self.id, None) for road in self.roads_dict.values()]  # 可能报错，存在单向道路
        lane_queues = list(filter(lambda x: len(x) != 0,
                                  [list(lane.scheduler_queue) if not lane is None else [] for lane in export_lanes]))
        lane_num = len(lane_queues)
        # 每一个出口道路对应的优先级最高的车辆
        first_order_car = [q[0] for q in lane_queues]

        has_movable_car = True  # 是否有可动的车辆
        while has_movable_car:
            for lane_idx, queue in enumerate(lane_queues):
                # 如果队列为空，则说明全部调度完毕
                if len(queue) == 0:
                    finished_lane_ls.append(lane_idx)
                    continue

                # 如果已经调度完成或者处于冲突状态，则不需要在调度
                if lane_idx in conflict_lane_ls + finished_lane_ls:
                    continue

                for car in queue:
                    if car.stat == 'finial':
                        queue.remove(car)
                        continue

                    # 到达目标路口
                    if self.id == car.dest:
                        # 将小车从车道中拿出, 更新 后方 车辆可行驶距离信息, 放入神奇车库
                        export_lanes[lane_idx].pull_a_car(car)
                        self.magic_garage[1].append(car)
                        arrived_cars_num += 1
                        queue.remove(car)  # 将小车从调度队列中移除
                        continue

                    # 小车直行
                    if car.next_cross_id is None:
                        car.update_stat()
                        queue.remove(car)  # 将小车从调度队列中移除
                        continue

                    # 不是调度下一个路口，而是调度发生冲突的那个路口 ！！！！！！
                    # 小车需要通过路口， 若存在冲突则调度下一条道路,
                    if self.has_conflict(lane_idx, first_order_car):
                        # 更新该车道，优先级最高车辆的信息
                        first_order_car[lane_idx] = car
                        break

                    # # 获取下一条道路信息
                    # next_road = self.roads_dict[car.next_road_id]
                    # next_cross = next_road.cross_1 if next_road.cross_1 != self.id else next_road.cross_2
                    # next_lane = next_road.di_lanes_dict[next_cross]

                    # 获取下一条道路信息
                    next_cross = car.next_cross_id
                    for road in self.roads_dict.values():
                        if next_cross in [road.cross_1, road.cross_2]:
                            next_lane = road.di_lanes_dict[next_cross]

                    # 若道路可进入
                    is_access, info = next_lane.accessable(car)
                    if is_access:
                        # 将小车从车道中拿出, 更新后方车辆可行驶距离信息,放入下一条车道
                        export_lanes[lane_idx].pull_a_car(car)
                        next_lane.push_a_car(car)

                        queue.remove(car)  # 将小车从调度队列中移除
                    elif info == 'road limit':
                        # 将小车行驶至路口，等待下一个时间片段调度
                        car.run_to_edge()
                        queue.remove(car)
                    else:
                        # 因为其他路口未被调度，或者发生死锁现象
                        # 导致车辆需要行驶的车道容量不足
                        # 由于该条车道优先级最高的车辆无法通行
                        # 导致同一车道其他车辆也无法通行，因此该车道不在参与当前调度
                        # 当前调度结束后，需要重新调度所有路口
                        conflict_lane_ls.append(lane_idx)

            # 路口出的车道是否处于 发生冲突 或 完成调度 的状态
            finished_lane_num = len(finished_lane_ls)
            conflict_lane_num = len(conflict_lane_ls)
            if finished_lane_num + conflict_lane_num == lane_num:
                has_movable_car = False
            else:
                has_movable_car = True

        has_wait_car = True if len(conflict_lane_ls) != 0 else False
        return has_wait_car, arrived_cars_num

    def has_conflict(self, idx, first_order_car):
        """
        通过路口时需要进行冲突检测，
        :param idx: 当前等待通过路口的小车在  first_order_car 中的下标
        :param first_order_car:  各个路口中优先级最高的车辆
        :return: True or False， True: 当前小车不可行， False:当前小车可行
        """
        dir_ls = list(map(lambda x: self.direct_dict[x],
                          [(car.road_id, car.next_road_id) for car in first_order_car]))
        aim_car_dir = dir_ls[idx]
        dir_ls.pop(idx)
        if aim_car_dir == 'straight':  # 小车直行则不发生冲突
            return False
        elif 'straight' in dir_ls:  # 小车左转或右转，但是其他车辆存在直行，则发生冲突
            return True
        elif aim_car_dir == 'left':  # 小车左转，其他车辆没有直行，则不会发生冲突
            return False
        elif 'left' in dir_ls:  # 小车右转，但其他车辆具有左转，则发生冲突
            return True
        else:  # 小车右转，其他车辆都右转，则不会发生冲突
            return False

    def run_car_in_magic_garage(self, moment, graph):
        """
        调度当前时刻，神奇车库中可以出发的小车
        :param moment: 当前时刻
        :param graph: 动态道路图
        :return:
        """
        for car in self.magic_garage[0]:
            if car.sche_time <= moment:
                car.update_route(graph, update=False)

                next_cross = car.next_cross_id
                for road in self.roads_dict.values():
                    if next_cross in [road.cross_1, road.cross_2]:
                        next_lane = road.di_lanes_dict[next_cross]

                is_access, info = next_lane.accessable(car)
                if is_access:
                    # 将小车从车道中拿出, 更新后方车辆可行驶距离信息,放入下一条车道
                    next_lane.push_a_car(car)
                    graph[car.loc][car.next_cross_id]['weight'] = car.v
                else:
                    continue
            else:
                continue

    def __str__(self):
        return 'Commander at {}'.format(self.id)
