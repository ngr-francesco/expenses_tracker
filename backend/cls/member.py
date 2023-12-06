from utils.const import EUROCENT, STATUS, MSG
from utils.logging import get_logger
from utils.id_factory import IdFactory
from cls.transaction import Transaction

class Member:
    def __init__(self,name,balance = 0,status = None, spent_total = 0, days_spent = 0):
        self.logger = get_logger(self.__name__)
        self.name = name
        self.id = IdFactory.get_obj_id(self)
        self._settled = False
        self.status = status
        self.balance = balance
        self.spent_total = spent_total
        self.days_spent = days_spent
        self.transactions = []
        print(f"Initialized {name}: {status} for {balance}")
    
    def is_settled(self):
        if not self._settled and self.partial_amount < EUROCENT:
            self._settled = True
            self.partial_amount = 0
        return self._settled
    
    def begin_settle_up(self):
        self.logger.debug(f"Preparing to settle up {self.name}, balance = {self.balance}")
        self.init_amount = abs(self.balance)
        self.partial_amount = self.init_amount
    
    def finalize_settle_up(self):
        if not self.is_settled():
            raise ValueError(f"Member {self.name} is not settled, yet. Can't finalize settling up process.")
        self.clear_transactions()
        self.balance = 0
        self.partial_amount = 0
        self.spent_total -= self.balance
        del self.init_amount

    def clear_transactions(self):
        if not self.is_settled():
            self.logger.warning("You are clearing the transaction of a member which is not yet settled up."
                                " this will most likely affect the overall balance of this group/list")
        self.transactions = []
    
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
            'name' : self.name
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
            'settled': self.is_settled(),
            "total spent": self.spent_total,
            "days spent": self.days_spent,
            
        })
        return summary_dict
    
    