import environment
import constants
from processor import Processor
import random
import configparser
import sys


class NotEvenNumberException(Exception):
    pass


class Parameters(object):
    def __init__(self):
        pass

    def load(self, config):
        city_config = config['CITY']
        self.width = int(city_config['WIDTH'])
        self.height = int(city_config['HEIGHT'])
        self.horizontal_roads_count = int(city_config['HORIZONTAL_ROADS'])
        self.vertical_roads_count = int(city_config['VERTICAL_ROADS'])

        journey_config = config['JOURNEY']
        self.min_travel_length = int(journey_config['MIN_TRAVEL_LENGTH'])
        self.max_travel_length = int(journey_config['MAX_TRAVEL_LENGTH'])

        car_config = config['CAR']
        self.min_cruise_speed = int(car_config['MIN_CRUISE_SPEED'])
        self.max_cruise_speed = int(car_config['MAX_CRUISE_SPEED'])
        self.min_accel_speed = int(car_config['MIN_ACCEL_SPEED'])
        self.max_accel_speed = int(car_config['MAX_ACCEL_SPEED'])
        self.distance_acceptance = int(car_config['DISTANCE_ACCEPTANCE'])

        if self.horizontal_roads_count % 2 == 1 or self.vertical_roads_count % 2 == 1:
            raise NotEvenNumberException()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Must provide path to config file")
        exit(1)

    random.seed(10)

    path = sys.argv[1]

    config = configparser.ConfigParser()
    config.read(path)

    parameters = Parameters()
    try:
        parameters.load(config)
    except ValueError:
        print("Error while parsing config file. Values must be integers.")
        exit(1)
    except KeyError:
        print(
            "Error while parsing config file. Incorrect keys, check example.")
        exit(1)
    except NotEvenNumberException:
        print(
            "Error while parsing config file. Amount of roads must be even numbers."
        )
        exit(1)

    city = environment.City('City', parameters)

    p = Processor(city)
    p.start_gui()
    p.run()
