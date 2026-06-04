import os
import sys
from enum import IntEnum, Enum

import wx


class Colors(Enum):
    BG = "#2f2f2f"
    SIDEBAR = "#3a3a3a"
    TOPBAR = "#252525"
    ROW_BG = "#343434"
    TEXT = "#dcdcdc"
    ACCENT = "#b6e3c6"


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


# Helper per colore/stile
class GuiCol(Enum):
    BG = "#2f2f2f"
    SIDEBAR = "#3a3a3a"
    TOPBAR = "#252525"
    ROW_BG = "#343434"
    TEXT = "#dcdcdc"
    ACCENT = "#b6e3c6"

    def wx(self) -> wx.Colour:
        return wx.Colour(self.value)

