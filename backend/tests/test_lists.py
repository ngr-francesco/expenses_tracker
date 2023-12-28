from backend.cls.list import List, ListItem, SharingMethods
from backend.cls.member import Member
import pytest

def init_basic_list():
    m1 = Member('A')
    m2 = Member('B')
    mems = [m1,m2]
    l = List("test",[m for m in mems])
    return l


def test_list_init():
    l = init_basic_list()
    i = ListItem('test_i',l.members.get_by_name('A'),amount = 10,members_involved=l.members)
    print(i)
    l.add_item(i)
    assert len(l.members) == 2

def test_list_load():
    pass



if __name__ == '__main__':
    test_list_init()