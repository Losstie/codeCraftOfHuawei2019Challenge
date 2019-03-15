# -*- coding: utf-8 -*-
"""
Created on 2019/3/11 下午6:45

@author: Evan Chen
"""
import networkx as nx
from ch_version.car import Car
from ch_version.cross import Cross
from ch_version.road import Road
from ch_version.utils import load_entities
from ch_version.scheduler import Scheduler
from matplotlib import pyplot as plt


def driver(road_path, car_path, cross_path):
    # 初始化实体对象
    cars_dict = load_entities(Car, car_path)
    road_dict = load_entities(Road, road_path)
    commander_dict = load_entities(Cross, cross_path, road_dict, cars_dict)

    # 初始化有向图
    G = nx.DiGraph()
    # 添加节点
    for cross in commander_dict.values():
        G.add_node(cross.id)
    # 添加边
    for road in road_dict.values():
        G.add_edge(road.cross_1, road.cross_2, weight=road.current_v_max(road.cross_1))
        if road.two_way:
            G.add_edge(road.cross_2, road.cross_1, weight=road.current_v_max(road.cross_2))

    # 查看有向图
    #plot_gird(G)

    # 执行调度
    sche = Scheduler(G, road_dict.values(), commander_dict.values())
    # sche.start()

def plot_gird(G):
    position = nx.spring_layout(G)

    nx.draw_networkx_nodes(G, position, node_size=100, node_color="r")
    nx.draw_networkx_edges(G, position, length=10)
    nx.draw_networkx_labels(G, position)
    plt.show()


if __name__ == '__main__':
    road_path = '../config/road.txt'
    car_path = '../config/car.txt'
    cross_path = '../config/cross.txt'
    driver(road_path, car_path, cross_path)
