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

def direct_relat_other_test(cross_id, roads_enumer):
    roads = list(filter(lambda x: x[1] is not None, roads_enumer))
    crosses = list(map(lambda x: (x[0],conver_to_cross(cross_id, x[1])), roads))

    direct_dict = dict()
    for l1, c1 in crosses:
        for l2, c2 in crosses:
            if c1 == c2:
                continue

            if (l1, l2) in [(1, 4), (4, 3), (3, 2), (2, 1)]:
                direct_dict[(c1, c2)] = 'right'
            elif (l1, l2) in [(4, 1), (3, 4), (2, 3), (1, 2)]:
                direct_dict[(c1, c2)] = 'left'
            else:
                direct_dict[(c1, c2)] = 'straight'
    return direct_dict

def conver_to_cross(cross_id, road):
    """
    cross_id -> road 所属方向
    :param cross_id:
    :param road:
    :return:
    """
    if cross_id == road.cross_1:
        return road.cross_2
    if road.two_way:
        return road.cross_1