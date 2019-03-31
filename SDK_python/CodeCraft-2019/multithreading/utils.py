# -*- coding: utf-8 -*-
"""
Created on 2019/3/14 上午10:19

@author: Evan Chen
"""


def direct_relat_other(cross_id, roads_enumer):

    roads = list(filter(lambda x: x[1] is not None, roads_enumer))
    direct_dict = dict()
    for l1, r1 in roads:
        for l2, r2 in roads:
            if r1.road_id == r2.road_id:
                continue
            r1_flag = r1.two_way or (cross_id == r1.corss_2)
            r2_flag = r2.two_way or (cross_id == r2.corss_1)

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
        direct_dict[(c1, cross_id)] = 'straight'

    # if cross_id == 12:
        # print(direct_dict)
    return direct_dict

def conver_to_cross(cross_id, road):

    if cross_id == road.cross_1:
        return road.cross_2
    else:
        return road.cross_1

from os.path import split,join
def to_sort(line):
    str_num = line.split(',')[-1].split(')')[0]
    int_num = int(str_num)
    return int_num

def change_base_num(line, base):
    l = line.split(',')
    planeTime = int(l[-1].split(')')[0])
    fix = planeTime - base
    l[-1] = '{})\n'.format(fix)
    return ','.join(l)

def split_file(car_path, data_count):
    """将文件按行分割多份"""
    base_dir = split(car_path)[0]
    file_paths = list()
    count = 0
    with open(car_path) as car_file:
        header = car_file.readline()
        lines = list()
        sort_lines = sorted(car_file.readlines(), key=to_sort)
        for ix, line in enumerate(sort_lines):
            count += 1
            lines.append(line)
            if count == data_count:
                new_path = join(base_dir, 'car_{}.txt'.format(str(ix)))
                file_paths.append(new_path)

                base_num = int(lines[0].split(',')[-1].split(')')[0]) - 1
                lines = [change_base_num(line, base_num) for line in lines]

                with open(new_path, 'w') as tf:
                    tf.write(header)
                    tf.writelines(lines)
                    tf.flush()

                lines = list()
                count = 0

        if len(lines) !=0 :
            new_path = join(base_dir, 'car_{}.txt'.format(str(len(sort_lines))))
            file_paths.append(new_path)
            base_num = int(lines[0].split(',')[-1].split(')')[0]) - 1
            lines = [change_base_num(line, base_num) for line in lines]
            with open(new_path, 'w') as tf:
                tf.write(header)
                tf.writelines(lines)
                tf.flush()
    return file_paths

def review_sche_time(line, last_sche_time):
    l = line.split(',')
    l[1] = str(int(l[1]) + last_sche_time + 30)
    return ','.join(l)

def merge_file(new_answer_paths, answer_path):
    all_lines = []
    for path in new_answer_paths:
        with open(path) as file:
            slines = list(file.readlines())
            last_sche_time = int(slines[0].split(',')[1])
            slines = [review_sche_time(line, last_sche_time) for line in slines]
            all_lines += slines
    with open(answer_path, 'w') as file:
        file.writelines(all_lines)
        file.flush()

def crear_answer(answer_ls, anser_path):
    with open(anser_path,'w') as file:
        all_lines = []
        last_sche_time = 0
        for anser in answer_ls:
            slines = [review_sche_time(line,last_sche_time) for line in anser]

            all_lines += slines
            last_sche_time = int(anser[0].split(',')[1])

        file.writelines(all_lines)
        file.flush()