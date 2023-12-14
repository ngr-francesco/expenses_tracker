import abc
import sys
from backend.sim.singleton import Singleton
class Button(abc.ABC,Singleton):
    def __init__(self):
        self.name = ''
        self.text = ''
        self.input_fields = {}
        self.screen_after_pressed = None
    
    def __str__(self):
        return self.name
    
    def __repr__(self) -> str:
        return self.str()
    
    def pressed(self,*args):
        raise NotImplementedError("Implement in children")

class QuitButton(Button):
    def __init__(self):
        super().__init__()
        self.name = 'Quit'
        self.text = 'Exiting application ...'
        self.screen_after_pressed = None
    
    def pressed(self, *args):
        print(self.text)
        sys.exit()

class NewGroupButton(Button):
    def __init__(self):
        super().__init__()
        
