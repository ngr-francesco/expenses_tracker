import os
import json

from backend.cls.object_with_id import ObjectWithId
from backend.cls.saveable import Saveable
from backend.utils.const import MSG
from backend.settings import prefs
from backend.utils.time import get_timestamp_numerical

def get_transaction_info_from_id(transaction_id,path):
    if not os.path.exists(path):
        raise FileNotFoundError("Path to transactions list is not in system.")
    with open(path,'r') as file:
        data = json.load(file)

    return data[transaction_id]


class Transaction(ObjectWithId):
    def __init__(self, sender, receiver, amount, time_created = None, id = None, event_id = None):
        # The super init assigns this transaction an id automatically
        super().__init__()
        # Roll back the id if one was given as input
        if id:
            self.id = id
        self.event_id = event_id
        self.pending = True
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time_created = time_created if time_created else get_timestamp_numerical()
        self.msgs = {
            MSG.SENT : self.msg_transaction_debitor,
            MSG.RECEIVED : self.msg_transaction_creditor
        }
    
    def msg_transaction_debitor(self):
        verb = 'owes' if self.pending else 'sent'
        msg = f"{self.sender.name} (id: {self.sender.id}) {verb} {self.amount} to {self.receiver.name} (id: {self.receiver.id})"
        return msg
    
    def msg_transaction_creditor(self):
        verb = 'will receive' if self.pending else 'received'
        msg =  f"{self.receiver.name} (id: {self.receiver.id}) {verb} {self.amount} from {self.sender.name} (id: {self.sender.id})"
        return msg
        
    def close(self):
        self.sender.add_to_balance(self.amount)
        self.receiver.add_to_balance(-self.amount)
        self.pending = False
    
    def POV_str(self,m_id):
        if m_id != self.sender.id and m_id != self.receiver.id:
            raise ValueError(f"Member {m_id} not involved in transaction between "
                             f"{self.sender.id} and {self.receiver.id}")
        msg = MSG.SENT if m_id == self.sender.id else MSG.RECEIVED
        return self.msgs[msg]()

    def summary(self):
        summary_dict = {
            'id': self.id,
            'event_id': self.event_id,
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'amount': self.amount,
            'time_created': self.time_created,
            'pending': self.pending
        }
        return summary_dict
    
    def __eq__(self,other):
        if not isinstance(other, Transaction):
            return False
        attributes_to_check = ['id','time_created','amount',
                               'pending','sender','receiver']
        return all([getattr(self,attr)==getattr(other,attr) for attr in attributes_to_check])

