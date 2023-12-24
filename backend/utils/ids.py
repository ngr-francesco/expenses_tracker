import json
import os

from backend.utils.const import default_data_dir
from enum import Enum
import uuid

# TODO change this to the class definitions instead
default_ids = {
    'ListItem': 'it0000',
    'Member': 'mm0000',
    'Group': 'gr0000',
    'List': 'ls0000',
    'Transaction': 'tr0000', 
}

class IdTypes(Enum):
    LIST_ITEM = 0
    MEMBER = 1
    GROUP = 2
    LIST = 3
    TRANSACTION = 4

id_types = {
    'it' : IdTypes.LIST_ITEM,
    'mm' : IdTypes.MEMBER,
    'ls' : IdTypes.LIST,
    'tr' : IdTypes.TRANSACTION 
}



class IdFactory:
    file_path = os.path.join(default_data_dir,'id_factory','ids.json')
    try:
        with open(file_path,'r') as file:
            next_ids = json.load(file)
    except FileNotFoundError:
        next_ids = default_ids
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    
    @staticmethod
    def get_obj_id(obj):
        try:
            id = IdFactory.next_ids[type(obj).__name__]
            IdFactory._increment_ids(type(obj).__name__)
        except KeyError:
            raise ValueError(f"Object of type {type(obj).__name__} is not eligible for id assignment.")
        return id
    
    @staticmethod
    def roll_back_id(obj):
        """
        Roll back the last id assigned to an object type. If the object given as argument was not the last of its
        kind to receive an id, this method will raise an error.
        """
        try:
            id = IdFactory.next_ids[type(obj).__name__]
            # Check that the object was the last defined (to avoid conflicts)
            assert int(id[2:]) == int(obj.id[2:]) + 1 , "Id cannot be rolled back, this is a bug"
            IdFactory.next_ids[type(obj).__name__] = str(obj.id)
            IdFactory._save_ids()
        except KeyError:
            raise ValueError(f"Object of type {type(obj).__name__} is not eligible for id assignment.")

    
    def _increment_ids(name):
        id = IdFactory.next_ids[name]
        id_N = int(id[2:]) + 1
        next_id = id[:2] + str(id_N)
        IdFactory.next_ids[name] = next_id
        IdFactory._save_ids()

    
    def _save_ids():
        with open(IdFactory.file_path,'w+') as file:
            json.dump(IdFactory.next_ids, file, indent = 4)



def is_uuid4(id:str):
    try:
        id_class = uuid.UUID(id)

        return id_class.version == 4
    except ValueError:
        return False


