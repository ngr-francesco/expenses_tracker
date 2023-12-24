import uuid
from backend.cls.saveable import Saveable


class UserProfile(Saveable):
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.usr_id = uuid.uuid4()

