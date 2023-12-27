from backend.balance_calculator import BalanceCalculator
from backend.balance_settler import BalanceSettler

class ProfileManager:
    def __init__(self, user_profile):
        self.user_groups = self.load_user_groups()
        self.user_lists = self.load_user_lists()
        self.user_profile = user_profile
    

    def load_profile_data(self):
        pass

    def load_user_groups(self):
        pass

    def load_user_lists(self):
        pass
    

    def calculate_group_balances(self, group_id):
        """
        Calculate the balances over either a list, or a group.
        In case it's for a group have the option to show the balance for each of the lists.
        """
        group = self.user_groups[group_id]
        lists_array = [l for l in group.lists.values()]
        
        for l in lists_array:
            balance_calculator = BalanceCalculator(expenses_list= l)
            balance_calculator.calculate_balances()
    
    def calculate_list_balances(self, list_id):
        list = self.user_lists[list_id]
        balance_calculator = BalanceCalculator(expenses_list=list)
        balance_calculator.calculate_balances()


    def settle_balances(self, id):
        """
        Find the optimal transactions between group members to settle up 
        a group or list balance. If for group remind the user that they
        are balancing across multiple lists.
        """
        pass

