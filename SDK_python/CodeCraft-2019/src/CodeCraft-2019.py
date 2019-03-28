#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: codeCraftOfHuawei2019Challenge
@file:CodeCraft-2019.py
@author: dujiahao
@create_time: 2019/3/18 22:09
@description:
"""
import logging
import sys
from driver import driver

# logging.basicConfig(level=logging.DEBUG,
#                     filename='../logs/CodeCraft-2019.log',
#                     format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     filemode='a')


def main():
    # if len(sys.argv) != 5:
    #     logging.info('please input args: car_path, road_path, cross_path, answerPath')
    #     exit(1)

    # car_path = sys.argv[1]
    # road_path = sys.argv[2]
    # cross_path = sys.argv[3]
    # answer_path = sys.argv[4]

    car_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_2\car.txt'
    road_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_2\road.txt'
    cross_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_2\cross.txt'
    answer_path = r'D:\Project\codeCraftOfHuawei2019Challenge\SDK_python\CodeCraft-2019\config_2\answer.txt'
    # logging.info("car_path is %s" % (car_path))
    # logging.info("road_path is %s" % (road_path))
    # logging.info("cross_path is %s" % (cross_path))
    # logging.info("answer_path is %s" % (answer_path))

    driver(road_path, car_path, cross_path, answer_path)



if __name__ == "__main__":
     main()
