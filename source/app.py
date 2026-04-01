import os
import wx
from gui_wx import Mainframe
from source.wx_tt_mainwin import TTMainWin
from ttdatabase import TTDatabase

def main():
    db = TTDatabase()
    app = wx.App(False)
    frame = TTMainWin(db)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
