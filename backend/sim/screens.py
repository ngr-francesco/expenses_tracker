"""
Moving across screens:
    Each screen should be instantiated only once,
    so you should make sure that there is only one instance 
    of each.
    You then have to look through the objects defined in the namespace and 
    get a reference to the right screen.
"""


import abc
from buttons import *
class Screen(abc.ABC):
    def __init__(self):
        self.title = ''
        self.reachable_screens = {}
        self.action_buttons = {}
        self.buttons = list(self.reachable_screens.keys()) + list(self.action_buttons.keys())
        self.buttons = [(i,button) for i,button in enumerate(self.buttons)]
        self.coming_from = None

    def change_screen(self,button_name):
        self.reachable_screens[button_name].open(self)
    
    def open(self, opened_by = None):
        if opened_by:
            self.coming_from = opened_by
        self.display_screen()
    
    def display_screen(self):
        print(self.title)
        print(self.text)
        self.show_buttons()

    def show_buttons(self):
        for i,button in self.buttons:
            print(i,button)
        valid_choice = False
        while not valid_choice:
            try:
                choice = int(input())
                if 0 <= choice < len(self.buttons):
                    valid_choice = True
                else:
                    print("Invalid choice. Choose again.")
            except ValueError:
                print("Inputs are expected to be numbers.")

            
        chosen_button = self.buttons[choice][1]
        if chosen_button in self.reachable_screens:
            self.change_screen(chosen_button)
        elif choice in self.action_buttons:
            self.action_buttons[chosen_button].pressed()
        
    def back_to_previous(self):
        # We don't update 'coming_from' so that it's possible
        # to chain 'backs' and reach the starting screen.
        self.coming_from.open()
    
    def add_screens(self, screens_dict:dict):
        self.reachable_screens.update(screens_dict)

class MainScreen(Screen):
    def __init__(self):
        self.title = 'Main Screen'
        self.text = ''
        self.reachable_screens = {
            'new_group': None,
            'settings': None,
        }
        self.action_buttons = {
            'Quit': QuitButton()
        }

        
        


        



