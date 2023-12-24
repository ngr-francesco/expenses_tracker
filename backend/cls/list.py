from backend.utils.logging import get_logger
import os, json, shutil
import typing as ty

from backend.cls.member import Member
from backend.cls.saveable import Saveable
from backend.utils.ids import IdFactory
from backend.utils.const import default_data_dir, EUROCENT
import numpy as np

from enum import Enum

PERCENTAGE_MAX_ERROR = 0.01

class SharingMethods(Enum):
    EQUAL = 0
    PERCENTAGES = 0
    AMOUNTS = 0


class ListItem():
    def __init__(self,name,bought_by,amount = 0,members_involved = {}, sharing_method = SharingMethods.EQUAL, percentages = {}, amounts = {}, **kwargs):
        self.logger = get_logger(type(self).__name__)
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        self.bought_by = bought_by
        self.amount = amount
        self.members_involved = members_involved
        self.shares = self.calculate_shares(sharing_method, percentages, amounts)

    def calculate_shares(self,sharing_method, percentages = {}, amounts = {}):
        shares = {}

        if sharing_method == SharingMethods.EQUAL:
            shares = {m : self.amount/len(self.members_involved) for m in self.members_involved}

        elif sharing_method == SharingMethods.PERCENTAGES:
            if not sum(list(percentages.values())) - 1 < PERCENTAGE_MAX_ERROR:
                raise ValueError("The given list of percentages doesn't add up to 1!")
            if not list(percentages.keys()) == self.members_involved.keys():
                raise ValueError("The percentages don't cover all members involved or have extra members."
                                 f"members: {self.members_involved.keys()}, percentages: {percentages.keys()}")
            
            shares = {m : self.amount*percentage for m,percentage in percentages.items()}

        elif sharing_method == SharingMethods.AMOUNTS:
            if not sum(list(amounts.values())) - self.amount < EUROCENT:
                raise ValueError("The given amounts for the sharing method are not summing up to the total."
                                 f"Summed amounts: {sum(list(amounts.values()))}, spent amount: {self.amount}")
            if not list(percentages.keys()) == self.members_involved.keys():
                raise ValueError("The amounts given don't cover all members involved or have extra members."
                                 f"members: {self.members_involved.keys()}, percentages: {amounts.keys()}")
            
            shares = {m : a for m,a in amounts.items()}

        return shares
    
    def summary(self):
        summary_dict = {
            'name': self.name,
            'id': self.id,
            'bought_by': self.bought_by,
            'members_involved': [m for m in self.members_involved],
            'shares': [(m.name,self.shares[m]) for m in self.members_involved]
        }
        return summary_dict
    
    def __str__(self):
        printable_summary = json.dumps(self.summary(), indent=4)
        return printable_summary
    
    def __json__(self):
        return self.summary()


class List(Saveable):
    def __init__(self,name:str, 
                 members: ty.List[ty.Union[dict,Member]], 
                 data_dir: str = default_data_dir, 
                 file_name: str = "list_info.json", 
                 load_from_file: bool = False, 
                 load_file_path = '', 
                 cycle_length = None):
        super().__init__()
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        if members:
            assert type(members) == list, "members argument to List must be a list"
            assert type(members[0]) == Member, "members list must contain Member objects"
            self.members = {
                m.id: m for m in members
            }

        self.items = {}
        self.file_name = f'{self.id}_{file_name}'
        self.data_dir = os.path.join(data_dir , f'List_{self.id}')
        self.cycle_length = cycle_length
        if load_from_file:
            self.load(load_file_path)
            IdFactory.roll_back_id(self)
    @Saveable.affects_class_data(log_msg="Adding item to list")   
    def add_item(self,item: ty.Union[dict,ListItem]):
        if not isinstance(item, ListItem):
            item = ListItem(*item)
        self.items[item.id] = item
    
    @Saveable.affects_class_data(log_msg="Removing item from list")
    def remove_item(self,id):
        try:
            self.items.pop(id)
        except KeyError:
            self.logger.warning(f"Item not in list {id}")
    
    @Saveable.affects_class_data(log_msg="Editing item in list")
    def edit_item(self,id,key,value):
        if type(value) != type(self.items[id][key]):
            raise ValueError(f"Existing key {key}:{self.items[id][key]} has different type than given key {value}")
        self.items[id][key] = value
    
    def total_spent_per_member(self):
        for item in self.list.items:
            for m in self.members:
                try:
                    pass
                except:
                    pass
    
    def load(self,file_path):
        if file_path == '':
            file_path = os.path.join(self.data_dir,self.file_name)
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data = json.load(file)
            for key,value in data.items():
                if key == 'members':
                    for id,member_dict in value.items():
                        self.members[id] = Member(*member_dict)
                elif key == 'items':
                    for id, item in value.items():
                        self.items[id] = ListItem(*item)
                elif hasattr(self,key) and not key == 'members':
                    self.logger.diagnostic(f"Setting list attribute {key} = {value}")
                    setattr(self,key,value)
                        
                self.data_dir = os.path.dirname(file_path)
                self.file_name = os.path.basename(file_path)

            self.logger.debug(f"Loaded list data from file {file_path}")
        else:
            self.logger.warning(f"Tried to load from non-existing file {file_path}")
    
    def save_data(self):
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
    
    @Saveable.affects_class_data("Adding member to list's included members")
    def add_member(self,member):
        if not isinstance(member, Member):
            member = Member(*member)
        self.members[member.id] = member

        
    
