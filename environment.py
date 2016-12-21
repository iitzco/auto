from agents import Car
from utils import Direction, is_horizontal, manhattan_distance
from factory import CarFactory
from components import Road, Route, Block

import random


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

    def add_times_multiple_agents(self):
        for i in range(5 * self.get_multiple_amount()):
            agent = self.create_random_agent()
            self.processor.add_agent(agent)

    def add_custom_agents(self, amount):
        for i in range(amount):
            agent = self.create_random_agent()
            self.processor.add_agent(agent)

    def delete_agent(self, agent):
        self.processor.remove_agent(agent)

    def get_all_agents(self):
        return self.processor.agents

    def pause(self):
        self.processor.paused = not self.processor.paused


class City(Environment):
    def __init__(self, name, params):
        super().__init__()
        self.name = name

        self.params = params

        self.height = params.height
        self.width = params.width
        self.horizontal_roads_count = params.horizontal_roads_count
        self.vertical_roads_count = params.vertical_roads_count

        self.block_height_size = self.height / (
            self.horizontal_roads_count - 1)
        self.block_width_size = self.width / (self.vertical_roads_count - 1)

        self.generate_roads()

        self.car_factory = CarFactory(self, params)

        self.accidents = 0
        self.accidents_list = []

        self.arrivals = 0

    def generate_roads(self):
        self.roads = []
        self.horizontal_roads = {}
        self.vertical_roads = {}

        for i in range(self.horizontal_roads_count):
            road = Road(i, Direction.WE if i % 2 else Direction.EW, self.width,
                        self.vertical_roads_count - 1, self)
            self.roads.append(road)
            self.horizontal_roads[i] = road
        for i in range(self.vertical_roads_count):
            road = Road(i, Direction.SN if i % 2 else Direction.NS,
                        self.height, self.horizontal_roads_count - 1, self)
            self.roads.append(road)
            self.vertical_roads[i] = road

    def get_multiple_amount(self):
        return int(self.vertical_roads_count + self.horizontal_roads_count)

    def inform_crash(self, car1, car2):
        self.accidents += 2
        self.accidents_list.append((car1, car2))
        self.processor.remove_agent(car1)
        self.processor.remove_agent(car2)

    def inform_arrival(self):
        self.arrivals += 1

    def get_max_speed(self):
        return self.params.max_cruise_speed

    def create_random_agent(self):
        return self.car_factory.generate_random_agent()
