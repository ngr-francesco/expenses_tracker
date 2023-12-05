__module__ = 'settling_up_algorithm'

import numpy as np
from enum import Enum
from typing import Union
import json
import os

from utils.utils import print_dict_in_dict

# The minimum accuracy required for this application
EUROCENT = 0.01

class STATUS(Enum):
    Debitor = 0
    Creditor = 1

    def __str__(self) -> str:
        return self.name

class Member:
    def __init__(self,name,amount,status):
        self.name = name
        self.init_amount = amount
        self.partial_amount = amount
        self.settled = False
        self.status = status
        self.transactions = []
        print(f"Initialized {name}: {status} for {amount}")
    
    def is_settled(self):
        if not self.settled and self.partial_amount < EUROCENT:
            self.settled = True
        return self.settled
    
    def clear_transactions(self):
        self.transactions = []
    
    def process_transaction(self,person,amount):
        self.partial_amount -= amount
        msg = 'sends to' if self.status == STATUS.Debitor else 'receives from'
        transaction_info = {'name': person.name,'amount': round(amount,2),'msg': msg}
        if self.partial_amount < -EUROCENT:
            raise ValueError(f"This transaction between {self.name} to {person.name} for {amount}€ surpasses the partial"
                             f" amount of {self.name} of {self.partial_amount}")
        self.transactions.append(transaction_info)
    
    def summary(self):
        summary_dict = {
            'name' : self.name,
            'status': str(self.status),
            'initial_amount': self.init_amount,
            'transactions': [f"{self.name} {trans['msg']} {trans['name']}, {trans['amount']} Euros" for trans in self.transactions], 
            'settled': self.is_settled()
        }
        return summary_dict


def sort_members(members_0: Union[list,Member], *add_members: Union[list,Member]) -> tuple[Member]:
    members_list = [members_0]
    if add_members:
        for m in add_members:
            members_list.append(m)
    # Make sure everything is np.array
    members_list = [np.array(members) for members in members_list]
    amounts_list = [[m.partial_amount for m in members] for members in members_list]
    to_return = tuple([member[np.argsort(amounts)[::-1]] for member,amounts in zip(members_list,amounts_list)])
    # we invert the argsort to have decreasing order
    return to_return

class BalanceSettler:
    def __init__(self,debitors = [],creditors = [], folder_path = ''):
        self.debitors = debitors
        self.creditors = creditors
        self.folder_path = folder_path
    
    def add_person(self,name,amount,status = None):
        if not status:
            status = STATUS.Debitor if amount < 0 else STATUS.Creditor
        if status == STATUS.Debitor:
            self.debitors.append(Member(name,abs(amount),status))
        else:
            self.creditors.append(Member(name,abs(amount),status))

    def check_overall_balance(self):
        debit = 0
        for d in self.debitors:
            debit += d.init_amount
        credit = 0
        for c in self.creditors:
            credit += c.init_amount
        if abs(credit - debit) > 2*EUROCENT:
            raise ValueError("The group debits and credits are not balanced!")

    def transaction(self,debitor,creditor):
        if creditor.is_settled():
            raise ValueError(f"Creditor {creditor.name} is already settled, this transaction should"
                             " not take place!")
        amount = min(abs(debitor.partial_amount),abs(creditor.partial_amount))
        debitor.process_transaction(creditor,amount)
        creditor.process_transaction(debitor,amount)

    def settle_up(self):
        self.check_overall_balance()
        debitors = self.debitors
        creditors = self.creditors
        # sort from largest to smallest
        debitors,creditors = sort_members(debitors,creditors)
        for cur_d in debitors:
            while not cur_d.is_settled():
                self.transaction(cur_d,creditors[0])
                creditors = sort_members(creditors)[0]

    def save_transaction_record(self, verbose = False):
        debitors_dict = {}
        for d in self.debitors:
            debitors_dict[d.name] = d.summary()

        creditors_dict = {}
        for c in self.creditors:
            creditors_dict[c.name] = c.summary()

        with open(os.path.join(self.folder_path,'debitors_transaction_record.json'), 'w+') as file:
            json.dump(debitors_dict, file, indent = 4)
        with open(os.path.join(self.folder_path,'creditors_transaction_record.json'), 'w+') as file:
            json.dump(creditors_dict, file, indent = 4)
        if verbose:
            print("Saved transaction record to files:")
            d_to_print = [debitors_dict,creditors_dict]
            msgs = ["Debitors", "Creditors"]
            for d,msg in zip(d_to_print,msgs):
                print_dict_in_dict(d,msg)

if __name__ == '__main__':
    owed = [20,30,50]
    owes = [5,40,30,25]
    folder_path = 'transaction_records'
    debitors = [Member(f'deb_{k}',owes[k],STATUS.Debitor) for k in range(len(owes))]
    creditors = [Member(f'cred_{k}',owed[k], STATUS.Creditor) for k in range(len(owed))]
    bal_settler = BalanceSettler(debitors,creditors, folder_path= folder_path)
    bal_settler.settle_up()
    bal_settler.save_transaction_record(verbose=True)
