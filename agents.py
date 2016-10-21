from utils import Direction, is_horizontal, distance, manhattan_distance
import constants

import time
from enum import Enum

def signo(num):
    return 1 if num>0 else (-1 if num<0 else 0)


class State(Enum):

    ACCELERATING = 1
    BREAKING = 2
    CRUISING = 3
    STOPPED = 4


class MessageType(Enum):

    DISTANCE = 1


class Message(object):

    def __init__(self, m_type):
        self.m_type = m_type


class Request(Message):

    def __init__(self, car, m_type):
        super().__init__(m_type)
        self.requester = car


class Response(Message):

    def __init__(self, m_type, msg):
        super().__init__(m_type)
        self.msg = msg


class Agent(object):

    def __init__(self):
        self.answers = []
        self.requests = []


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
        self.locate_car()

        self.state =  State.ACCELERATING
        self.arrived = False

        self.prev_x, self.prev_y = None, None

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

    def get_block(self, x, y):
        if is_horizontal(self.current_road().direction):
            return self.current_road().get_block(x)
        else:
            return self.current_road().get_block(y)

    def locate_car(self):
        self.get_block(self.x, self.y).cars.append(self)

    def current_road(self):
        return self.route.roads[self.route.index]

    def next_road(self):
        return self.route.roads[self.route.index+1] if self.route.index + 1 < len(self.route.roads) else None

    def process(self, delta_t):
        self.process_answers()
        self.process_requests()
        self.make_requests()
        self.process_location(delta_t)

    def process_answers(self):
        if not self.answers:
            self.process_return()
            return

        most_important_distance_msg = None

        while self.answers:
            ans = self.answers.pop()
            if ans.m_type == MessageType.DISTANCE:
                if ans.msg[0] < constants.DISTANCE_ACCEPTANCE:
                    if (not most_important_distance_msg) or ans.msg[0] < most_important_distance_msg.msg[0]:
                        most_important_distance_msg = ans

        if most_important_distance_msg:
            self.process_break(most_important_distance_msg.msg[0], most_important_distance_msg.msg[1])
        else:
            self.process_return()

    def process_break(self, distance, other):
        if self.state==State.STOPPED or self.no_need_breaking(other):
            self.process_return()
            return

        t = self.get_safety_time(distance)
        if is_horizontal(self.current_road().direction):
            self.acc_x = (other.speed_x-self.speed_x)/t
        else:
            self.acc_y = (other.speed_y-self.speed_y)/t

        if self.state == State.CRUISING or self.state == State.ACCELERATING:
            self.state = State.BREAKING

    def no_need_breaking(self, other):
        if other.current_road() != self.current_road():
            if is_horizontal(self.current_road().direction):
                return abs(self.speed_x) < abs(other.speed_y)
            else:
                return abs(self.speed_y) < abs(other.speed_x)
        else:
            if is_horizontal(self.current_road().direction):
                return abs(self.speed_x) < abs(other.speed_x)
            else:
                return abs(self.speed_y) < abs(other.speed_y)

    def get_safety_time(self, d):
        if is_horizontal(self.current_road().direction):
            return (d*0.8)/abs(self.speed_x)
        else:
            return (d*0.8)/abs(self.speed_y)

    def process_return(self):
        if self.state == State.STOPPED or self.state == State.BREAKING:
            self.set_original_acc()
            self.state = State.ACCELERATING

    def set_original_acc(self):
        road = self.current_road()
        if road.direction == Direction.EW or road.direction == Direction.WE:
            sign = 1 if road.direction == Direction.WE else -1
            self.acc_x, self.acc_y = sign*self.acceleration, 0
        elif road.direction == Direction.NS or road.direction == Direction.SN:
            sign = 1 if road.direction == Direction.NS else -1
            self.acc_y, self.acc_x = sign*self.acceleration, 0

    def process_requests(self):
        while self.requests:
            req = self.requests.pop()
            if req.m_type == MessageType.DISTANCE and self.before(req.requester):
                req.requester.answers.append(Response(MessageType.DISTANCE, [manhattan_distance(self.x, self.y, req.requester.x, req.requester.y), self]))

    def before(self, other):
        if other.current_road() != self.current_road():
            distance = manhattan_distance(self.x, self.y, other.x, other.y)
        else:
            if self.current_road().direction == Direction.WE:
                distance = self.x - other.x
            if self.current_road().direction == Direction.EW:
                distance = -(self.x - other.x)
            if self.current_road().direction == Direction.NS:
                distance = self.y-other.y
            if self.current_road().direction == Direction.SN:
                distance = -(self.y - other.y)

        if distance > 0 and distance<constants.DISTANCE_FOR_RESPONSE:
            return True
        return False

    def make_requests(self):
        block = self.get_block(self.x, self.y)
        for each in block.cars:
            if not each == self:
                each.requests.append(Request(self, MessageType.DISTANCE))

        next_block = block.road.get_next_block(block)
        turning_block = block.road.get_next_turning_block(block)

        next_road = self.next_road()

        if next_road and turning_block and next_road == turning_block.road:
            for each in turning_block.cars:
                if not each == self:
                    each.requests.append(Request(self, MessageType.DISTANCE))
        elif next_block:
            for each in next_block.cars:
                if not each == self:
                    each.requests.append(Request(self, MessageType.DISTANCE))

    def process_location(self, delta_t):
        self.update_position(delta_t)
        if self.should_turn():
            self.change_speeds()
            self.get_block(self.prev_x, self.prev_y).cars.remove(self)
            self.route.index+=1
            self.get_block(self.x, self.y).cars.append(self)
        elif self.arrived:
            if self.state == State.STOPPED:
                self.city.delete_agent(self)
        else:
            self.analyze_change_block()
            self.analyze_travel_end()

        if self.out_of_city():
            self.city.delete_agent(self)

    def analyze_change_block(self):
        prev_block = self.get_block(self.prev_x, self.prev_y)
        curr_block = self.get_block(self.x, self.y)
        if prev_block!=curr_block:
            prev_block.cars.remove(self)
            curr_block.cars.append(self)

    def update_position(self, delta_t):

        self.prev_x, self.prev_y = self.x, self.y

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
            return abs(self.x - self.route.destiny.number)<constants.ERROR
        return abs(self.y - self.route.destiny.number) < constants.ERROR

    def should_turn(self):
        if self.route.index == len(self.route.roads)-1:
            return False

        if is_horizontal(self.route.roads[self.route.index+1].direction):
            if abs(self.y - self.route.roads[self.route.index+1].number*self.city.block_height_size)<constants.ERROR:
                return True
            else:
                return False
        else:
            if abs(self.x - self.route.roads[self.route.index+1].number*self.city.block_width_size)<constants.ERROR:
                return True
            else:
                return False

