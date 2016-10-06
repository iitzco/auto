from utils import Direction
import time

class Agent(object):

    def __init__(self):
        self.msg = []

class Car(Agent):
    counter = 0

    def __init__(self, city, route, max_speed, acceleration):
        super(Car, self).__init__()
        self.id = Car.counter
        Car.counter+=1

        self.city = city
        self.route = route
        self.max_speed = max_speed
        self.acceleration = acceleration

        self.set_position()
        self.locate_car_in_block()

        self.counter_events = 0

    @classmethod
    def withRandomRoute(cls):
        pass

    def set_position(self):
        start_road = self.route.origin.road
        if start_road.direction == Direction.EW or start_road.direction == Direction.WE:
            self.x = self.route.origin.number
            self.y = start_road.number*self.city.block_height_size
        elif start_road.direction == Direction.NS or start_road.direction == Direction.SN:
            self.y = self.route.origin.number
            self.x = start_road.number*self.city.block_width_size

    def locate_car_in_block(self):
        origin = self.route.origin.number
        start_road = self.route.origin.road
        if start_road.direction == Direction.EW or start_road.direction == Direction.WE:
            index = int(origin/self.city.block_width_size)
        elif start_road.direction == Direction.NS or start_road.direction == Direction.SN:
            index = int(origin/self.city.block_height_size)
        start_road.blocks[index].cars.append(self)

    def process(self, delta_t):
        self.update_position(delta_t)
	
    def update_position(self, delta_t):
        direction = self.route.roads[self.route.index].direction
        if direction == Direction.NS:
            self.y -= self.max_speed*delta_t
        if direction == Direction.SN:
            self.y += self.max_speed*delta_t
        if direction == Direction.EW:
            self.x -= self.max_speed*delta_t
        if direction == Direction.WE:
            self.x += self.max_speed*delta_t
