from backend.cls.list import List, ListItem, SharingMethods
from backend.cls.member import Member
import pytest

def test_list_init():
    m1 = Member('A')
    m2 = Member('B')
    mems = [m1,m2]
    l = List("test",[m for m in mems])
    print(l.members)
    i = ListItem('test_i',m1,amount = 10,members_involved=l.members)
    print(i)
    l.add_item(i)
    print(l.items)
    print(l.members)
    assert len(l.members) == 2



if __name__ == '__main__':
    test_list_init()