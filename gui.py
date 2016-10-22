import tkinter as tk
import constants

import random
import math


class ConsoleGUI():
    def __init__(self):
        super(ConsoleGUI, self).__init__()

    def update_car(self, car):
        print("X {} - Y {}".format(car.x, car.y))


class TkinterGUI():
    def __init__(self, city, processor):
        self.city = city
        self.processor = processor
        self.frame = MainFrame(city, self)
        self.cars_map = {}
        self.fading_accident_list = []

        self.refresh()

    def update(self, cars, delta_t):
        for car in cars:
            self.frame.update_car(car, self.cars_map)
        self.frame.update_accidents(delta_t)
        self.frame.menu_frame.update_delta_t_label(delta_t)
        self.frame.menu_frame.update_cars_label(len(self.processor.agents))
        self.refresh()

    def refresh(self):
        self.frame.update_idletasks()
        self.frame.update()

    def start(self):
        self.frame.draw_city()

    def remove_agent(self, agent):
        spot = self.cars_map.get(agent.id)
        if spot:
            self.frame.delete_agent(spot)


class MenuFrame(tk.Frame):
    def __init__(self, parent, city):
        tk.Frame.__init__(self, parent)
        self.city = city

        self.stats_label = tk.Label(self, text='Stats', font=(None, 40))
        self.stats_label.pack(side=tk.TOP)

        self.accident_label = tk.Label(
            self,
            text='Accidents: {}'.format(self.city.accidents),
            font=(None, 20))
        self.accident_label.pack(pady=5)

        self.delta_t_label = tk.Label(self, text='DeltaT: ', font=(None, 20))
        self.delta_t_label.pack(pady=5)

        self.cars_label = tk.Label(self, text='Cars: ', font=(None, 20))
        self.cars_label.pack(pady=5)

        self.label = tk.Label(self, text='Menu', font=(None, 40))
        self.label.pack(side=tk.TOP)

        self.add_button = tk.Button(
            self, text='Add Car', command=self.city.add_random_agent)
        self.add_button.pack(pady=5)

        self.add_boost_button = tk.Button(
            self,
            text='Add {} Cars'.format(
                int(self.city.vertical_roads_count +
                    self.city.horizontal_roads_count)),
            command=self.city.add_multiple_agents)
        self.add_boost_button.pack(pady=5)

        self.add_super_boost_button = tk.Button(
            self,
            text='Add {} Cars'.format(
                int(self.city.vertical_roads_count +
                    self.city.horizontal_roads_count) * 5),
            command=self.city.add_times_multiple_agents)
        self.add_super_boost_button.pack(pady=5)

    def update_accidents_label(self):
        self.accident_label.config(
            text='Accidents: {}'.format(self.city.accidents))

    def update_delta_t_label(self, delta_t):
        self.delta_t_label.config(text='DeltaT: {:.3f}'.format(delta_t))

    def update_cars_label(self, quantity):
        self.cars_label.config(text='Cars: {}'.format(quantity))


class CityFrame(tk.Frame):
    def __init__(self, parent, city, manager):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.city = city
        self.manager = manager

        self.canvas = tk.Canvas(self, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

    def draw_city(self):
        self.w = self.canvas.winfo_width()
        self.h = self.canvas.winfo_height()

        self.margin_w = self.w * constants.MARGIN / 2
        self.margin_h = self.h * constants.MARGIN / 2

        self.w *= (1 - constants.MARGIN)
        self.h *= (1 - constants.MARGIN)

        self.rel_x = self.w / self.city.width
        self.rel_y = self.h / self.city.height

        for i in range(self.city.horizontal_roads_count):
            pos = (i * self.city.block_height_size * self.rel_y
                   ) + self.margin_h
            self.canvas.create_rectangle(
                self.margin_w - constants.ROAD_WIDTH / 2,
                pos - constants.ROAD_WIDTH / 2,
                self.w + self.margin_w + constants.ROAD_WIDTH / 2,
                pos + constants.ROAD_WIDTH / 2,
                fill="gray",
                outline='grey')

        for i in range(self.city.vertical_roads_count):
            pos = (i * self.city.block_width_size * self.rel_x) + self.margin_w
            self.canvas.create_rectangle(
                pos - constants.ROAD_WIDTH / 2,
                self.margin_h,
                pos + constants.ROAD_WIDTH / 2,
                self.h + self.margin_h,
                fill="gray",
                outline='grey')

    def get_drawing_position_car(self, car):
        return self.get_drawing_position(car.x, car.y)

    def get_drawing_position(self, x, y):
        mapped_x = x * self.rel_x + self.margin_w
        mapped_y = y * self.rel_y + self.margin_h
        return (mapped_x, mapped_y)

    def update_car(self, car, cars_map):
        spot = cars_map.get(car.id)
        if spot:
            self.canvas.delete(spot[0])
        color = self.get_speed_color(car)
        pos = self.get_drawing_position_car(car)
        id_ = self.canvas.create_oval(
            pos[0] - constants.CAR_RADIUS,
            pos[1] - constants.CAR_RADIUS,
            pos[0] + constants.CAR_RADIUS,
            pos[1] + constants.CAR_RADIUS,
            fill=color)
        cars_map[car.id] = (id_, color)

    def update_accidents(self, delta_t):
        self.parent.menu_frame.update_accidents_label()
        for each in self.city.accidents_list[:]:
            (c1, c2) = self.city.accidents_list.pop()
            x, y = self.get_drawing_position((c1.x + c2.x) / 2,
                                             (c1.y + c2.y) / 2)
            r = 3 * constants.CAR_RADIUS
            id_ = self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill='red')
            self.manager.fading_accident_list.append([id_, (x, y), r])
        self.draw_fading_accidents(delta_t)

    def draw_fading_accidents(self, delta_t):
        for each in self.manager.fading_accident_list[:]:
            self.canvas.delete(each[0])
            x, y = each[1]
            r = each[2]
            each[2] = each[2] - 10 * delta_t
            if each[2] < 0:
                self.canvas.delete(each[0])
                self.manager.fading_accident_list.remove(each)
            else:
                id_ = self.canvas.create_oval(
                    x - r, y - r, x + r, y + r, fill='red')
                each[0] = id_

    def delete_agent(self, spot):
        self.canvas.delete(spot[0])

    def get_speed_color(self, car):
        speed = math.sqrt(car.speed_x**2 + car.speed_y**2)
        speed = speed / self.city.get_max_speed()
        if speed > 1:
            speed = 1
        base_FF_speed = int(speed * 255)
        invert_FF_speed = int(255 - base_FF_speed)
        return "#00" + "{:02x}".format(base_FF_speed) + "{:02x}".format(
            invert_FF_speed)


class MainFrame(tk.Frame):
    def __init__(self, environment, manager):
        tk.Frame.__init__(self)
        self.city = environment
        self.manager = manager

        self.init_main_frame()

        self.city_frame = CityFrame(self, self.city, self.manager)
        self.menu_frame = MenuFrame(self, self.city)

        self.city_frame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)
        self.menu_frame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.RIGHT)

    def init_main_frame(self):
        self.master.title("AUTO - self driving cars")

        # Full Windows Size
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def draw_city(self):
        self.city_frame.draw_city()

    def delete_agent(self, spot):
        self.city_frame.delete_agent(spot)

    def update_car(self, car, car_map):
        self.city_frame.update_car(car, car_map)

    def update_accidents(self, delta_t):
        self.city_frame.update_accidents(delta_t)
