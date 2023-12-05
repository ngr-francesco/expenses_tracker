
from warnings import warn 
import os
import json
from utils.utils import print_dict_in_dict

class Member:
    def __init__(self, name, spent_total, days_spent, folder = ''):
        self.name = name
        self.spent_total = spent_total
        self.days_spent = days_spent
        self.balance = 0
        self.folder_path = folder
    
    def summary(self):
        s = {
            "name": self.name,
            "total spent": self.spent_total,
            "days spent": self.days_spent,
            "balance": self.balance
        }
        return s

class BalanceCalculator:
    def __init__(self, members, cycle_length):
        self.members = members
        self.cycle_length = cycle_length
        self.check_member_data()

    def check_member_data(self):
        for m in self.members:
            if m.days_spent > self.cycle_length:
                raise ValueError(f"The data for {m.name}, {m.days_spent} days spent, is incompatible with the cycle length of {self.cycle_length} days.")
        group_days_spent = sum([m.days_spent for m in self.members])
        if group_days_spent == 0:
            warn("Group days spent is zero, this will be counted as one to avoid errors.")
    
    def add_member(self, name,spent_total, days_spent):
        self.members.append(Member(name,spent_total,days_spent))
        self.check_member_data()
        
    def calculate_balances(self):
        group_total = sum([m.spent_total for m in self.members])
        # At least 1 to avoid division by zero
        group_days_spent = max(sum([m.days_spent for m in self.members]),1)
        daily_expense = group_total/group_days_spent
        for m in self.members:
            m.balance = m.spent_total - m.days_spent*daily_expense
    
    def save_balances(self, verbose = False):
        dict_to_save = {m.name: m.summary() for m in self.members}
        with open(os.path.join(self.folder_path,'balance_record.json'),'w+') as file:
            json.dump(dict_to_save,file, indent=4)
        if verbose:
            print_dict_in_dict(dict_to_save,"Saved balances to file")


if __name__ == '__main__':
    pass
            



