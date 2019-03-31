# -*- coding: utf-8 -*-
"""
Created on 2019/3/11 涓嬪崍6:45

@author: Evan Chen
"""
#import networkx as nx
import nx
from car import Car
from cross import Cross
from road import Road
from scheduler import Scheduler



# def plot_gird(G):
#     position = nx.spring_layout(G)
#
#     nx.draw_networkx_nodes(G, position, node_size=100, node_color="r")
#     nx.draw_networkx_edges(G, position)
#     nx.draw_networkx_labels(G, position)
#     plt.show()


def load_traffic_data(car_path=None, road_path=None, cross_path=None):

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


    for cross in cross_dict.values():
        cross.magic_garage[0] = sorted(cross.magic_garage[0], key=lambda x:(x.sche_time,x.car_id))

    return car_list, list(road_dict.values()), list(cross_dict.values())


def driver(road_path, car_path, cross_path, answer_path):

    car_list, road_list, cross_list = load_traffic_data(car_path, road_path, cross_path)

    G = nx.DiGraph()

    for cross in cross_list:
        G.add_node(cross.id)

    for road in road_list:
        G.add_edge(road.cross_1, road.cross_2, weight=road.weight_in_graph(road.cross_1))
        if road.two_way:
            G.add_edge(road.cross_2, road.cross_1, weight=road.weight_in_graph(road.cross_2))

    for car in car_list:
        car.graph = G

    for road in road_list:
        road.graph = G


    sche = Scheduler(G, car_list, road_list, cross_list)
    sche.run()

    sche.create_answer(answer_path)


