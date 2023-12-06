from utils.id_factory import IdFactory
from utils.const import MSG
from cls.member import Member

class Transaction:
    def __init__(self, sender: Member, receiver: Member, amount, sent_received):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.sent_received = sent_received
        self.id = IdFactory.get_obj_id(self)
        self.msgs = {
            MSG.SENT : f"{self.sender.name} (id: {self.sender.id}) sent {self.amount} to {self.receiver} (id: {self.receiver.id})",
            MSG.RECEIVED : f"{self.receiver} (id: {self.receiver.id}) received {self.amount} from {self.sender} (id: {self.sender.id})"
        }
    
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