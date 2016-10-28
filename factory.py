import constants
import random

from utils import Direction, is_horizontal, manhattan_distance
from components import Block, Place, Road, Route

from agents import Car


class CarFactory(object):
    def __init__(self, city):
        self.city = city

    def generate_random_agent(self):
        length = random.randint(constants.MIN_TRAVEL_LENGTH,
                                constants.MAX_TRAVEL_LENGTH)

        start = self.get_random_start()

        route_list = [start.block]
        curr = start.block

        while length > 0:
            next_block = self.decide_next_block(curr)
            route_list.append(next_block)
            curr = next_block
            length -= 1

        end = Place(route_list[-1], self.get_possible_end(curr))

        route = Route(route_list, start, end)

        speed = random.uniform(constants.MIN_CRUISE_SPEED,
                               constants.MAX_CRUISE_SPEED)
        acc = random.uniform(constants.MIN_ACCEL_SPEED,
                             constants.MAX_ACCEL_SPEED)

        return Car(self.city, route, speed, acc)

    def decide_next_block(self, block):
        n_block = block.road.get_next_block(block)
        t_block = block.road.get_next_turning_block(block)
        if not n_block:
            return t_block
        if not t_block:
            return n_block
        return random.choice([n_block, t_block])

    def get_possible_end(self, block):
        return random.uniform(block.from_n, block.to_n)

    def get_random_start(self):
        while True:
            if random.random() > 0.5:
                road = self.city.horizontal_roads[random.randint(
                    0, int(self.city.horizontal_roads_count) - 1)]
            else:
                road = self.city.vertical_roads[random.randint(
                    0, int(self.city.vertical_roads_count) - 1)]
            number = random.randint(0, int(self.city.width) - 1)
            block = road.get_block(number)
            if number > (block.from_n + constants.CAR_RADIUS) and number < (
                    block.to_n - constants.CAR_RADIUS):
                if not block.cars:
                    return Place(block, number)
                else:
                    overlaps = False
                    for each in block.cars:
                        if is_horizontal(road.direction):
                            pos = each.x
                        else:
                            pos = each.y
                        if abs(pos - number) < 3 * constants.CAR_RADIUS:
                            overlaps = True
                            break
                    if not overlaps:
                        return Place(block, number)

    def get_starting_number(self, from_road, to_road):
        if to_road.direction == Direction.EW:
            return int(self.block_width_size * from_road.number) - 1
        if to_road.direction == Direction.WE:
            return int(self.block_width_size * from_road.number) + 1
        if to_road.direction == Direction.NS:
            return int(self.block_height_size * from_road.number) + 1
        if to_road.direction == Direction.SN:
            return int(self.block_height_size * from_road.number) - 1
