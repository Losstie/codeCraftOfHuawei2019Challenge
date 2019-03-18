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

    def run_a_time(self, current_moment):
        """
        调度处于等待行驶状态的车辆，并且通过路口时符合交通规则
        每一个路口需要多次调度才可以运行一个时间片段
        :return: 1.当前路口是否存在未调度车辆：{True, False}  2.本次运行抵达该路口有多少辆
        """
        # 所有出口为当前路口的单向道路
        export_road = list()
        for road in self.roads_dict.values():
            di_road = road.get_di_road(self.id, direct='export')
            if di_road is None:
                continue
            export_road.append((road.road_id, di_road))

        # 每一条道路对应的非空调度序列
        # (road_id, export_road_sche_queue)
        road_queues = list(filter(lambda x: len(x[1]) != 0, map(lambda x: (x[0],x[1].scheduler_queue), export_road)))
        all_queues_num = len(road_queues)

        if all_queues_num == 0: # 没有调度的车辆
            return False, 0

        has_wait_car, arrived_cars_num = self.__run(all_queues_num, road_queues, current_moment)
        return has_wait_car, arrived_cars_num

    def __run(self, all_queues_num, road_queues, current_moment):
        print('self_id', self.id)
        arrived_cars_num = 0
        finished_lane_ls = list()  # 完成调度的车道
        conflict_lane_ls = list()  # 因其他车道未调度，导致当前无法调度的车道

        # 每一个出口道路对应的优先级最高的车辆
        first_order_car = [q[0] for _, q in road_queues]
        has_movable_car = True  # 是否有可动的车辆
        while has_movable_car:
            for idx, road_queue in enumerate(road_queues):
                road_id, queue = road_queue

                # 如果队列为空，则说明全部调度完毕
                if len(queue) == 0:
                    print('None queue')
                    finished_lane_ls.append(idx)
                    continue

                # 如果已经调度完成或者处于冲突状态，则不需要在调度
                if idx in conflict_lane_ls + finished_lane_ls:
                    print('conflict')
                    continue

                for car in queue:
                    if car.stat == 'finial':
                        print('fininal')
                        queue.remove(car)
                        continue

                    # 到达目标路口
                    if self.id == car.dest:
                        print('arrive')
                        car.real_time = current_moment
                        # 将小车从车道中拿出, 更新 后方 车辆可行驶距离信息, 放入神奇车库
                        car.run_out_current_road()
                        self.magic_garage[1].append(car)
                        arrived_cars_num += 1
                        queue.remove(car)  # 将小车从调度队列中移除
                        self.roads_dict[road_id].pull_a_car(car)
                        continue

                    # 当前小车为该车道优先级最高的车辆
                    # 检测小车是否能通过路口, 若不能，则调度其他路口
                    first_order_car[idx] = car
                    if self.has_conflict(idx, first_order_car):
                        break
                    else:
                        # 获取下一条道路信息
                        print('进入下一条道路', car.next_cross_id)
                        next_road = None
                        next_cross = car.next_cross_id # 这里的小车一定会过路口，因此会有这个属性
                        for road in self.roads_dict.values():
                            if next_cross in [road.cross_1, road.cross_2]:
                                next_road = road
                        #print('self_id', self.id)
                        try:
                            is_success, info = next_road.push_a_car(car, self.id)
                        except:
                            # print('self_id', self.id,)
                            print(car)

                        if is_success:
                            # print('mark')
                            # car.loc = self.id
                            queue.remove(car)
                            self.roads_dict[road_id].pull_a_car(car, self.id)
                        elif info == 'road limit':
                            car.run_to_edge()
                            queue.remove(car)
                        else:
                            conflict_lane_ls.append(idx)

            finished_lane_num = len(finished_lane_ls)
            conflict_lane_num = len(conflict_lane_ls)
            if finished_lane_num + conflict_lane_num == all_queues_num:
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
        # dir_ls = list(map(lambda x: self.direct_dict[x],
        #                   [(car.road_id, car.next_road_id) for car in first_order_car]))
        # aim_car_dir = dir_ls[idx]
        # dir_ls.pop(idx)
        # if aim_car_dir == 'straight':  # 小车直行则不发生冲突
        #     return False
        # elif 'straight' in dir_ls:  # 小车左转或右转，但是其他车辆存在直行，则发生冲突
        #     return True
        # elif aim_car_dir == 'left':  # 小车左转，其他车辆没有直行，则不会发生冲突
        #     return False
        # elif 'left' in dir_ls:  # 小车右转，但其他车辆具有左转，则发生冲突
        #     return True
        # else:  # 小车右转，其他车辆都右转，则不会发生冲突
        #     return False
        return False

    def run_car_in_magic_garage(self, moment):
        """
        调度当前时刻，神奇车库中可以出发的小车
        :param moment: 当前时刻
        :param graph: 动态道路图
        :return:
        """
        for car in self.magic_garage[0]:
            if car.sche_time <= moment:
                car.update_route()

                # 获取下一条道路信息
                next_road = None
                next_cross = car.next_cross_id  # 这里的小车一定会过路口，因此会有这个属性
                for road in self.roads_dict.values():
                    if next_cross in [road.cross_1, road.cross_2]:
                        next_road = road

                is_success, info = next_road.push_a_car(car, self.id)
                if is_success:
                    self.magic_garage[0].remove(car)
                else:
                    continue
            else:
                continue

    def __str__(self):
        return 'Commander at {}'.format(self.id)