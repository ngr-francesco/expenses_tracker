from backend.utils.const import EUROCENT, STATUS, MSG
from backend.settings import prefs
from backend.utils.logging import get_logger
from backend.cls.transactions import Transaction
from backend.utils.ids import is_uuid4
from backend.cls.saveable import Saveable
from backend.utils.decorators import requires_reload
from backend.utils.time import get_timestamp_numerical
import os, json
from backend.utils.ids import Id

default_members_file = 'all_members.json'

class SharingWeight:
    def __init__(self,name, value = 1):
        self.name = name
        self.value = value
    
    def tuple(self):
        return (self.name,self.value)


class Member(Saveable):
    
    @Saveable.takes_class_snapshot
    def __init__(self,
                 name = '',
                 id = None,
                 balance = 0,
                 spent_total = 0, 
                 sharing_weights = None, 
                 usr_id = None):
        super().__init__()
        # Id data
        # If a member is initialized through their id (no given name)
        if Id.is_id(name):
            id = name
            name = ''
        self.name = name
        self.user_id = None
        # Member data used by lists and groups
        self.involved_in = set()
        self._settled = False
        self.balance = balance
        self.spent_total = spent_total
        self.sharing_weights = sharing_weights if sharing_weights else [SharingWeight('weight')]      
        
        loaded_member = self.load(name,id)
        if loaded_member:
            # This is saved as a list so we need to convert it to a set again
            self.involved_in = set(self.involved_in)
            
        # If a usr_id was given we connect this member to that user
        if usr_id:
            self.connect_to_usr_profile(usr_id)

        self.logger.debug(f"Initialized member: {name} status: {self.status} for amount: {balance}")
        self.save_data()

    @property
    def status(self):
        if abs(self.balance) < EUROCENT:
            return STATUS.SettledUp
        elif self.balance > 0:
            return STATUS.Creditor
        
        return STATUS.Debitor

    @Saveable.affects_metadata(log_msg="Changed member balance")
    def add_to_balance(self,amount):
        self.balance += amount

    @Saveable.affects_metadata(log_msg="Changed member spent total")
    def add_to_spent_total(self,amount):
        self.spent_total += amount

    @Saveable.affects_metadata(log_msg="Connected member to user profile")
    def connect_to_usr_profile(self,usr_id):
        if usr_id is None:
            raise ValueError(f"Member {self.name} {self.id} is already connected to usr id {usr_id}. Cannot connect to new user.")
        if not is_uuid4(usr_id):
            raise ValueError(f"Given user id is not uuid4: {usr_id}")
        self.user_id = usr_id
    
    def is_connected_to_usr_profile(self):
        """
        Check if this member is connected to an external user profile
        """
        return self.user_id is not None
        
    @Saveable.takes_class_snapshot
    def set_data(self,data_dict):
        """
        Used to load data when initializing a list or a group. The data stored by these objects
        will set the attributes of this particular instance of Member, without affecting its unique identifiers
        (name, id, user_id)
        """
        id_check = self.id == data_dict['id']
        if not id_check:
            raise ValueError(f"Trying to set member data from unrecognized member." 
                             f"Current member: {self.name}_{self.id}. Given data: {data_dict['id']}")
        
        for key,value in data_dict.items():
            if key == 'sharing_weights':
                value = [SharingWeight(*v) for v in value]
            if hasattr(self,key):
                setattr(self,key,value)
            else:
                self.logger.debug(f"Attribute {key} retrieved from data_dict is not in Member class attributes, ignoring it.")
    
    def is_settled(self):
        if not self._settled and abs(self.balance) < EUROCENT:
            self._settled = True
            self.balance = 0
        return self._settled

    def member_summary(self):
        """
        Only member summary contains the member name. Since this can be
        changed by the user, we don't want to rely on it too much.
        """
        summary_dict = {
            'id' : self.id,
            'name' : self.name,
            'user_id': self.user_id,
            'time_created': self.time_created,
            'involved_in': list(self.involved_in)
        }
        return summary_dict
    
    def balance_summary(self):
        # This is only saved within 
        summary_dict = {
            'id': self.id,
            'status': str(self.status),
            "balance": self.balance,
            '_settled': self.is_settled(),
            "spent_total": self.spent_total,
        }
        return summary_dict
    
    def extended_summary(self):
        return self.balance_summary()
    
    def list_summary(self):
        """
        Within lists we can have different sharing weights to be used to calculate
        list-item shares. These should not be imported from groups, since they're not needed.
        """
        summary_dict = self.balance_summary()
        summary_dict['sharing_weights'] = [weight.tuple() for weight in self.sharing_weights]
        return summary_dict
    
    @Saveable.affects_metadata(log_msg="Renamed member.")
    @requires_reload
    def rename(self,new_name: str):
        print("Renaming member")
        file_path = os.path.join(prefs.data_dir,default_members_file)
        # We need to remove the old entry in the all_members file
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data_dict = json.load(file)
            # Check for name clashes
            if new_name in data_dict['members_from_name']:
                self.logger.warning("Name would clash with pre-existing member name. Aborting...")
                return -1
            if self.id in data_dict['members_from_id'] and self.name in data_dict['members_from_name']:
                data_dict["members_from_id"].pop(self.id)
                data_dict['members_from_name'].pop(self.name)
        self.name = new_name
        return 0


    def save_data(self):
        member_dict = self.member_summary()
        file_path = os.path.join(prefs.data_dir,default_members_file)
        if os.path.exists(file_path):
            with open(file_path,'r') as file:
                data_dict = json.load(file)
            if self.id in data_dict['members_from_id'] and data_dict['members_from_id'][self.id]['name'] != self.name:
                raise Exception("Two members share the same id, this is a bug.")
            
            data_dict['members_from_id'][self.id] = member_dict
            data_dict['members_from_name'][self.name] = member_dict
        else:
            data_dict = {
                'members_from_id': {self.id: member_dict},
                'members_from_name': {self.name: member_dict}
            }
            
        # Member data is only saved in the all_members file, other data 
        # structures will only reference the members through their ids.
        with open(file_path, 'w+') as file:
            json.dump(data_dict, file, indent=4)
        self.logger.debug(f"Saved member data for {self.name}, with id: {self.id} to file {file_path}")

    def load(self,name = '', id = None):
        file_path = os.path.join(prefs.data_dir,default_members_file)
        member_dict = {}
        # When reloading this is the case!
        if not name and not id and len(self.name):
            name = self.name

        if os.path.isfile(file_path):
            with open(file_path,'r') as file:
                data = json.load(file)
                if id and id in data['members_from_id']:
                    member_dict = data['members_from_id'][id]
                elif id is None and name in data['members_from_name']:
                    member_dict = data['members_from_name'][name]
                else:
                    self.logger.warning(f"Member {name} with given id: {id} was not found in members file.")
                    return False
            if not 'name' in member_dict:
                raise ValueError(f"Member entry for member {id} doesn't have a name. This should never happen.")
                
            for key,value in member_dict.items():
                setattr(self,key,value)
            return True
        else:
            self.logger.debug("Trying to load member data from non-existing file. If you're making a new member it's all good.")
            return False

