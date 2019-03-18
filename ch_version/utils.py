# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""


def direct_relat_other(cross_id, roads_enumer):
    """
    输入与路口按照顺时针相连的四个道路对象
    输出为方向字典
    key：（roud_1, roud_2） value: {left, right, straight，unreachable}

    :param cross_id: 路口唯一标识
    :param roads: (1, road_1), (2, road_2), (3, road_3), (4, road_4)
    :return:
    """
    roads = list(filter(lambda x: x[1] is not None, roads_enumer))
    direct_dict = dict()
    for l1, r1 in roads:
        for l2, r2 in roads:
            if r1.road_id == r2.road_id:
                continue
            # r1 --> r2， 可以行驶
            r1_flag = r1.two_way or (cross_id == r1.corss_2)  # r1为双向道路，或者r1的终点路口为当前路口
            r2_flag = r2.two_way or (cross_id == r2.corss_1)  # r2为双向道路，或者r2的起始路口为当前路口

            if r1_flag and r2_flag:
                if (l1, l2) in [(1, 4), (4, 3), (3, 2), (2, 1)]:
                    direct_dict[(r1.road_id, r2.road_id)] = 'right'
                elif (l1, l2) in [(4, 1), (3, 4), (2, 3), (1, 2)]:
                    direct_dict[(r1.road_id, r2.road_id)] = 'left'
                else:
                    direct_dict[(r1.road_id, r2.road_id)] = 'straight'
            else:
                direct_dict[(r1.road_id, r2.road_id)] = 'unreachable'

    return direct_dict


def load_entities(_class, path, road_dict=None, car_dict=None):
    """
    加载文件数据，并将数据转化为对应的数据类型
    :param _class: 类名
    :param path: 文件路径
    :return: 实体映射字典，实体id -> 实体
    """
    entity_map = dict()
    with open(path) as file:
        lines = file.readlines()
        g = map(lambda x: x.strip('#()\n').split(','), lines)
        for entity_str in g:
            if 'id' in entity_str: continue  # remove header

            if road_dict is None:  # 加载汽车、道路实体
                entity = _class(*entity_str)
                id = entity_str[0]
                entity_map[id] = entity
            else:  # 加载与路口对应的 Commander 实体
                id = entity_str[0]
                roads = list(map(lambda x: road_dict.get(x), entity_str[1:]))
                entity_map[id] = _class(id, *roads)
                cars = [(car, 'active') if car.loc == id else None for car in car_dict.values()]
                entity_map[id].push_into_garage('active',
                                                *filter(lambda x: x is not None, cars))  # 将未出发的汽车放入magic_garage

    return entity_map


from road import Road
# from cross import Cross


# def load_traffic_data(car_path=None, road_path=None, cross_path=None):
#     """
#     :param car_path:
#     :param road_path:
#     :param cross_path:
#     :return:
#     """
#     car_path = '../config/car.txt'
#     road_path = '../config/road.txt'
#     cross_path = '../config/cross.txt'
#     traffic_model = [list(), list()]  # 0. Roads 1.Cross
#
#     road_dict = dict()
#     with open(road_path) as file:
#         file.readline()  # remove header
#         lines = file.readlines()
#         generator = map(lambda x: x.strip('#()\n').split(','), lines)
#         for line in generator:
#             road_dict[line[0]] = Road(*line)
#
#     cross_list = list()
#     with open(cross_path) as file:
#         file.readline()
#         lines = file.readlines()
#         generator = map(lambda x: x.strip('#()\n').split(','), lines)
#         for line in generator:
#             roads = [road_dict.get(road_id, -1) for road_id in line[1:]]
#             cross_list.append(Cross(line[0], *roads))
#
# load_traffic_data()
