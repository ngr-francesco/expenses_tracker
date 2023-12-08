from utils.id_factory import IdFactory
from member import Member
import os
import json
from utils.const import default_data_dir
from list import List


class Group:
    def __init__(self,name,members = None, data_dir = default_data_dir, load_from_file = False, load_file_path = ''):
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
        if load_from_file:
            self.load_from_file(load_file_path)
            IdFactory.roll_back_id(self)

    def add_member(self,member = None,name = ''):
        if not member:
            if name == '':
                raise ValueError("Either member or name of new member must be specified!")
            member = Member(name)
        self.members[member.id] = member
    
    def remove_member(self,member = None, id = None):
        if id is None:
            id = member.id
        self.members.pop(id)
    
    def add_list(self,list):
        self.lists[list.id] = list
    
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
                m.id : m.member_summary() for m in self.members
            }
        }
        return summary_dict
    
    def save_group_info(self):
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
            setattr(self,key,value)
        
        for l_id, l_path in self.lists:
            self.lists[l_id] = List(load_from_file=True, load_file_path = l_path)
        
        for m_id, m_dict in self.members:
            self.members[m_id] = Member(*m_dict)