class MembersList:
    def __init__(self, owner: Saveable = None, members = None):
        self.logger = get_logger(type(self).__name__)
        self.members_by_id = {}
        self.members_by_name = {}
        # Reports are only useful for Saveable classes (assured to have a data_dir, even if set to None)
        self.reports_dir = None
        self.owner_id = None
        if isinstance(owner,Saveable):
            self.reports_dir = os.path.join(owner.data_dir,'balance_summaries')
            self.owner_id = owner.id
        self.summary_type = 'list_summary' if type(owner).__name__ =='List' else 'extended_summary'
        self.index = 0
        if members:
            assert isinstance(members,(list)), f"Arg. 'members' expected to be of type {type(list)}, got {type(members)}."
            assert type(members[0]) == Member, f"Arg. 'members' must contain {Member} objects"
            for member in members:
                self.add_member(member)
            
    ids = property(lambda self: [id for id in self.members_by_id])
    names = property(lambda self: [name for name in self.members_by_name])
    debitors = property(lambda self : [m for m in self.members_by_id.values() if m.status == STATUS.Debitor])
    creditors = property(lambda self : [m for m in self.members_by_id.values() if m.status == STATUS.Creditor])

    def get_by_name(self, name):
        return self.members_by_name[name]

    def get_by_id(self, id):
        return self.members_by_id[id]
    
    def get(self,name_or_id):
        """
        Generalized get function with a bit of overhead.
        """
        if name_or_id in self.members_by_id and name_or_id in self.members_by_name:
            raise ValueError(f"Something is wrong, given name or id is in both by_id and by_name dictionaries {name_or_id}.")
        if name_or_id in self.members_by_id:
            return self.get_by_id(name_or_id)
        if name_or_id in self.members_by_name:
            return self.get_by_name(name_or_id)

    def summary(self):
        return {member.id : getattr(member,self.summary_type)() for member in self}

    def add_member(self, member: Member):
        if member in self:
            self.logger.warning(f"Member already in MemberList {member.name}{member.id}")
            return
        if self.owner_id:
            member.involved_in.add(self.owner_id)
        self.members_by_id[member.id] = member
        self.members_by_name[member.name] = member
    
    def add_member_from_dict(self,m_dict : dict):
        member = Member(id = m_dict["id"])
        member.set_data(m_dict)
        self.add_member(member)
    
    def load_members_from_dict(self, data_dict : dict):
        for m_dict in data_dict.values():
            self.add_member_from_dict(m_dict)

    def remove_member(self,member : Member):
        if isinstance(member,str):
            member = self.get(member)
        if not member in self:
            self.logger.warning(f"Member not in MemberList {member.name}{member.id}")
            return
        if self.owner_id:
            member.involved_in.remove(self.owner_id)
        self.members_by_id.pop(member.id)
        self.members_by_name.pop(member.name)
    
    def balance_report(self, save_to_file = False):
        if self.reports_dir is None:
            self.logger.warning("Saving reports is not supported for this instance of MembersList.")
            return

        bal_report = {
            m.name : m.balance_summary() for m in self.members_by_name
        }
        if save_to_file:
            if not os.path.exists(self.reports_dir):
                os.makedirs(self.reports_dir)
            file_name = f'balance_summary_{get_timestamp_numerical()}.json'
            with open(os.path.join(self.reports_dir,file_name),'w+') as file:
                json.dump(bal_report, file, indent = 4)
        return bal_report
    
    def sort_by_balance(self,descending = True):
        return dict(sorted(self.members_by_id.items(),key = lambda item: item[1].balance, reverse = descending))
    
    def sort_by_partial_amount(self, descending = True):
        """
        Useful for settling up.
        """
        return dict(sorted(self.members_by_id.items(),key = lambda item: item[1].partial_amount, reverse = descending))        
    
    # Dunder overloads
    def __contains__(self,member):
        return member.id in self.members_by_id and member.name in self.members_by_name
    
    def __iter__(self):
        self.index = 0
        return self
    
    def __next__(self):
        if self.index < len(self.members_by_id):
            next_item = list(self.members_by_id.values())[self.index]
            self.index += 1
            return next_item
        else:
            raise StopIteration
    
    def __len__(self):
        return len(self.members_by_id)



    
    