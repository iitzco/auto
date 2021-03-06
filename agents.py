from utils import Direction, is_horizontal, distance, manhattan_distance, get_cuadratic_solution
import constants

import time
from enum import Enum

INFINITE = 100000


def signo(num):
    return 1 if num > 0 else (-1 if num < 0 else 0)


class State(Enum):

    ACCELERATING = 1
    BREAKING = 2
    CRUISING = 3
    STOPPED = 4


class MessageType(Enum):

    DISTANCE = 1
    INTERSECTION = 2


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


class NavigationManager(object):
    def __init__(self, car, max_speed, acceleration, route, error,
                 distance_acceptance):
        self.car = car

        self.max_speed = max_speed
        self.acceleration = acceleration

        self.speed_x = 0
        self.speed_y = 0

        self.arrived = False
        self.crossing_car = False

        self.route = route

        self.error = error
        self.distance_acceptance = distance_acceptance

    def current_road(self):
        return self.route.blocks[self.route.index].road

    def current_block(self):
        road = self.current_road()
        if is_horizontal(road.direction):
            return road.get_block(self.x)
        else:
            return road.get_block(self.y)

    def expected_block(self):
        return self.route.blocks[self.route.index]

    def set_original_position(self):
        road = self.current_road()

        if is_horizontal(road.direction):
            self.x = self.route.origin.number
            self.y = road.number * self.car.city.block_height_size

        else:
            self.y = self.route.origin.number
            self.x = road.number * self.car.city.block_width_size

    def set_original_acc(self):
        road = self.current_road()

        if is_horizontal(road.direction):
            sign = 1 if road.direction == Direction.WE else -1
            self.acc_x, self.acc_y = sign * self.acceleration, 0

        else:
            sign = 1 if road.direction == Direction.NS else -1
            self.acc_y, self.acc_x = sign * self.acceleration, 0

    def init_position(self):
        self.set_original_position()
        self.set_original_acc()

        self.current_block().cars.append(self.car)
        self.state = State.ACCELERATING

    def process_location(self, delta_t):
        self.update_position(delta_t)
        self.analyze_update()
        self.analyze_travel_end()

    def update_position(self, delta_t):

        if self.state == State.CRUISING:
            self.x += self.speed_x * delta_t
            self.y += self.speed_y * delta_t

        elif self.state == State.ACCELERATING or self.state == State.BREAKING:

            prev_speeds = (self.speed_x, self.speed_y)

            self.y += self.speed_y * delta_t + (1 / 2) * self.acc_y * (delta_t
                                                                       **2)
            self.speed_y += self.acc_y * delta_t

            self.x += self.speed_x * delta_t + (1 / 2) * self.acc_x * (delta_t
                                                                       **2)
            self.speed_x += self.acc_x * delta_t

            if self.state == State.ACCELERATING and (
                    abs(self.speed_y) > self.max_speed or
                    abs(self.speed_x) > self.max_speed):
                self.speed_y = signo(self.speed_y) * self.max_speed
                self.speed_x = signo(self.speed_x) * self.max_speed

                self.state = State.CRUISING

            if self.state == State.BREAKING:
                if abs(prev_speeds[0] - self.speed_x) > abs(prev_speeds[
                        0]) or abs(prev_speeds[1] - self.speed_y) > abs(
                            prev_speeds[1]):
                    self.speed_x = 0
                    self.speed_y = 0
                    self.state = State.STOPPED

    def analyze_update(self):
        # Analyze also lost cars that missed a turn.
        # This will drive through current road but
        # in following blocks.

        road = self.current_road()
        block = self.current_block()
        expected_block = self.expected_block()

        self.remove_from_road(road)

        if self.on_end_of_block(
                block) and expected_block == block and self.route.index != len(
                    self.route.blocks) - 1:

            curr = self.route.blocks[self.route.index].road.direction
            next_ = self.route.blocks[self.route.index + 1].road.direction

            if curr != next_:
                if curr == Direction.NS:
                    sign = 1 if next_ == Direction.WE else -1
                if curr == Direction.SN:
                    sign = 1 if next_ == Direction.EW else -1
                if curr == Direction.EW:
                    sign = 1 if next_ == Direction.SN else -1
                if curr == Direction.WE:
                    sign = 1 if next_ == Direction.NS else -1
                self.speed_x, self.speed_y = sign * self.speed_y, sign * self.speed_x
                self.acc_x, self.acc_y = sign * self.acc_y, sign * self.acc_x

            self.route.index += 1

        # current_block takes into account index++ in case of not lost car.
        new_block = self.current_block()
        new_block.cars.append(self.car)

    def remove_from_road(self, road):
        for each in road.blocks:
            if self.car in each.cars:
                each.cars.remove(self.car)

    def on_end_of_block(self, block):
        direction = block.road.direction

        if direction == Direction.NS:
            d = abs(self.y - block.to_n)
        if direction == Direction.SN:
            d = abs(self.y - block.from_n)
        if direction == Direction.WE:
            d = abs(self.x - block.to_n)
        if direction == Direction.EW:
            d = abs(self.x - block.from_n)

        return d < self.error

    def analyze_travel_end(self):
        if self.route.index == len(self.route.blocks) - 1:
            if (not self.arrived) and self.has_arrived():
                self.arrived = True
                self.set_original_acc()
                self.acc_x, self.acc_y = -self.acc_x, -self.acc_y
                self.state = State.BREAKING

        if self.arrived:
            if self.state == State.STOPPED:
                self.car.city.inform_arrival()
                self.car.city.delete_agent(self.car)

        if self.out_of_city():
            self.car.city.inform_arrival()
            self.car.city.delete_agent(self.car)

    def out_of_city(self):
        return (self.x < -2 * self.error or
                self.x > self.car.city.width + 2 * self.error or
                self.y < -2 * self.error or
                self.y > self.car.city.height + 2 * self.error)

    def has_arrived(self):
        if is_horizontal(self.route.blocks[-1].road.direction):
            n = self.x
        else:
            n = self.y

        return abs(n - self.route.destiny.number) < self.error

    def process_break(self, distance, other):
        if self.state == State.STOPPED or (other and
                                           self.no_need_breaking(other)):
            if not self.crossing_car:
                self.process_return()
            return

        t = self.get_safety_time(distance)

        if other:
            other_speed_x, other_speed_y = other.navigation_manager.speed_x, other.navigation_manager.speed_y
        else:
            other_speed_x, other_speed_y = 0, 0

        if is_horizontal(self.current_road().direction):
            self.acc_x = (other_speed_x - self.speed_x) / t
        else:
            self.acc_y = (other_speed_y - self.speed_y) / t

        if self.state == State.CRUISING or self.state == State.ACCELERATING:
            self.state = State.BREAKING

    def no_need_breaking(self, other):
        if other.navigation_manager.current_road() != self.current_road():

            if is_horizontal(self.current_road().direction):
                return abs(self.speed_x) < abs(
                    other.navigation_manager.speed_y)
            else:
                return abs(self.speed_y) < abs(
                    other.navigation_manager.speed_x)

        else:

            if is_horizontal(self.current_road().direction):
                return abs(self.speed_x) < abs(
                    other.navigation_manager.speed_x)
            else:
                return abs(self.speed_y) < abs(
                    other.navigation_manager.speed_y)

    def get_safety_time(self, d):
        if is_horizontal(self.current_road().direction):
            return (d * 0.8) / abs(self.speed_x)
        else:
            return (d * 0.8) / abs(self.speed_y)

    def process_return(self):
        if self.arrived:
            should_stop = False
            if is_horizontal(self.current_road().direction):
                if abs(self.speed_x) < 0.075 * self.max_speed:
                    should_stop = True
            else:
                if abs(self.speed_y) < 0.075 * self.max_speed:
                    should_stop = True

            if should_stop:
                self.speed_x, self.speed_y = 0, 0
                self.state = State.STOPPED

            return

        if self.state == State.STOPPED or self.state == State.BREAKING:
            self.set_original_acc()
            self.state = State.ACCELERATING

    def get_distance(self, other):
        if other.navigation_manager.current_road() != self.current_road():
            d = abs(self.x - other.navigation_manager.x) + abs(
                self.y - other.navigation_manager.y)

        else:
            if self.current_road().direction == Direction.WE:
                d = self.x - other.navigation_manager.x
            if self.current_road().direction == Direction.EW:
                d = -(self.x - other.navigation_manager.x)
            if self.current_road().direction == Direction.NS:
                d = self.y - other.navigation_manager.y
            if self.current_road().direction == Direction.SN:
                d = -(self.y - other.navigation_manager.y)

        return d

    def before(self, other):
        d = self.get_distance(other)
        if d > 0 and d < self.distance_acceptance:
            return True
        return False

    def effective_distance(self, other):
        return self.get_distance(other) - 2 * constants.CAR_RADIUS

    def passed_half_block(self):
        curr_road_direction = self.current_road().direction
        curr_block = self.current_block()
        half = curr_block.from_n + (curr_block.to_n - curr_block.from_n) / 2
        if is_horizontal(curr_road_direction):
            if curr_road_direction == Direction.WE:
                return self.x > half
            else:
                return self.x < half
        else:
            if curr_road_direction == Direction.NS:
                return self.y > half
            else:
                return self.y < half

    def distance_to_intersection(self):
        curr_road_direction = self.current_road().direction
        curr_block = self.current_block()
        if is_horizontal(curr_road_direction):
            if curr_road_direction == Direction.WE:
                return abs(curr_block.to_n - self.x)
            else:
                return abs(curr_block.from_n - self.x)
        else:
            if curr_road_direction == Direction.NS:
                return abs(curr_block.to_n - self.y)
            else:
                return abs(curr_block.from_n - self.y)


