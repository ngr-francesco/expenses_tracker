from member import Member
import os
import json
from list import List

from backend.utils.ids import IdFactory
from backend.utils.const import default_data_dir
from backend.cls.saveable import Saveable



class Group(Saveable):
    def __init__(self,name,members = None, data_dir = default_data_dir, load_from_file = False, load_file_path = ''):
        super().__init__()
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        self.data_dir = data_dir + 'Group_' + self.id
        if members:
            assert type(members) == list, "members argument to Group must be a list"
            assert type(members[0]) == Member, "members list must contain Member objects"
            self.members = {
                m.id: m for m in members
            }
        self.lists = {}
        self.save_data()

        if load_from_file:
            IdFactory.roll_back_id()
            self.load_from_file(load_file_path)

    @Saveable.affects_class_data(log_msg= "Added new member")
    def add_member(self,member = None,name = '', id = None):
        if not member:
            if name: 
                member = Member(name)
            elif id:
                member = Member(id)
            else:
                raise ValueError("No information regarding the member to be added was given.")
        self.members[member.id] = member
    @Saveable.affects_class_data(log_msg="Removed member")
    def remove_member(self,member = None, id = None):
        if id is None:
            id = member.id
        self.members.pop(id)
    
    @Saveable.affects_class_data(log_msg="Addded new list")
    def add_list(self,list):
        self.lists[list.id] = list
    
    @Saveable.affects_class_data(log_msg="Removed list")
    def remove_list(self,list = None, id = None):
        if id is None:
            id = list.id
        self.lists.pop(id)
    
    def summary(self):
        summary_dict = {
            'name': self.name,
            'id' : self.id,
            'data_dir': self.data_dir,
            'lists' : {
                l.id : os.path.join(l.data_dir,l.file_name) for l in self.lists
            },
            'members': {
                m.id: m.group_summary() for m in self.members
            }
        }
        return summary_dict
    
    def save_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        with open(os.path.join(self.data_dir,f'{self.id}_group_info.json'),'w+') as file:
            json.dump(self.summary(),file, indent = 4)
    
    def load_from_file(self, path):
        if not os.path.exists(path):
            raise ValueError(f"Cannot read file from inexistent path {path}")
    
        with open(path,'r') as file:
            data = json.load(file)
        for key,value in data:
            if key == 'members':
                for m_id, m_dict in value.items():
                    member = Member(id = m_id)
                    member.set_data(m_dict)
                    self.members[m_id] = member
            elif key == 'lists':
                for l_id, l_path in value.items():
                    self.lists[l_id] = List(load_from_file=True, load_file_path = l_path)
            else:
                setattr(self,key,value)
        
        
        
        

