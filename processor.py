import gui
import agents
import time
import environment

import constants

class Processor(object):

    def __init__(self, environment):
        self.environment = environment
        self.environment.set_processor(self)
        self.agents = []
        self.gui = gui.TkinterGUI(environment, self)
        self.last = None

    def start_gui(self):
        self.gui.start()

    def add_agent(self, agent):
        self.agents.append(agent)

    def remove_agent(self, agent):
        self.agents.remove(agent)
        self.gui.remove_agent(agent)

    def run(self):
        while True:
            now = time.time()
            delta_t = (now - self.last) if self.last else 0
            self.last = now
            for agent in self.agents:
                agent.process(delta_t)
            self.gui.update(self.agents) 

