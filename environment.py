from agents import Car
from utils import Direction, is_horizontal

import constants

import random


class Place(object):
    def __init__(self, road, number):
        self.road = road
        self.number = number


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


class Environment(object):
    def __init__(self):
        pass

    def set_processor(self, processor):
        self.processor = processor

    def add_random_agent(self):
        agent = self.create_random_agent()
        self.processor.add_agent(agent)

    def add_multiple_agents(self):
        for i in range(self.get_multiple_amount()):
            agent = self.create_random_agent()
            self.processor.add_agent(agent)

    def delete_agent(self, agent):
        self.processor.remove_agent(agent)


class City(Environment):

    def __init__(self, name, height, width, horizontal_roads_count, vertical_roads_count):
        super().__init__()
        self.name = name
        self.height = height
        self.width = width
        self.horizontal_roads_count = horizontal_roads_count
        self.vertical_roads_count = vertical_roads_count

        self.block_height_size = height/ (self.vertical_roads_count-1)
        self.block_width_size = width/ (self.horizontal_roads_count-1)

        self.generate_roads()

    def generate_roads(self):
        self.roads = []
        self.horizontal_roads = {}
        self.vertical_roads = {}

        for i in range(self.horizontal_roads_count):
            road = Road(i, Direction.WE if i%2 else Direction.EW, self.width, self.vertical_roads_count-1)
            self.roads.append(road)
            self.horizontal_roads[i] = road
        for i in range(self.vertical_roads_count):
            road = Road(i, Direction.SN if i%2 else Direction.NS, self.height, self.horizontal_roads_count-1)
            self.roads.append(road)
            self.vertical_roads[i] = road

    def get_multiple_amount(self):
        return int(self.vertical_roads_count + self.horizontal_roads_count)

    def create_random_agent(self):
        length = random.randint(constants.MIN_TRAVEL_LENGTH, constants.MAX_TRAVEL_LENGTH)
        start = self.get_random_place()
        route = [start.road]
        curr = start
        while length>0:
            next_road = random.choice(self.get_possible_turns(curr))
            number = self.get_starting_number(curr.road, next_road)
            curr = Place(next_road, number)
            route.append(curr.road)
            length-=1
        end = self.get_possible_end(route[-1], curr.number)
        route = Route(route, start, end)
        return Car(self, route, random.uniform(constants.MIN_CRUISE_SPEED, constants.MAX_CRUISE_SPEED), random.uniform(constants.MIN_ACCEL_SPEED, constants.MAX_ACCEL_SPEED))

    def get_possible_end(self, road, number):
        if road.direction == Direction.WE:
            return Place(road, random.randint(number, number+int(self.block_width_size)-1))
        if road.direction == Direction.EW:
            return Place(road, random.randint(number - int(self.block_width_size)-1, number))
        if road.direction == Direction.NS:
            return Place(road, random.randint(number, number+int(self.block_height_size)-1))
        if road.direction == Direction.SN:
            return Place(road, random.randint(number - int(self.block_height_size)-1, number))

    def get_random_place(self):
        if random.random()>0.5:
            return Place(self.horizontal_roads[random.randint(0, int(self.horizontal_roads_count)-1)], random.randint(0, int(self.width)-1))
        return Place(self.vertical_roads[random.randint(0, int(self.vertical_roads_count)-1)], random.randint(0, int(self.height)-1))

    def get_starting_number(self, from_road, to_road):
        if to_road.direction == Direction.EW:
            return int(self.block_width_size*from_road.number)-1
        if to_road.direction == Direction.WE:
            return int(self.block_width_size*from_road.number)+1
        if to_road.direction == Direction.NS:
            return int(self.block_height_size*from_road.number)+1
        if to_road.direction == Direction.SN:
            return int(self.block_height_size*from_road.number)-1

    def get_possible_turns(self, place):
        if place.road.direction == Direction.WE:
            index = int(place.number//self.block_width_size)
            candidates = []
            for i in range(index+1, self.vertical_roads_count):
                if (not (place.road.number == 0 and self.vertical_roads[i].direction == Direction.SN)) and (not (place.road.number == self.horizontal_roads_count-1 and self.vertical_roads[i].direction == Direction.NS)):
                    candidates.append(self.vertical_roads[i])
            return candidates
        if place.road.direction == Direction.EW:
            index = int(place.number//self.block_width_size)
            candidates = []
            for i in range(0, index+1):
                if (not (place.road.number == 0 and self.vertical_roads[i].direction == Direction.SN)) and (not (place.road.number == self.horizontal_roads_count-1 and self.vertical_roads[i].direction == Direction.NS)):
                    candidates.append(self.vertical_roads[i])
            return candidates

        if place.road.direction == Direction.NS:
            index = int(place.number//self.block_height_size)
            candidates = []
            for i in range(index+1, self.horizontal_roads_count):
                if (not (place.road.number == 0 and self.horizontal_roads[i].direction == Direction.EW)) and (not (place.road.number == self.vertical_roads_count-1 and self.horizontal_roads[i].direction == Direction.WE)):
                    candidates.append(self.horizontal_roads[i])
            return candidates
        if place.road.direction == Direction.SN:
            index = int(place.number//self.block_height_size)
            candidates = []
            for i in range(0, index+1):
                if (not (place.road.number == 0 and self.horizontal_roads[i].direction == Direction.EW)) and (not (place.road.number == self.vertical_roads_count-1 and self.horizontal_roads[i].direction == Direction.WE)):
                    candidates.append(self.horizontal_roads[i])
            return candidates
