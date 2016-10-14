import tkinter as tk
import constants

import random

class ConsoleGUI():
    def __init__(self):
        super(ConsoleGUI, self).__init__()

    def update_car(self, car):
        print("X {} - Y {}".format(car.x, car.y))


class TkinterGUI():

    def __init__(self, city, processor):
        self.city=city
        self.processor = processor
        self.frame = MainFrame(city, self)
        self.cars_map = {}
        self.refresh()

    def update(self, cars):
        for car in cars:
            self.frame.update_car(car, self.cars_map) 
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

class MainFrame(tk.Frame):

    def __init__(self, environment, manager):
        tk.Frame.__init__(self)
        self.city=environment
        self.manager = manager

        self.init_main_frame()

        self.city_frame = tk.Frame(self)
        self.menu_frame = tk.Frame(self)

        self.city_frame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)
        self.menu_frame.pack(fill=tk.Y, expand=tk.YES, side=tk.RIGHT)

        self.canvas = tk.Canvas(self.city_frame, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.label = tk.Label(self.menu_frame, text='Menu')
        self.label.pack(side=tk.TOP)

        self.add_button = tk.Button(self.menu_frame, text='Add Car', command=self.city.add_random_agent)
        self.add_button.pack()

        self.add_boost_button = tk.Button(self.menu_frame, text='Add {} Cars'.format(int(self.city.vertical_roads_count+self.city.horizontal_roads_count)), command=self.city.add_multiple_agents)
        self.add_boost_button.pack()

    def init_main_frame(self):
        self.master.title("GUI")

        # Full Windows Size
        self.master.geometry("{0}x{1}+0+0".format(
            self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def draw_city(self):
        self.w = self.canvas.winfo_width()
        self.h = self.canvas.winfo_height()

        self.margin_w = self.w*constants.MARGIN/2
        self.margin_h = self.h*constants.MARGIN/2

        self.w *= (1-constants.MARGIN)
        self.h *= (1-constants.MARGIN)

        self.rel_x = self.w/self.city.width
        self.rel_y = self.h/self.city.height

        for i in range(self.city.horizontal_roads_count):
            pos = (i*self.city.block_height_size*self.rel_y) + self.margin_h
            self.canvas.create_rectangle(self.margin_w-constants.ROAD_WIDTH/2, pos-constants.ROAD_WIDTH/2, self.w+self.margin_w+constants.ROAD_WIDTH/2, pos+constants.ROAD_WIDTH/2, fill="gray", outline='grey')

        for i in range(self.city.vertical_roads_count):
            pos = (i*self.city.block_width_size*self.rel_x) + self.margin_w
            self.canvas.create_rectangle(pos-constants.ROAD_WIDTH/2, self.margin_h, pos+constants.ROAD_WIDTH/2, self.h+self.margin_h, fill="gray", outline='grey')


    def get_drawing_position(self, car):
        x = car.x*self.rel_x + self.margin_w
        y = car.y*self.rel_y + self.margin_h
        return (x,y)
        
    def update_car(self, car, cars_map):
        spot = cars_map.get(car.id)
        if spot:
            color = spot[1]
            self.canvas.delete(spot[0])
        else:
            color = random.choice(["red", "green", "blue", "cyan", "yellow", "magenta"])
        pos = self.get_drawing_position(car)
        id_ = self.canvas.create_oval(pos[0]-constants.CAR_RADIUS, pos[1]-constants.CAR_RADIUS, pos[0]+constants.CAR_RADIUS, pos[1]+constants.CAR_RADIUS, fill=color)
        cars_map[car.id] = (id_, color)

    def delete_agent(self, spot):
        self.canvas.delete(spot[0])
