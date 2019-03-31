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
from utils import split_file, merge_file,crear_answer
from os.path import split, join
import multiprocessing

# logging.basicConfig(level=logging.DEBUG,
#                     filename='../logs/CodeCraft-2019.log',
#                     format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     filemode='a')

from multiprocessing import Process
def main():
    # if len(sys.argv) != 5:
    #     logging.info('please input args: car_path, road_path, cross_path, answerPath')
    #     exit(1)

    # car_path = sys.argv[1]
    # road_path = sys.argv[2]
    # cross_path = sys.argv[3]
    # answer_path = sys.argv[4]
    #car_path = '/Users/ch_cmpter/Desktop/car_test.txt'
    car_path = '../config_5/car.txt'
    road_path = '../config_5/road.txt'
    cross_path = '../config_5/cross.txt'
    answer_path = '../config_5/answer.txt'
    # logging.info("car_path is %s" % (car_path))
    # logging.info("road_path is %s" % (road_path))
    # logging.info("cross_path is %s" % (cross_path))
    # logging.info("answer_path is %s" % (answer_path))

    car_paths = split_file(car_path, 8000)
    base_answer_dir = split(answer_path)[0]
    answer_paths = [join(base_answer_dir, 'answer_{}.txt'.format(str(ix))) for ix, _ in enumerate(car_paths)]

    pool = multiprocessing.Pool()
    results = []
    for ix, path in zip(car_paths, answer_paths):
        result = pool.apply_async(driver, args=(road_path,path[0],cross_path,path[1]))
        results.append(result)

    pool.close()
    pool.join()
    for r in results:
        print(r.get())
    # answer_ls = list(map(lambda x:x[1].get(),sorted(results,key=lambda x:x[0])))

    # crear_answer(answer_ls, answer_path)



if __name__ == "__main__":
     main()
