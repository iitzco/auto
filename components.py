from utils import Direction, is_horizontal, manhattan_distance

class Place(object):
    def __init__(self, block, number):
        self.block = block
        self.number = number

class Route(object):
    def __init__(self, blocks, origin, destiny):
        self.blocks = blocks
        self.index = 0

        # Places
        self.origin = origin
        self.destiny = destiny

class Block(object):
    def __init__(self, number, road, from_n, to_n):
        self.number = number
        self.road = road
        self.from_n = from_n
        self.to_n = to_n
        self.cars = []


class Road(object):
    def __init__(self, number, direction, size, blocks_count, city):
        self.number = number
        self.direction = direction
        self.blocks = []
        self.size_per_block = size / blocks_count
        for i in range(blocks_count):
            self.blocks.append(
                Block(i, self, i * self.size_per_block, (i + 1) *
                      self.size_per_block))
        self.city = city

    def get_block(self, position):
        index = int(position / self.size_per_block)
        index = 0 if index < 0 else (index - 1
                                     if index >= len(self.blocks) else index)
        return self.blocks[index]

    def get_next_block(self, block):
        index = block.number
        if self.direction == Direction.NS or self.direction == Direction.WE:
            return self.blocks[index + 1] if index + 1 < len(
                self.blocks) else None
        else:
            return self.blocks[index - 1] if index - 1 >= 0 else None

    def get_next_turning_block(self, block):
        index = block.number

        if self.direction == Direction.NS:
            road = self.city.horizontal_roads[index + 1]
            if road.direction == Direction.WE:
                block_number = self.number
                return road.blocks[block_number] if block_number < len(
                    self.blocks) else None
            else:
                block_number = self.number - 1
                return road.blocks[block_number] if block_number >= 0 else None

        if self.direction == Direction.SN:
            road = self.city.horizontal_roads[index]
            if road.direction == Direction.WE:
                block_number = self.number
                return road.blocks[block_number] if block_number < len(
                    self.blocks) else None
            else:
                block_number = self.number -1
                return road.blocks[block_number] if block_number >= 0 else None

        if self.direction == Direction.WE:
            road = self.city.vertical_roads[index + 1]
            if road.direction == Direction.NS:
                block_number = self.number
                return road.blocks[block_number] if block_number < len(
                    self.blocks) else None
            else:
                block_number = self.number - 1
                return road.blocks[block_number] if block_number >= 0 else None

        if self.direction == Direction.EW:
            road = self.city.vertical_roads[index]
            if road.direction == Direction.NS:
                block_number = self.number
                return road.blocks[block_number] if block_number < len(
                    self.blocks) else None
            else:
                block_number = self.number - 1
                return road.blocks[block_number] if block_number >= 0 else None


