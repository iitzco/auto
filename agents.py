from utils import Direction, is_horizontal
import time

from enum import Enum

ERROR = 2

class Agent(object):

    def __init__(self):
        self.msg = []

class State(Enum):

    ACCELERATING = 1
    BREAKING = 2
    CRUISING = 3
    STOPPED = 4


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

        self.speed_x = 0
        self.speed_y = 0

        self.set_position()
        self.locate_car_in_block()

        self.state =  State.ACCELERATING
        self.arrived = False

    @classmethod
    def withRandomRoute(cls):
        pass

    def set_position(self):
        start_road = self.route.origin.road
        if start_road.direction == Direction.EW or start_road.direction == Direction.WE:
            self.x = self.route.origin.number
            self.y = start_road.number*self.city.block_height_size
            sign = 1 if start_road.direction == Direction.WE else -1
            self.acc_x, self.acc_y = sign*self.acceleration, 0
        elif start_road.direction == Direction.NS or start_road.direction == Direction.SN:
            self.y = self.route.origin.number
            self.x = start_road.number*self.city.block_width_size
            sign = 1 if start_road.direction == Direction.NS else -1
            self.acc_y, self.acc_x = sign*self.acceleration, 0

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
        if self.should_turn():
            self.change_speeds()
            self.route.index+=1
        elif self.arrived:
            if self.state == State.STOPPED:
                self.city.delete_agent(self)
        else:
            self.analyze_travel_end()

        if self.out_of_city():
            self.city.delete_agent(self)
	
    def update_position(self, delta_t):

        if self.state == State.CRUISING:
            self.y += self.speed_y*delta_t
            self.x += self.speed_x*delta_t
        elif self.state == State.ACCELERATING or self.state == State.BREAKING:
            prev_speeds = (self.speed_x, self.speed_y)
            self.y += self.speed_y*delta_t + (1/2)*self.acc_y*(delta_t**2)
            self.speed_y += self.acc_y*delta_t

            self.x += self.speed_x*delta_t + (1/2)*self.acc_x*(delta_t**2)
            self.speed_x += self.acc_x*delta_t

            if self.state == State.ACCELERATING and (abs(self.speed_y) > self.max_speed or abs(self.speed_x) > self.max_speed):
                self.state = State.CRUISING
            if self.state == State.BREAKING and (abs(prev_speeds[0]-self.speed_x)>abs(prev_speeds[0]) or abs(prev_speeds[1]-self.speed_y)>abs(prev_speeds[1])):
                self.speed_x = 0
                self.speed_y = 0
                self.state = State.STOPPED

    def change_speeds(self):
        curr = self.route.roads[self.route.index].direction
        next_ = self.route.roads[self.route.index+1].direction
        
        if curr == Direction.NS:
            sign = 1 if next_ == Direction.WE else -1
        if curr == Direction.SN:
            sign = 1 if next_ == Direction.EW else -1
        if curr == Direction.EW:
            sign = 1 if next_ == Direction.SN else -1
        if curr == Direction.WE:
            sign = 1 if next_ == Direction.NS else -1
        self.speed_x, self.speed_y = sign*self.speed_y, sign*self.speed_x
        self.acc_x, self.acc_y = sign*self.acc_y, sign*self.acc_x

    def analyze_travel_end(self):
        if self.route.index == len(self.route.roads)-1:
            if self.has_arrived():
                self.arrived = True
                self.acc_x, self.acc_y = -self.acc_x, -self.acc_y
                self.state = State.BREAKING

    def out_of_city(self):
        return self.x<0 or self.x>self.city.width or self.y<0 or self.y>self.city.height

    def has_arrived(self):
        if is_horizontal(self.route.roads[-1].direction):
            return abs(self.x - self.route.destiny.number)<ERROR
        return abs(self.y - self.route.destiny.number) < ERROR

    def should_turn(self):
        if self.route.index == len(self.route.roads)-1:
            return False

        if is_horizontal(self.route.roads[self.route.index+1].direction):
            if abs(self.y - self.route.roads[self.route.index+1].number*self.city.block_height_size)<ERROR:
                return True
            else:
                return False
        else:
            if abs(self.x - self.route.roads[self.route.index+1].number*self.city.block_width_size)<ERROR:
                return True
            else:
                return False

