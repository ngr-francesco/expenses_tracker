import os, sys
from backend.cls.group import Group
from backend.cls.member import Member
from backend.utils.logging import Logger, LogLevel
from backend.tests.test_lists import init_basic_list
import pytest

def init_basic_group():
    m1 = Member('A')
    m2 = Member('B')
    mems = [m1,m2]
    g = Group("test",[m for m in mems])
    return g

def test_group_init():
    group = init_basic_group()
    assert len(group.members) == 2


def test_add_list():
    group = init_basic_group()
    ls = init_basic_list()
    assert len(group.lists) == 0
    group.add_list(ls)
    assert len(group.lists) == 1

    with pytest.raises(ValueError):
        ls2 = init_basic_list()
        ls2.add_member(Member('C'))
        group.add_list(ls2)


if __name__ == '__main__':
    test_group_init()
    test_add_list()