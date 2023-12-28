from backend.cls.saveable import Saveable

def reload_backend():
    """
    Save and reload all instances of Saveable
    """
    for instance in Saveable._instances:
        instance.save_data()
        instance.load()
