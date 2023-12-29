from backend.cls.list import List, ListItem, SharingMethods
from backend.cls.member import Member
import os
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
    l.add_item(i)
    assert len(l.members) == 2

def test_list_load():
    l = init_basic_list()
    l.save_data()
    dir = l.data_dir
    file_name = l.file_name
    del l
    l2 = List(load_from_file=True,load_file_path=os.path.join(dir,file_name))
    assert len(l2.members) == 2




if __name__ == '__main__':
    test_list_init()
    test_list_load()