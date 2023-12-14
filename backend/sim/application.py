from backend.sim.screens import *
from backend.sim.buttons import *

class application:
    def __init__(self):
        self.class_instances = {MainScreen : MainScreen()}
        self.current_screen = self.class_instances[MainScreen]
    
    def run(self):
        self.current_screen.open()
        
