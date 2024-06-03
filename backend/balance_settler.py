__module__ = 'settling_up_algorithm'

import numpy as np
from enum import Enum
from typing import Union
import json
import os

from backend.utils.const import EUROCENT, STATUS
from backend.cls.member import Member, MembersList
from backend.cls.transactions import PendingTransactions, Transaction

class BalanceSettler:
    def __init__(self,members = [], folder_path = ''):
        self.members = MembersList(owner=self)
        self.partial_amounts = {}
        for member in members:
            self.add_person(member)
        self.transactions = PendingTransactions()
        self.folder_path = folder_path
    
    def sort_members(self, members_0: Union[list,Member], *add_members: Union[list,Member]) -> tuple[Member]:
        """
        Sort members by the amount owed or owed to them.
        """
        members_list = [members_0]
        if add_members:
            for m in add_members:
                members_list.append(m)
        # Make sure everything is np.array
        for k in range(len(members_list)):
            members_list[k] = sorted(members_list[k],key = lambda member: abs(member.balance),reverse=True)
        # we invert the argsort to have decreasing order
        return members_list
    
    def add_person(self,member = None, name = '',amount:float = 0):
        if member is None:
            member = Member(name = name,balance=amount)
        self.members.add_member(member)
        self.partial_amounts[member.id] = member.balance


    def check_overall_balance(self):
        overall_balance = 0
        for m in self.members:
            overall_balance += m.balance
        if abs(overall_balance) > 2*EUROCENT:
            raise ValueError(f"The group debits and credits are not balanced! diff = {overall_balance}")

    def transaction(self,debitor,creditor):
        if creditor.is_settled():
            raise ValueError(f"Creditor {creditor.name} is already settled, this transaction should"
                             " not take place!")
        d_id, c_id = debitor.id,creditor.id
        deb_amount = self.partial_amounts[d_id]
        cred_amount = self.partial_amounts[c_id]
        amount = min(abs(deb_amount),abs(cred_amount))

        # Local effect: Update partial sums
        self.partial_amounts[d_id] += amount
        self.partial_amounts[c_id] -= amount

        # Global effect: Create a transaction to keep track of the settling up process
        trans = Transaction(sender = debitor,receiver= creditor,amount=amount)
        self.transactions.add_transaction(trans)

    def generate_settle_up_transactions(self):
        self.check_overall_balance()
        self.generate_event_id()
        debitors = self.members.debitors
        creditors = self.members.creditors
        # sort from largest to smallest
        debitors,creditors = self.sort_members(debitors,creditors)

        for cur_d in debitors:
            while not abs(self.partial_amounts[cur_d.id]) < EUROCENT:
                self.transaction(cur_d,creditors[0])
                if self.partial_amounts[creditors[0].id] < EUROCENT:
                    creditors = creditors[1:] + [creditors[0]]
                    
                # Resorting results in the lowest debitor having to fill 
                # a bunch of holes, so it's a bit more annoying
                #creditors = self.sort_members(creditors)[0]
    
    def generate_event_id(self):
        """
        Create a unique id that represents this event, characterized
        by THESE members trying to settle up with THESE specific balances
        and THIS specific configuration of debitors and creditors.
        This should be pretty safe in ensuring that this id is unique.
        """
        e_id = 0
        for m in self.members:
            dc_specifier = 1 if m in self.members.creditors else 2
            e_id += m.id.numeral*dc_specifier*int(m.balance*100)
        self.transactions.set_event_id(e_id)



    def save_transaction_record(self, verbose = False):
        dict_to_save = {}
        for m in self.members:
            member_transactions = self.transactions.member_transactions(m.id, event_id = True)
            for t in member_transactions:
                print(t.POV_str(m.id))
            dict_to_save[m.id] = [trans.POV_str(m.id) for trans in member_transactions]

        with open(os.path.join(self.folder_path,'settle_up_transaction_summary.json'), 'w+') as file:
            json.dump(dict_to_save, file, indent = 4)

        if verbose:
            print("Saved transaction record to files:")
            print("Summary:")
            print(json.dumps(dict_to_save,indent = 4))

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
