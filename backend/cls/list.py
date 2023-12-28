from backend.utils.logging import get_logger
import os, json
import typing as ty

from backend.cls.member import Member, MembersList
from backend.cls.saveable import Saveable
from backend.utils.const import default_data_dir, EUROCENT
from backend.utils.time import get_timestamp_numerical
from backend.cls.object_with_id import ObjectWithId

from enum import Enum

PERCENTAGE_MAX_ERROR = 0.01

class SharingMethods(Enum):
    EQUAL = 0
    PERCENTAGES = 0
    AMOUNTS = 0


class ListItem(ObjectWithId):
    def __init__(self,name,bought_by,amount = 0,members_involved = MembersList(), sharing_method = SharingMethods.EQUAL, percentages = {}, amounts = {}, **kwargs):
        super().__init__()
        self.logger = get_logger(type(self).__name__)
        self.name = name
        self.bought_by = bought_by
        self.amount = amount
        self.members_involved = members_involved
        self.shares = self.calculate_shares(sharing_method, percentages, amounts)

    def calculate_shares(self,sharing_method, percentages = {}, amounts = {}):
        shares = {}

        if sharing_method == SharingMethods.EQUAL:
            shares = {m.id : self.amount/len(self.members_involved) for m in self.members_involved}

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
            'bought_by': self.bought_by.id,
            'members_involved': [m.id for m in self.members_involved],
            'shares': [(m.name,self.shares[m.id]) for m in self.members_involved],
            'time_created': get_timestamp_numerical()
        }
        return summary_dict
    
    def __str__(self):
        printable_summary = json.dumps(self.summary(), indent=4)
        return printable_summary

default_lists_dir = os.path.join(default_data_dir,'ungrouped_lists')

class List(Saveable):
    def __init__(self,name:str, 
                 members: ty.List[ty.Union[str,Member]], 
                 data_dir: str = default_lists_dir, 
                 file_name: str = "list_info.json", 
                 group_name: str = None,
                 load_from_file: bool = False, 
                 load_file_path = '',
                 cycle_length = None):
        super().__init__()
        self.name = name
        
        self.members = MembersList(members)

        self.items = {}
        self.file_name = f'{self.id}_{file_name}'
        self.data_dir = os.path.join(data_dir , f'List_{self.id}')
        self.group_name = group_name
        self.cycle_length = cycle_length
        # To make sure all the required attributes were set I first
        # set them, then if the list should be loaded from file, we load it.
        if load_from_file:
            list_loaded = self.load(load_file_path)
        
    @Saveable.affects_metadata(log_msg="Adding item to list")   
    def add_item(self,item: ty.Union[dict,ListItem]):
        if not isinstance(item, ListItem):
            item = ListItem(*item)
        self.items[item.id] = item
    
    @Saveable.affects_metadata(log_msg="Removing item from list")
    def remove_item(self,id):
        try:
            self.items.pop(id)
        except KeyError:
            self.logger.warning(f"Item not in list {id}")
    
    @Saveable.affects_metadata(log_msg="Editing item in list")
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
    
    def load(self,file_path = ''):
        if file_path == '':
            file_path = os.path.join(self.data_dir,self.file_name)
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data = json.load(file)

            for key,value in data.items():
                if key == 'members':
                    self.members.load_members_from_dict(value)

                elif key == 'items':
                    for id, item in value.items():
                        item_data = self.preprocess_item_data(item)
                        
                        self.items[id] = ListItem(*item_data)
                        
                elif hasattr(self,key) and not key == 'members':
                    self.logger.diagnostic(f"Setting list attribute {key} = {value}")
                    setattr(self,key,value)
                        
                self.data_dir = os.path.dirname(file_path)
                self.file_name = os.path.basename(file_path)

            self.logger.debug(f"Loaded list data from file {file_path}")
            return True
        else:
            self.logger.warning(f"Tried to load from non-existing file {file_path}")
            return False
        
    def preprocess_item_data(self,item_dict):
        """
        Since when saving item data we only save ids of users,
        here we preprocess their ids and return the actual member classes.
        """

        buyer_id = item_dict['bought_by']
        item_dict['bought_by'] = self.members.get_by_id(buyer_id)

        members_involved = item_dict['members_involved']
        item_dict['members_involved'] = {
            m_id: self.members.get_by_id(m_id) for m_id in members_involved
        }

        return item_dict
    
    def save_data(self):
        self.logger.debug(f"Saving data from list to {self.data_dir}/{self.file_name}")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        dict_to_save = {
            'name': self.name,
            'data_dir': self.data_dir,
            'id': self.id,
            'time_created': self.time_created,
            'members': self.members.summary(),
            'items': {item.id: item.summary() for item in self.items.values()},
            
        }
        self.logger.diagnostic(json.dumps(dict_to_save,indent = 4))
        file_path = os.path.join(self.data_dir,self.file_name)
        with open(file_path, 'w+') as file:
            json.dump(dict_to_save, file, indent = 4)
        self.logger.debug("Successfully saved list data to disk")
    
    @Saveable.affects_metadata("Adding member to list's included members")
    def add_member(self,member):
        # If an Id to be loaded from files is given, it will be a string
        if isinstance(member, str):
            member = Member(member)
        if member.id in self.members.ids:
            raise ValueError(f"The member you're trying to add is already in this List {member.name}")
        self.members.add_member(member)

        
    