class CommunicationManager(object):
    def __init__(self, car, distance_acceptance):
        self.car = car
        self.distance_acceptance = distance_acceptance

    def process_answers(self):
        most_important_distance_msg = None

        self.car.navigation_manager.crossing_car = False

        while self.car.answers:
            ans = self.car.answers.pop()

            if ans.m_type == MessageType.DISTANCE:
                if ans.msg[0] < self.distance_acceptance:
                    if (not most_important_distance_msg
                        ) or ans.msg[0] < most_important_distance_msg.msg[0]:
                        most_important_distance_msg = ans

            if ans.m_type == MessageType.INTERSECTION:
                d = self.car.navigation_manager.distance_to_intersection()

                if d > 3 * constants.CAR_RADIUS:
                    self.car.navigation_manager.crossing_car = True

                    if (not most_important_distance_msg
                        ) or d < most_important_distance_msg.msg[0]:

                        # 3 because d is distance from center of car to intersection.
                        # Should include self, other car passing and extra space
                        most_important_distance_msg = Response(
                            MessageType.DISTANCE,
                            [d - 3 * constants.CAR_RADIUS, None])

        if most_important_distance_msg:
            self.car.navigation_manager.process_break(
                most_important_distance_msg.msg[0],
                most_important_distance_msg.msg[1])

        else:
            self.car.navigation_manager.process_return()

    def process_requests(self):
        while self.car.requests:
            req = self.car.requests.pop()

            if req.m_type == MessageType.DISTANCE and self.car.navigation_manager.before(
                    req.requester):

                d = self.car.navigation_manager.effective_distance(
                    req.requester)

                if d <= 0:
                    self.car.city.inform_crash(self.car, req.requester)
                else:
                    req.requester.answers.append(
                        Response(MessageType.DISTANCE, [
                            d * 0.5, self.car
                        ]))  # Aparent 80% less space for breaking

            if req.m_type == MessageType.INTERSECTION:
                if self.car.navigation_manager.passed_half_block():
                    req.requester.answers.append(
                        Response(MessageType.INTERSECTION, self.car))

    def make_requests(self):
        block = self.car.navigation_manager.current_block()

        for each in block.cars:
            if not each == self.car:
                each.requests.append(Request(self.car, MessageType.DISTANCE))

        next_block = block.road.get_next_block(block)
        if next_block:
            for each in next_block.cars:
                if not each == self.car:
                    each.requests.append(
                        Request(self.car, MessageType.DISTANCE))

        turning_block = block.road.get_next_turning_block(block)
        if turning_block:
            for each in turning_block.cars:
                if not each == self.car:
                    each.requests.append(
                        Request(self.car, MessageType.DISTANCE))

        priority_block = block.road.get_priority_block(block)
        if priority_block and self.car.navigation_manager.passed_half_block():
            for each in priority_block.cars:
                if not each == self.car:
                    each.requests.append(
                        Request(self.car, MessageType.INTERSECTION))


class Car(Agent):
    counter = 0

    def __init__(self, city, route, max_speed, acceleration, error,
                 distance_acceptance):
        super(Car, self).__init__()
        self.id = Car.counter
        Car.counter += 1

        self.city = city

        self.navigation_manager = NavigationManager(
            self, max_speed, acceleration, route, error, distance_acceptance)
        self.communication_manager = CommunicationManager(self,
                                                          distance_acceptance)

        self.navigation_manager.init_position()

    def process(self, delta_t):
        self.communication_manager.process_answers()
        self.communication_manager.process_requests()
        self.navigation_manager.process_location(delta_t)
        self.communication_manager.make_requests()
