from enum import Enum
import os
import uuid

EUROCENT = 0.01

default_data_dir = 'usr_data'

class ItemPrintEnum(Enum):
    def __str__(self) -> str:
        return self.name

class STATUS(ItemPrintEnum):
    Debitor = 0
    Creditor = 1

class MSG(ItemPrintEnum):
    SENT = 0
    RECEIVED = 1