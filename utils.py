from enum import Enum

import math


class Direction(Enum):
    EW = 1
    WE = 2
    NS = 3
    SN = 4
    WEEW = 5
    SNNS = 6


def show_city(city):
    h_s = (''.join(' ' for e in range(int(city.width_distance) // 2)) +
           '| {} |' + ''.join(' '
                              for e in range(int(city.width_distance) // 2))
           ) * city.horizontal_roads_count
    l = [
        '↑' if city.vertical_roads[i].direction == Direction.SN else '↓'
        if city.vertical_roads[i].direction == Direction.NS else '↕'
        for i in range(city.vertical_roads_count)
    ]

    for i in range(city.horizontal_roads_count):
        for j in range(int(city.height_distance) // 4):
            aux_l = l if j % 2 else [' '] * city.vertical_roads_count
            print(h_s.format(*aux_l))
        s = ''.join('.' for e in range(len(h_s)))
        print(s)
        print(('   →   ' if city.horizontal_roads[i].direction == Direction.WE
               else '   ←   '
               if city.horizontal_roads[i].direction == Direction.EW else
               '↔') * (len(h_s) // 7))
        print(s)
        for j in range(int(city.height_distance) // 4):
            aux_l = l if j % 2 else [' '] * city.vertical_roads_count
            print(h_s.format(*aux_l))


def is_horizontal(d):
    return d == Direction.EW or d == Direction.WE


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def get_cuadratic_solution(a, b, c):
    d = (b**2) - (4 * a * c)  # discriminant

    if d < 0:
        return None
    elif d == 0:
        return (-b) / (2 * a)
    else:
        t1 = (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)
        t2 = (-b - math.sqrt(b**2 - 4 * a * c)) / (2 * a)
        return (t1, t2)


def get_useful_time(t):
    if not t:
        return INFINITE
    if isinstance(t, tuple):
        if t[0] > 0 and t[1] > 0:
            return min(t)
        if t[0] < 0 and t[1] < 0:
            return INFINITE
        return t[0] if t[0] > 0 else t[1]
    if t < 0:
        return INFINITE
    else:
        return t
