from backend.utils.const import EUROCENT, STATUS, MSG
from backend.utils.logging import get_logger
from backend.utils.ids import IdFactory
from backend.cls.transaction import Transaction
from backend.utils.ids import is_uuid4
from backend.cls.saveable import Saveable
from backend.utils.const import default_data_dir
import os, json

default_members_file = 'all_members.json'

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
        if new_member:        
            self.name = name
            self.usr_id = None
            # If we're loading a member
            if id is not None:
                self.id = id
            # If we're initializing a new member
            else:
                self.id = IdFactory.get_obj_id(self)
            self._settled = False
            self.status = status
            self.balance = balance
            self.spent_total = spent_total
            self.days_spent = days_spent
            self.transactions = []
            self.logger.debug(f"Initialized member: {name} status: {status} for amount: {balance}")
            self.save_data()
        else:
            member_dict = self.load_from_members_file(name,id)
            for key,value in member_dict.items():
                setattr(self,key,value)
        # If a usr_id was given we connect this member to that user
        if usr_id:
            self.connect_to_usr_profile(usr_id)
            
    @Saveable.affects_class_data(log_msg="Connected member to user profile")
    def connect_to_usr_profile(self,usr_id):
        if usr_id is None:
            raise ValueError(f"Member {self.name} {self.id} is already connected to usr id {usr_id}. Cannot connect to new user.")
        if not is_uuid4(usr_id):
            raise ValueError(f"Given user id is not uuid4: {usr_id}")
        self.usr_id = usr_id
    
    def is_connected_to_usr_profile(self):
        """
        Check if this member is connected to an external user profile
        """
        return self.usr_id is not None
    
    def load_from_members_file(self,name = '', id = None):
        with open(os.path.join(default_data_dir,default_members_file),'r') as file:
            data = json.load(file)
            if id:
                member_dict = data['members_from_id'][id]
            else:
                member_dict = data['members_from_name'][name]
        return member_dict
    
    def is_settled(self):
        if not self._settled and self.partial_amount < EUROCENT:
            self._settled = True
            self.partial_amount = 0
        return self._settled
    
    def begin_settle_up(self):
        self.logger.debug(f"Preparing to settle up {self.name}, balance = {self.balance}")
        self.init_amount = abs(self.balance)
        self.partial_amount = self.init_amount
    
    @Saveable.affects_class_data(log_msg="Settled up member")
    def finalize_settle_up(self):
        if not self.is_settled():
            raise ValueError(f"Member {self.name} is not settled, yet. Can't finalize settling up process.")
        self.clear_transactions()
        self.balance = 0
        self.partial_amount = 0
        self.spent_total -= self.balance
        del self.init_amount

    @Saveable.affects_class_data(log_msg="Clearing transactions list")   
    def clear_transactions(self):
        if not self.is_settled():
            self.logger.warning("You are clearing the transaction of a member which is not yet settled up."
                                " this will most likely affect the overall balance of this group/list")
        self.transactions = []
        self.logger.debug("Saving member data after clearing transactions")
        self.save_data()
    
    @Saveable.affects_class_data(log_msg="Processing transaction to/from other member")
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
        summary_dict = {
            'id' : self.id,
            'name' : self.name,
            'user_id': self.usr_id
        }
        return summary_dict
    
    def transaction_summary(self):
        summary_dict = self.member_summary()
        summary_dict.update({
            'status': str(self.status),
            "balance": self.balance,
            'transactions': [str(trans) for trans in self.transactions], 
            'settled': self.is_settled(),
        })
        return summary_dict
    
    def balance_summary(self):
        summary_dict = self.member_summary()
        summary_dict.update({
            'status': str(self.status),
            "balance": self.balance,
            '_settled': self.is_settled(),
            "spent_total": self.spent_total,
            "days_spent": self.days_spent,
            
        })
        return summary_dict
    
    def __json__(self):
        pass

    def save_data(self):
        dict_to_save = self.balance_summary()
        #TODO: Finish this

    
    