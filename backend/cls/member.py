from backend.utils.const import EUROCENT, STATUS, MSG
from backend.utils.logging import get_logger
from backend.cls.transaction import Transaction
from backend.utils.ids import is_uuid4
from backend.cls.saveable import Saveable
from backend.utils.decorators import requires_reload
from backend.utils.const import default_data_dir
import os, json

default_members_file = 'all_members.json'

class MembersList:
    def __init__(self, members = None):
        self.logger = get_logger(type(self).__name__)
        self.members_by_id = {}
        self.members_by_name = {}
        self.index = 0
        if members:
            assert isinstance(members,(list,MembersList)), "members argument to List must be a list or MembersList"
            assert type(members[0]) == Member, "members list must contain Member objects"
            for member in members:
                self.add_member(member)
            
    @property
    def ids(self):
        return [id for id in self.members_by_id]
    @property
    def names(self):
        return [name for name in self.members_by_name]

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
        return {member.id : member.extended_summary() for member in self}

    def load_from_file(self, file_path):
        pass

    def add_member(self, member):
        if member in self:
            self.logger.warning(f"Member already in MemberList {member.name}{member.id}")
            return
        self.members_by_id[member.id] = member
        self.members_by_name[member.name] = member
    
    def add_member_from_dict(self,m_dict):
        member = Member(m_dict["id"])
        member.set_data(m_dict)
        self.add_member(member)
    
    def load_members_from_dict(self, data_dict):
        for m_dict in data_dict.values():
            self.add_member_from_dict(m_dict)

    def remove_member(self,member):
        if isinstance(member,str):
            member = self.get(member)
        if not member in self:
            self.logger.warning(f"Member not in MemberList {member.name}{member.id}")
            return
        self.members_by_id.pop(member.id)
        self.members_by_name.pop(member.name)
    
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


class Member(Saveable):
    def __init__(self,name = '',
                 balance = 0,
                 status = None, 
                 spent_total = 0, 
                 days_spent = 0, 
                 id = None,
                 usr_id = None,
                 new_member = False):
        super().__init__()
        # Id data
        self.name = name
        self.user_id = None
        # Member data used by lists and groups
        self._settled = False
        self.status = status
        self.balance = balance
        self.spent_total = spent_total
        self.days_spent = days_spent
        self.transactions = []
        # Quantities required to calculate balances
        self.partial_amount = 0
        self.init_amount = 0

        self.logger.debug(f"Initialized member: {name} status: {status} for amount: {balance}")
        
        
        if not new_member:
            loaded_member = self.load(name,id)
            
        # If a usr_id was given we connect this member to that user
        if usr_id:
            self.connect_to_usr_profile(usr_id)
        self.save_data()
            
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
    
    def load(self,name = '', id = None):
        file_path = os.path.join(default_data_dir,default_members_file)
        member_dict = {}
        # When reloading this is the case
        if not name and not id and len(self.name):
            name = self.name

        if os.path.exists(file_path):
            with open(os.path.join(default_data_dir,default_members_file),'r') as file:
                data = json.load(file)
                if id and id in data['members_from_id']:
                    member_dict = data['members_from_id'][id]
                elif id is None and name in data['members_from_name']:
                    member_dict = data['members_from_name'][name]
                else:
                    self.logger.warning(f"Member {name} with given id: {id} was not found in members file.")
                    return
                
            for key,value in member_dict.items():
                setattr(self,key,value)
            return True
        else:
            self.logger.warning("Trying to load member data from non-existing file.")
            return False
    
    def set_data(self,data_dict):
        """
        Used to load data when initializing a list or a group. The data stored by these objects
        will set the attributes of this particular instance of Member, without affecting its unique identifiers
        (name, id, user_id)
        """
        id_check = all(x==y for x,y in [(self.name,data_dict['name']),
                                            (self.id,data_dict['id']),
                                            (self.user_id, data_dict['user_id'])])
        if not id_check:
            raise ValueError(f"Trying to set member data from unrecognized member." 
                             f"Current member: {self.name}{self.id}. Given data: {data_dict['name']}{data_dict['id']}")
        
        for key,value in data_dict.items():
            if hasattr(self,key):
                setattr(self,key,value)
            else:
                self.logger.debug(f"Attribute {key} retrieved from data_dict is not in Member class attributes, ignoring it.")
    
    def is_settled(self):
        if not self._settled and self.partial_amount < EUROCENT:
            self._settled = True
            self.partial_amount = 0
        return self._settled
    
    def begin_settle_up(self):
        self.logger.debug(f"Preparing to settle up {self.name}, balance = {self.balance}")
        self.init_amount = abs(self.balance)
        self.partial_amount = self.init_amount
    
    @Saveable.affects_metadata(log_msg="Settled up member")
    def finalize_settle_up(self):
        if not self.is_settled():
            raise ValueError(f"Member {self.name} is not settled, yet. Can't finalize settling up process.")
        self.clear_transactions()
        self.balance = 0
        self.partial_amount = 0
        self.spent_total -= self.balance
        del self.init_amount

    @Saveable.affects_metadata(log_msg="Clearing transactions list")   
    def clear_transactions(self):
        if not self.is_settled():
            self.logger.warning("You are clearing the transaction of a member which is not yet settled up."
                                " this will most likely affect the overall balance of this group/list")
        self.transactions = []
        self.logger.debug("Saving member data after clearing transactions")
    
    @Saveable.affects_metadata(log_msg="Processing transaction to/from other member")
    def process_transaction(self,person,amount):
        if self.is_settled():
            self.logger.warn("You are about to make a transaction with a settled up person. This is rarely the intended behavior.")
        self.partial_amount -= amount
        if self.status == STATUS.Debitor:
            sender = self
            receiver = person
        else:
            sender = person
            receiver = self
        sent_received = MSG.SENT if self.status == STATUS.Debitor else MSG.RECEIVED
        transaction = Transaction(sender = sender,receiver= receiver, amount = round(amount,2),sent_received = sent_received)
        if self.partial_amount < -EUROCENT:
            raise ValueError(f"This transaction between {self.name} to {person.name} for {amount}€ surpasses the partial"
                             f" amount of {self.name} of {self.partial_amount}")
        self.transactions.append(transaction)

    def member_summary(self):
        """
        Only member summary contains the member name. Since this can be
        changed by the user, we don't want to rely on it too much.
        """
        summary_dict = {
            'id' : self.id,
            'name' : self.name,
            'user_id': self.user_id,
            'time_created': self.time_created
        }
        return summary_dict
    
    def transaction_summary(self):
        summary_dict = {
            'id': self.id,
            'status': str(self.status),
            "balance": self.balance,
            'transactions': [str(trans) for trans in self.transactions], 
            'settled': self.is_settled(),
        }
        return summary_dict
    
    def balance_summary(self):
        summary_dict = {
            'id': self.id,
            'status': str(self.status),
            "balance": self.balance,
            '_settled': self.is_settled(),
            "spent_total": self.spent_total,
            "days_spent": self.days_spent,
            
        }
        return summary_dict
    
    def extended_summary(self):
        return self.balance_summary()
    
    def group_summary(self):
        return self.balance_summary()
    
    def __json__(self):
        return self.id
    
    @Saveable.affects_metadata(log_msg="Renamed member.")
    @requires_reload
    def rename(self,new_name: str):
        file_path = os.path.join(default_data_dir,default_members_file)
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
        file_path = os.path.join(default_data_dir,default_members_file)
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


    
    