import gui
import agents
import time
import environment


class Processor(object):

    def __init__(self, environment):
        self.environment = environment
        self.agents = []
        self.gui = gui.TkinterGUI(environment, self)
        self.last = None

    def start_gui(self):
        self.gui.start()

    def add_agent(self, agent):
        self.agents.append(agent)

    def run(self):
        while True:
            now = time.time()
            delta_t = (now - self.last) if self.last else 0
            self.last = now
            for agent in self.agents:
                agent.process(delta_t)
            self.gui.update(self.agents) 

    def add_car(self):
        road = self.environment.horizontal_roads[0] 
        route = environment.Route([road], 10, 40)
        self.agents.append(agents.Car(self.environment, route, 10, 0))

if __name__ == '__main__':

    city = environment.City('City', 50, 50, 5, 5)

    road = city.horizontal_roads[0] 
    route = environment.Route([road], 10, 40)

    road1 = city.horizontal_roads[2] 
    route1 = environment.Route([road1], 0, 40)

    c1 = agents.Car(city, route, 10, 0)
    c2 = agents.Car(city, route1, 10, 0)

    p = Processor(city)
    p.add_agent(c1)
    p.add_agent(c2)
    
    p.start_gui()
    p.run()

