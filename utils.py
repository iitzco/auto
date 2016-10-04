from enum import Enum

class Direction(Enum):
    EW = 1
    WE = 2
    NS = 3
    SN = 4
    WEEW = 5
    SNNS = 6


def show_city(city):
    h_s = (''.join(' 'for e in range(int(city.width_distance)//2)) + '| {} |' + ''.join(' 'for e in range(int(city.width_distance)//2)))*city.horizontal_roads_count
    l = ['↑' if city.vertical_roads[i].direction == Direction.SN else '↓' if city.vertical_roads[i].direction == Direction.NS else '↕'for i in range(city.vertical_roads_count)] 

    for i in range(city.horizontal_roads_count):
        for j in range(int(city.height_distance)//4):
            aux_l = l if j%2 else [' ']*city.vertical_roads_count
            print(h_s.format(*aux_l))
        s = ''.join('.'for e in range(len(h_s)))
        print(s)
        print(('   →   ' if city.horizontal_roads[i].direction==Direction.WE else '   ←   ' if city.horizontal_roads[i].direction==Direction.EW else '↔') * (len(h_s)//7))
        print(s)
        for j in range(int(city.height_distance)//4):
            aux_l = l if j%2 else [' ']*city.vertical_roads_count
            print(h_s.format(*aux_l))

