from typing import Any
from backend.cls.saveable import Saveable
from dataclasses import dataclass

def reload_backend():
    """
    Save and reload all instances of Saveable
    """
    for instance in Saveable._instances:
        instance.save_data()
        instance.load()

def save_all():
    """
    Save all saveable objects
    """
    for instance in Saveable._instances:
        instance.save_data()
