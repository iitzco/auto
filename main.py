import environment
import constants
from processor import Processor
import random

if __name__ == '__main__':
    random.seed(10)

    city = environment.City('City', constants.WIDTH, constants.HEIGHT, constants.HORIZONTAL_BLOCKS, constants.VERTICAL_BLOCKS)

    p = Processor(city)
    p.start_gui()
    p.run()

