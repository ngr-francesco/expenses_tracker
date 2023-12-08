from enum import Enum
import os

EUROCENT = 0.01

default_ids = {
    'ListItem': 'it0000',
    'Member': 'mm0000',
    'Group': 'gr0000',
    'List': 'ls0000',
    'Transaction': 'tr0000'
}

default_data_dir = '../usr_data'

class ItemPrintEnum(Enum):
    def __str__(self) -> str:
        return self.name

class STATUS(ItemPrintEnum):
    Debitor = 0
    Creditor = 1

class MSG(ItemPrintEnum):
    SENT = 0
    RECEIVED = 1