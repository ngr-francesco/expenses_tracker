from utils.logging import get_logger
import os, json, shutil

from backend.cls.member import Member
from backend.utils.id_factory import IdFactory
from backend.utils.const import default_data_dir

class ListItem:
    def __init__(self,name,owner,amount = 0,members_involved = {}):
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        self.owner = owner
        self.amount = amount
        self.members_involved = members_involved
        

class List:
    def __init__(self,name:str, members: dict, data_dir: str = default_data_dir, file_name: str = "list_info.json", load_from_file: bool = False, load_file_path = ''):
        self.logger = get_logger(List.__name__)
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        self.members = members
        self.items = {}
        self.file_name = f'{self.id}_{file_name}'
        self.data_dir = os.path.join(data_dir , f'List_{self.id}')
        if load_from_file:
            self.load(load_file_path)
            IdFactory.roll_back_id(self)
        
    def add_item(self,item):
        self.items[item.id] = item
    
    def remove_item(self,id):
        try:
            self.items.pop(id)
        except KeyError:
            self.logger.warning(f"Item not in list {id}")
    
    def edit_item(self,id,key,value):
        if type(value) != type(self.items[id][key]):
            raise ValueError(f"Existing key {key}:{self.items[id][key]} has different type than given key {value}")
        self.items[id][key] = value
    
    def load(self,file_path):
        if file_path == '':
            file_path = os.path.join(self.data_dir,self.file_name)
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data = json.load(file)
            for key,value in data.items():
                if hasattr(self,key) and not key == 'members':
                    self.logger.diagnostic(f"Setting list attribute {key} = {value}")
                    setattr(self,key,value)
                if key == 'members':
                    for id,member_dict in value.items():
                        self.members[id] = Member(*member_dict)
                        
                self.data_dir = os.path.dirname(file_path)
                self.file_name = os.path.basename(file_path)

            self.logger.debug(f"Loaded list data from file {file_path}")
        else:
            self.logger.warning(f"Tried to load from non-existing file {file_path}")
    
    def save(self):
        self.logger.debug(f"Saving data from list to {self.data_dir}/{self.file_name}")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        members_dict = {member.id : member.summary() for member in self.members}
        dict_to_save = {
            'name': self.name,
            'members': members_dict,
            'items': self.items
        }
        self.logger.diagnostic(json.dumps(dict_to_save,indent = 4))
        file_path = os.path.join(self.data_dir,self.file_name)
        with open(file_path) as file:
            json.dump(dict_to_save, file)
        self.logger.debug("Successfully saved list data to disk")

        
    
