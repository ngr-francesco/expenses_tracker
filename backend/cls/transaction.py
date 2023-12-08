from utils.id_factory import IdFactory
from utils.const import MSG, default_data_dir
import os
import json

def get_transaction_info_from_id(transaction_id,path):
    if not os.path.exists(path):
        raise FileNotFoundError("Path to transactions list is not in system.")
    with open(path,'r') as file:
        data = json.load(file)

    return data[transaction_id]


class Transaction:
    def __init__(self, sender, receiver, amount, sent_received, data_dir = os.path.join(default_data_dir,'transactions.json')):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.sent_received = sent_received
        self.id = IdFactory.get_obj_id(self)
        self.msgs = {
            MSG.SENT : f"{self.sender.name} (id: {self.sender.id}) sent {self.amount} to {self.receiver} (id: {self.receiver.id})",
            MSG.RECEIVED : f"{self.receiver} (id: {self.receiver.id}) received {self.amount} from {self.sender} (id: {self.sender.id})"
        }
        self.data_dir = data_dir
    
    def __str__(self):
        return self.msgs[self.sent_received]

    def summary(self):
        summary_dict = {
            'transaction_id': self.id,
            'sender': self.sender.member_summary(),
            'receiver': self.receiver.member_summary(),
            'amount': self.amount,
            'direction': str(self.sent_received)
        }
        return summary_dict
    
    def save_transaction(self):
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