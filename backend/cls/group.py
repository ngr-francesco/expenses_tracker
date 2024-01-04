from member import Member, MembersList
import os
import json
from list import List

from backend.utils.const import default_data_dir
from backend.cls.saveable import Saveable



class Group(Saveable):
    @Saveable.takes_class_snapshot
    def __init__(self,name,members = None, data_dir = default_data_dir, load_from_file = False, load_file_path = ''):
        super().__init__()
        self.name = name
        self.data_dir = data_dir + 'Group_' + self.id
        self.file_name = f'{self.id}_group_info.json'
        self.members = MembersList(self,members)
        self.lists = {}
        self.save_data()

        if load_from_file:
            group_loaded = self.load(load_file_path)


    @Saveable.affects_metadata(log_msg= "Added new member")
    def add_member(self,member = None,name = '', id = None):
        if not member:
            if name: 
                member = Member(name)
            elif id:
                member = Member(id)
            else:
                raise ValueError("No information regarding the member to be added was given.")
        self.members.add_member(member)

    @Saveable.affects_metadata(log_msg="Removed member")
    def remove_member(self,member = None, id = None):
        if id is None:
            id = member.id
        self.members.remove_member(id)
    
    @Saveable.affects_metadata(log_msg="Addded new list")
    def add_list(self,list):
        self.lists[list.id] = list
    
    @Saveable.affects_metadata(log_msg="Removed list")
    def remove_list(self,list = None, id = None):
        if id is None:
            id = list.id
        self.lists.pop(id)
    
    def summary(self):
        summary_dict = {
            'name': self.name,
            'id' : self.id,
            'data_dir': self.data_dir,
            'time_created': self.time_created,
            'lists' : {
                l.id : os.path.join(l.data_dir,l.file_name) for l in self.lists
            },
            'members': {
                m.id: m.group_summary() for m in self.members.values()
            }
        }
        return summary_dict
    
    def save_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        with open(os.path.join(self.data_dir,self.file_name),'w+') as file:
            json.dump(self.summary(),file, indent = 4)

    def load(self, path= None):
        # It's the case when reloading the backend
        if not path:
            path = os.path.join(self.data_dir, self.file_name)

        if not os.path.exists(path):
            self.logger.warning(f"Cannot read file from inexistent path {path}")
            return False
        
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
        return True
        
        
        
        

