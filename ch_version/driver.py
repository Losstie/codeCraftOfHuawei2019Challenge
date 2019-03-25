# -*- coding: utf-8 -*-
"""
Created on 2019/3/11 下午6:45

@author: Evan Chen
"""
import networkx as nx
from car import Car
from cross import Cross
from road import Road

from scheduler import Scheduler
from matplotlib import pyplot as plt


def plot_gird(G):
    position = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, position, node_size=100, node_color="r")
    nx.draw_networkx_edges(G, position)
    nx.draw_networkx_labels(G, position)
    plt.show()


def load_traffic_data(car_path=None, road_path=None, cross_path=None):
    """
    :param car_path:
    :param road_path:
    :param cross_path:
    :return:
    """
    road_dict = dict()
    with open(road_path) as file:
        file.readline()
        lines = file.readlines()
        generator = map(lambda x: x.strip('#()\n').split(','), lines)
        for line in generator:
            road_dict[line[0]] = Road(*line)

    cross_dict = dict()
    with open(cross_path) as file:
        file.readline()
        lines = file.readlines()
        generator = map(lambda x: x.strip('#()\n ').split(','), lines)
        for line in generator:
            roads = [road_dict.get(road_id.strip(), None) for road_id in line[1:]]
            cross_dict[line[0]] = Cross(line[0], *roads)

    car_list = list()
    with open(car_path) as file:
        file.readline()  # remove header
        lines = file.readlines()
        generator = map(lambda x: x.strip('#()\n').split(','), lines)
        for line in generator:
            car = Car(*line)
            car_list.append(car)
            start_cross = cross_dict[line[1].strip()]
            start_cross.magic_garage[0].append(car)

    # 按出发时间和车辆id排序
    for cross in cross_dict.values():
        cross.magic_garage[0] = sorted(cross.magic_garage[0], key=lambda x:(x.sche_time,x.car_id))

    return car_list, list(road_dict.values()), list(cross_dict.values())


def driver(road_path, car_path, cross_path):
    # 初始化实体对象
    car_list, road_list, cross_list = load_traffic_data(car_path, road_path, cross_path)

    # 初始化有向图
    G = nx.DiGraph()
    # 添加节点
    for cross in cross_list:
        G.add_node(cross.id)
    # 添加边
    for road in road_list:
        G.add_edge(road.cross_1, road.cross_2, weight=road.weight_in_graph(road.cross_1))
        if road.two_way:
            G.add_edge(road.cross_2, road.cross_1, weight=road.weight_in_graph(road.cross_2))

    # 将全局动态图插入汽车对象中, 用于规划路线
    for car in car_list:
        car.graph = G

    # 将全局动态图插入道路对象中，用于更新动态图
    for road in road_list:
        road.graph = G

    # 查看有向图
    plot_gird(G)

    # 执行调度
    sche = Scheduler(car_list, road_list, cross_list)
    sche.run()


if __name__ == '__main__':
    # road_path = '../config/road.txt'
    # car_path = '../config/car.txt'
    # cross_path = '../config/cross.txt'

    road_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_3\road.txt'
    car_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_3\car.txt'
    cross_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_3\cross.txt'
    driver(road_path, car_path, cross_path)
