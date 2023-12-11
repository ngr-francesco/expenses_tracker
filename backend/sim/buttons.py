import abc
import sys
class Button(abc.ABC):
    def __init__(self):
        self.name = ''
        self.text = ''
        self.input_fields = {}
        self.screen_after_pressed = None
    
    def pressed(self,*args):
        raise NotImplementedError("Implement in children")

class QuitButton(Button):
    def __init__(self):
        self.name = 'Quit'
        self.text = 'Exiting application ...'
        self.screen_after_pressed = None
    
    def pressed(self, *args):
        print(self.text)
        sys.exit()
    
