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
    


    def settle_balances(self, id):
        """
        Find the optimal transactions between group members to settle up 
        a group or list balance. If for group remind the user that they
        are balancing across multiple lists.
        """
        pass