class PendingTransactions(Saveable):
    @Saveable.takes_class_snapshot
    def __init__(self, owner: Saveable = None):
        super().__init__()
        self.owner = owner
        self.event_id = None
        self.data_dir = os.path.join(owner.data_dir,'transactions') if owner else \
                        os.path.join(prefs.data_dir,'standalone_transactions')
        prefix = f'{owner.id}_' if isinstance(owner,ObjectWithId) else '' 
        self.pending_trans_file_name = f'{prefix}pending_transactions.json'
        self.closed_trans_file_name = f'{prefix}transactions_history.json'
        # Dict for faster lookup
        self.pending_transactions = {}
        # List since we don't need lookups
        self.closed_transactions = []
        # Used when addressing repeatable events 
        # (prevents PendingTransactions from adding copies of the same transactions)
        self.numb = False
        try:
            self.load()
        except FileNotFoundError as e:
            self.logger.debug(e)
            pass
    
    def set_event_id(self, e_id: int):
        self.event_id = e_id
        self.numb = False
        for t in self.pending_transactions.values():
            if t.event_id == e_id:
                self.logger.warning(f"Event {e_id} is being repeated. Adding transactions through this event will be ignored!")
                self.numb = True
                return
    
    def member_transactions(self,member_id, event_id = False):
        if event_id:
            return [t for t in self.pending_transactions.values() \
                if (t.sender.id == member_id or t.receiver.id == member_id) \
                and t.event_id == self.event_id]
        
        return [t for t in self.pending_transactions.values() \
                if t.sender.id == member_id or t.receiver.id == member_id]
    
    def pending_transactions_summary(self):
        return [t.summary() for t in self.pending_transactions.values()]

    def closed_transactions_summary(self):
        return [transaction.summary() for transaction in self.closed_transactions]

    @Saveable.affects_metadata(log_msg="Added transaction to pending transactions")
    def add_transaction(self,transaction: Transaction):
        if self.numb:
            self.logger.debug(f"Ignoring transaction {transaction.id}")
            return
        if transaction.id in self.pending_transactions:
            if self.pending_transactions[transaction.id] == transaction:
                self.logger.warning("Transaction is already in pending transactions")
                return
            else: 
                raise RuntimeError("Fatal Error! Two transactions have the same id.")
        if not transaction.pending: 
            raise ValueError("Cannot add closed transaction to PendingTransactions")
        
        if self.event_id:
            transaction.event_id = self.event_id
        
        self.pending_transactions[transaction.id] = transaction
    
    @Saveable.affects_metadata(log_msg="Closed transaction")
    def close_transaction(self, transaction_id: str):
        if not transaction_id in self.pending_transactions:
            self.logger.warning(f"Transaction {transaction_id} not in PendingTransactions {self.id}")
        transaction = self.pending_transactions.pop(transaction_id)
        transaction.close()
        self.closed_transactions.append(transaction)
    
    def close_all(self):
        for trans in self.pending_transactions:
            self.close_transaction(trans)

    def save_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        p_t_file = os.path.join(self.data_dir,self.pending_trans_file_name)
        with open(p_t_file, 'w+') as file:
            dict_to_save = self.pending_transactions_summary()
            json.dump(dict_to_save,file, indent=4)
        
        if len(self.closed_transactions):
            c_t_file = os.path.join(self.data_dir,self.closed_trans_file_name)
            transaction_history = []
            if os.isfile(c_t_file):
                with open(c_t_file,'r') as file:
                    transaction_history = json.load(file)

            transaction_history.extend(self.closed_transactions_summary())
            with open(c_t_file,'w+') as file:
                json.dump(transaction_history,file)
                # Clear the closed transactions
                self.closed_transactions = {}

    def transaction_history(self):
        """
        Prints out the whole history of previous transactions
        of this group/list. Mainly for UX, but with the frontend
        will not be used.
        """  
        c_t_file = os.path.join(self.data_dir,self.closed_trans_file_name)
        if not os.path.isfile(c_t_file):
            self.logger.warning("Transaction history file not found.")
            return
        with open(c_t_file,'r') as file:
            transaction_history = json.load(file)
        for transaction in transaction_history:
            print(transaction)


    def load(self):
        from backend.cls.member import Member
        p_t_file = os.path.join(self.data_dir,self.pending_trans_file_name)
        if not os.path.isfile(p_t_file):
            raise FileNotFoundError("PendingTransactions file to load from not found")
        with open(p_t_file,'r') as file:
            transactions = json.load(file)
        for t in transactions:
            if self.owner and (not t['sender'] in self.owner.members or not t['receiver'] in self.owner.members):
                raise ValueError("Members involved in transaction "
                                 f"{t['sender']} and t['receiver'] are "
                                 "not related to these PendingTransactions for "
                                 f"{type(self.owner).__name__} {self.owner.id}")
            if not t['pending']:
                raise ValueError("Transaction found in file is closed, closed transactions cannot be loaded")
            sender = Member(t['sender'])
            receiver = Member(t['receiver'])
            new_trans = Transaction(sender = sender,
                                    receiver = receiver,
                                    amount = t['amount'],
                                    time_created= t['time_created'],
                                    id = t['id'],
                                    event_id = t['event_id'])
            self.pending_transactions[new_trans.id] = new_trans
            



    
