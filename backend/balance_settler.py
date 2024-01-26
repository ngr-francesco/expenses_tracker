__module__ = 'settling_up_algorithm'

import numpy as np
from enum import Enum
from typing import Union
import json
import os

from backend.utils.const import EUROCENT, STATUS
from backend.cls.member import Member, MembersList

def sort_members(members_0: Union[list,Member], *add_members: Union[list,Member]) -> tuple[Member]:
    """
    Sort members by the amount owed or owed to them.
    """
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
    def __init__(self,members = [], folder_path = ''):
        self.debitors = []
        self.creditors = []
        self.members = MembersList(owner=self)
        for member in members:
            self.add_person(member)
        
        self.folder_path = folder_path
    
    def add_person(self,member = None, name = '',amount:float = 0,status = None):
        if not status:
            status = STATUS.Debitor if amount < 0 else STATUS.Creditor
        if member is None:
            member = Member(name,balance=abs(amount), status=status)
            self.members.add_member(member)
        if status == STATUS.Debitor:
            self.debitors.append(member)
        else:
            self.creditors.append(member)

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

    def generate_settle_up_transactions(self):

        self.check_overall_balance()
        # Prepare members for settle up process
        for member in self.members:
            member.begin_settle_up()

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
            debitors_dict[d.name] = d.transaction_summary()

        creditors_dict = {}
        for c in self.creditors:
            creditors_dict[c.name] = c.transaction_summary()

        with open(os.path.join(self.folder_path,'debitors_transaction_record.json'), 'w+') as file:
            json.dump(debitors_dict, file, indent = 4)
        with open(os.path.join(self.folder_path,'creditors_transaction_record.json'), 'w+') as file:
            json.dump(creditors_dict, file, indent = 4)
        if verbose:
            print("Saved transaction record to files:")
            d_to_print = [debitors_dict,creditors_dict]
            msgs = ["Debitors", "Creditors"]
            for d,msg in zip(d_to_print,msgs):
                print(msg)
                print(json.dumps(d,indent = 4))

if __name__ == '__main__':
    owed = [20,30,50]
    owes = [5,40,30,25]
    folder_path = 'transaction_records'
    debitors = [Member(f'deb_{k}',owes[k],STATUS.Debitor) for k in range(len(owes))]
    creditors = [Member(f'cred_{k}',owed[k], STATUS.Creditor) for k in range(len(owed))]
    members = debitors
    members.extend(creditors)
    bal_settler = BalanceSettler(members, folder_path= folder_path)
    bal_settler.settle_up()
    bal_settler.save_transaction_record(verbose=True)
