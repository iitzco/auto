from agents import Car
from utils import Direction

ROAD_WIDTH = 5

class Block(object):

    def __init__(self, road, from_n, to_n):
        self.road = road
        self.from_n = from_n
        self.to_n = to_n
        self.cars = []


class Road(object):

    def __init__(self, number, direction, size, blocks_count):
        self.number = number
        self.direction = direction
        self.blocks = []
        size_per_block = size/blocks_count;
        for i in range(blocks_count):
            self.blocks.append(Block(self, i*size_per_block, (i+1)*size_per_block))


class Route(object):

    def __init__(self, roads, origin, destiny):
        self.roads = roads
        self.origin = origin
        self.destiny = destiny
        self.index = 0


class City(object):

    def __init__(self, name, height, width, horizontal_roads_count, vertical_roads_count):
        self.name = name
        self.height = height
        self.width = width
        self.horizontal_roads_count = horizontal_roads_count
        self.vertical_roads_count = vertical_roads_count
        
        self.width_distance = width / self.horizontal_roads_count
        self.height_distance = height/ self.vertical_roads_count

        self.block_height_size = height/ (self.vertical_roads_count-1)
        self.block_width_size = width/ (self.horizontal_roads_count-1)

        self.generate_roads()

    def generate_roads(self):
        self.roads = []
        self.horizontal_roads = {}
        self.vertical_roads = {}

        for i in range(self.horizontal_roads_count):
            road = Road(i, Direction.EW if i%2 else Direction.WE, self.width, self.vertical_roads_count-1)
            self.roads.append(road)
            self.horizontal_roads[i] = road
        for i in range(self.vertical_roads_count):
            road = Road(i, Direction.NS if i%2 else Direction.SN, self.height, self.horizontal_roads_count-1)
            self.roads.append(road)
            self.vertical_roads[i] = road

