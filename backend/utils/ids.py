import json
import os

from backend.settings import prefs
from enum import Enum
import uuid
import re


class Id(str):
    @property
    def literal(self):
        if len(self)<2:
            raise ValueError(f"Incorrect Id: {self}")
        return self[:2]
    @property
    def numeral(self):
        if len(self) < 2:
            raise ValueError(f"Incorrect Id: {self}")
        return int(self[2:])
    
    @staticmethod
    def is_id(id_str: str):
        """
        Simplistic by design, only make sure that the given string is
        made of 2 alphabetical chars + at least 4 numbers
        """
        if len(id_str) < 6:
            return False
        if not all(char.isalpha() for char in id_str[:2]):
            return False
        numeral = id_str[2:]
        if not all(char.isdigit() for char in numeral) or len(numeral) < 4:
            return False
        return True
        

        

# TODO change this to the class definitions instead
default_ids = {
    'ListItem': Id('it0000'),
    'Member': Id('mm0000'),
    'Group': Id('gr0000'),
    'List': Id('ls0000'),
    'Transaction': Id('tr0000'), 
    'PendingTransactions': Id('pt0000')
}

class IdFactory:
    file_path = os.path.join(prefs.data_dir,'id_factory','ids.json')
    try:
        with open(file_path,'r') as file:
            next_ids = json.load(file)
    except FileNotFoundError:
        next_ids = default_ids
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    # Convert strings to ids
    for key,value in next_ids.items():
        next_ids[key] = Id(value)

    @staticmethod
    def check_id_against_type(obj_type, id):
        obj_type = obj_type.__name__
        id = Id(id)
        if not obj_type in IdFactory.next_ids:
            raise ValueError(f"Object does not support id {obj_type}, {id}")
        id_in_factory = IdFactory.next_ids[obj_type]
        if id.literal != id_in_factory.literal:
            raise ValueError(f"Id for object {obj_type}, should start with "
                             f"{id_in_factory.literal}, not {id.literal} (full: {id})")
        if id.numeral > id_in_factory.numeral:
            raise ValueError(f"Id of loaded object {obj_type} is not compatible with "
                             f"ids stored in data folder: {IdFactory.file_path}")
    
    @staticmethod
    def get_obj_id(obj):
        obj_type = type(obj).__name__
        try:
            id = IdFactory.next_ids[obj_type]
            IdFactory._increment_ids(obj_type)
        except KeyError:
            # Check if this type of object is present in defaults
            # (could happen if updates bring additional features)
            try:
                id = default_ids[obj_type]
                IdFactory.next_ids[obj_type] = id
                IdFactory._increment_ids(obj_type)
            except KeyError:
                raise ValueError(f"Object of type {obj_type} is not eligible for id assignment.")
        return id
    
    @staticmethod
    def roll_back_id(obj,previous_id):
        """
        Roll back the last id assigned to an object type. If the object given as argument was not the last of its
        kind to receive an id, this method will raise an error.
        """
        obj_type = type(obj).__name__
        try:
            previous_id = Id(previous_id)
            id = IdFactory.next_ids[obj_type]
            assert id.numeral == previous_id.numeral + 1, "Id cannot be rolled back, this is a bug" 
            IdFactory.next_ids[obj_type] = previous_id
            IdFactory._save_ids()
        except KeyError:
            raise ValueError(f"Object of type {obj_type} is not eligible for id assignment.")

    
    def _increment_ids(name):
        id = IdFactory.next_ids[name]
        id_N = id.numeral + 1
        # Ensure Ids contain at least 4 digits
        id_N = f'{id_N:04d}' if id_N < 10000 else f'{id_N}'
        next_id = Id(id.literal + id_N)
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


