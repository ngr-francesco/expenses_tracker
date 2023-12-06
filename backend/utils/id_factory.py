import json
from const import default_ids

class IdFactory:
    try:
        with open('../data/ids.json','r') as file:
            next_ids = json.load(file)
    except FileNotFoundError:
        next_ids = default_ids
    
    @staticmethod
    def get_obj_id(obj):
        try:
            id = IdFactory.next_ids[type(obj).__name__]
            IdFactory._increment_ids(type(obj).__name__)
        except KeyError:
            raise ValueError(f"Object of type {type(obj).__name__} is not eligible for id assignment.")
        return id
    
    def _increment_ids(name):
        id = IdFactory.next_ids[name]
        id_N = int(id[2:]) + 1
        next_id = id[:2] + str(id_N)
        IdFactory.next_ids[name] = next_id
        IdFactory._save_ids()
    
    def _save_ids():
        with open('../data/ids.json','w+') as file:
            json.dump(IdFactory.next_ids, file)


