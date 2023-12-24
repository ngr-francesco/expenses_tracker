import abc
import sys
from backend.sim.singleton import Singleton
class Button(abc.ABC,Singleton):
    def __init__(self, owner):
        self.owner = owner
        self.name = ''
        self.text = ''
        self.input_fields = {}
        self.screen_after_pressed = None
        
    
    def __str__(self):
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
    def pressed(self, *args):
        print(self.text)
        if len(self.input_fields):
            for field in self.input_fields:
                self.input_fields[field] = input(field+ ': ')

class QuitButton(Button):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'Quit'
        self.text = 'Exiting application ...'
        self.screen_after_pressed = None
    
    def pressed(self, *args):
        super().pressed(*args)
        input()
        sys.exit()

class NewGroupButton(Button):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'New Group'
        self.text = 'Insert group name'
        self.input_fields = {
            'name': None
        }
    
    def pressed(self, *args):
        super().pressed(*args)
        # --- Insert functionality here:


        # -----------------------------
        if self.owner:
            self.owner.display_screen()
    