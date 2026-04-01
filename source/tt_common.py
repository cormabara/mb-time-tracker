import os
import sys
from enum import IntEnum, Enum

prj_path = os.path.dirname(__file__)
res_path = os.path.join(prj_path, '../resources')
ico_path = os.path.join(res_path, 'icons/dark')
usr_path = os.path.join(prj_path, '../user_data')

sys.path.append("")
sys.path.append("source/ble_central")


def get_res(name_):
    return os.path.join(res_path, name_)


def get_icon(name_):
    return os.path.join(ico_path, name_)


def get_usr_data(name_=""):
    return os.path.join(usr_path, name_)

class TTErrors(IntEnum):
    tt_e_none = 0

