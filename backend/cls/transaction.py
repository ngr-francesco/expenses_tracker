import os
import json

from backend.cls.object_with_id import ObjectWithId
from backend.cls.saveable import Saveable
from backend.utils.const import MSG, default_data_dir
from backend.utils.time import get_timestamp_numerical

def get_transaction_info_from_id(transaction_id,path):
    if not os.path.exists(path):
        raise FileNotFoundError("Path to transactions list is not in system.")
    with open(path,'r') as file:
        data = json.load(file)

    return data[transaction_id]

class PendingTransactions(Saveable):
    def __init__(self):
        super().__init__()
        raise NotImplementedError()

class Transaction(ObjectWithId):
    def __init__(self, sender, receiver, amount, sent_received, owner = None):
        super().__init__()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.sent_received = sent_received
        self.msgs = {
            MSG.SENT : f"{self.sender.name} (id: {self.sender.id}) sent {self.amount} to {self.receiver} (id: {self.receiver.id})",
            MSG.RECEIVED : f"{self.receiver} (id: {self.receiver.id}) received {self.amount} from {self.sender} (id: {self.sender.id})"
        }
        parent_dir = owner.data_dir if owner else default_data_dir
        self.data_dir = os.path.join(parent_dir,'transactions')
        self.save_data()
    
    def __str__(self):
        return self.msgs[self.sent_received]

    def summary(self):
        summary_dict = {
            'transaction_id': self.id,
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'amount': self.amount,
            'direction': str(self.sent_received),
            'time_created': get_timestamp_numerical()
        }
        return summary_dict
    
    def save_data(self):
        file_path = os.path.join(self.data_dir,'transactions.json')
        transactions = {}
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if os.path.exists(self.file_path):
            with open(file_path,'r') as file:
                transactions = json.load(file)
        # Ids should be unique: make sure that this is true
        if self.id in transactions:
            raise KeyError("Transaction is already present in transactions file, this is a bug and should not happen!")
        
        transactions[self.id]= self.summary()
        with open(file_path,'w+') as file:
            json.dump(transactions, file, indent = 4)
    
