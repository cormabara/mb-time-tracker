import os
import wx
from gui_wx import Mainframe
from ttdatabase import TTDatabase

def main():
    db = TTDatabase()
    app = wx.App(False)
    frame = Mainframe(db)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
