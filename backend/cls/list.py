from utils.logging import get_logger
import os, json, shutil
from member import Member

class ListItem:
    def __init__(self,name,id,owner,amount = 0,members_involved = {}):
        self.name = name
        self.id = id
        self.owner = owner
        self.amount = amount
        self.members_involved = members_involved
        

class List:
    def __init__(self,name:str, members: dict, data_dir: str, file_name: str, load_from_file: bool):
        self.logger = get_logger(self.__name__)
        self.name = name
        self.members = members
        self.items = {}
        self.file_name = file_name
        self.data_dir = data_dir
        if load_from_file:
            self.load()
        
    def add_item(self,id,item):
        self.items[id] = item
    
    def remove_item(self,id):
        try:
            self.items.pop(id)
        except KeyError:
            self.logger.warning(f"Item not in list {id}")
    
    def edit_item(self,id,key,value):
        if type(value) != type(self.items[id][key]):
            raise ValueError(f"Existing key {key}:{self.items[id][key]} has different type than given key {value}")
        self.items[id][key] = value
    
    def load(self):
        file_path = os.path.join(self.data_dir,self.file_name)
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data = json.load(file)
            for key,value in data.items():
                if hasattr(self,key) and not key == 'members':
                    self.logger.diagnostic(f"Setting list attribute {key} = {value}")
                    setattr(self,key,value)
                if key == 'members':
                    for name,member_dict in value.items():
                        self.members[name] = Member(member_dict)

            self.logger.debug(f"Loaded list data from file {file_path}")
        else:
            self.logger.warning(f"Tried to load from non-existing file {file_path}")
    
    def save(self):
        self.logger.debug(f"Saving data from list to {self.data_dir}/{self.file_name}")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        members_dict = {member.name : member.summary() for member in self.members}
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

        
    
