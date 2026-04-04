import calendar

import wx
import datetime

from mb_logger import Logger
from mb_wx_gui import MbWxToolbar
from source.tt_common import get_icon
from source.ttdatabase import TTDatabase
from source.wx_tt_timeslodialog import DateRangeDialog

# Helper per colore/stile
BG = "#2f2f2f"
SIDEBAR = "#3a3a3a"
TOPBAR = "#252525"
ROW_BG = "#343434"
TEXT = "#dcdcdc"
ACCENT = "#b6e3c6"

class TTTaskDialog(wx.Dialog):

    def __init__(self, parent,task_):
        super().__init__(parent)



class SingleTask(wx.Panel):

    def __init__(self, parent, db_,task_):
        super().__init__(parent)
        s = wx.BoxSizer(wx.HORIZONTAL)

        v = wx.BoxSizer(wx.VERTICAL)
        deal_name = db_.find_deal_from_id(task_["deal"])
        activity_name = db_.find_activity_from_id(task_["activity"])
        deal_label = wx.StaticText(self, label=deal_name if deal_name else "No deal")
        desc_label = wx.StaticText(self, label=activity_name if activity_name else "No activity")
        desc_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        v.Add(deal_label, 0, wx.BOTTOM, 2)
        v.Add(desc_label, 0)

        self.duration = task_["minutes"] / 60
        dur_label = wx.StaticText(self, label=f"{self.duration}h")
        dur_label.SetForegroundColour(TEXT)
        dur_label.SetMinSize((40, -1))

        s.Add(v, 1, wx.ALL | wx.EXPAND, 8)
        s.Add(dur_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
        self.SetSizer(s)

class SingleSlot(wx.Panel):

    def __init__(self,parent,date_:datetime.date,db_,tasks:list[dict]):
        super().__init__(parent)

        slot_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(self)
        sidebar.SetBackgroundColour(SIDEBAR)
        sidebar.SetMinSize((120, -1))
        day_sizer = wx.BoxSizer(wx.VERTICAL)
        day_lbl_big = wx.StaticText(sidebar, label=calendar.day_name[date_.weekday()] )
        day_lbl_big.SetForegroundColour(TEXT)
        day_lbl_small = wx.StaticText(sidebar, label=f"{date_.year}/{date_.month}/{date_.day}")
        day_lbl_small.SetForegroundColour(TEXT)
        day_sizer.Add(day_lbl_big, 0, wx.BOTTOM, 4)
        day_sizer.Add(day_lbl_small, 0)
        sidebar.SetSizer(day_sizer)

        tasks_area = wx.Panel(self)
        tasks_sizer = wx.BoxSizer(wx.VERTICAL)
        for task in tasks:
            row = SingleTask(tasks_area, db_, task)
            tasks_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)
        tasks_area.SetSizer(tasks_sizer)

        slot_sizer.Add(sidebar, 0, wx.EXPAND)
        slot_sizer.Add(tasks_area, 1, wx.EXPAND | wx.ALL, 6)
        self.SetSizer(slot_sizer)

class TTMainWin(wx.Frame):
    def __init__(self, db_:TTDatabase, parent=None):
        super().__init__(parent, title="Hamster Time Tracker", size=(940,520))
        self.tasks = None
        self.db = db_
        self.start_date = datetime.date(1970, 1, 1)
        self.end_date = datetime.date(1970, 1, 3)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        top = MbWxToolbar(self,height=32)
        top.SetBackgroundColour(BG)
        self.back = top.add_img_button(get_icon("arrow-left.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_backward)
        self.forw = top.add_img_button(get_icon("arrow-right.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_forward)
        self.date_slot = top.add_text_button("Slot button",wx.LEFT,wx.ALIGN_CENTER_VERTICAL,self.cb_pop_date_slot)
        top.add_spacer(4)
        plus = top.add_img_button(get_icon("plus.png"),position=wx.RIGHT)
        plus.Bind(wx.EVT_BUTTON, self.on_add)
        menu = top.add_img_button(get_icon("menu.png"),position=wx.RIGHT)
        main_sizer.Add(top, 0, wx.EXPAND)

        # Content area
        content = wx.Panel(self)
        content.SetBackgroundColour(BG)
        c_s = wx.BoxSizer(wx.HORIZONTAL)

        # Main list area
        main_area = wx.Panel(content)
        main_area.SetBackgroundColour(BG)
        ma_s = wx.BoxSizer(wx.VERTICAL)

        # Header (giorno + day column)
        header = wx.BoxSizer(wx.HORIZONTAL)
        daycol = wx.BoxSizer(wx.VERTICAL)
        header.Add(daycol, 0, wx.LEFT | wx.TOP, 8)
        ma_s.Add(header, 0, wx.EXPAND)

        # Scrolled list
        self.scroller = wx.ScrolledWindow(main_area, style=wx.VSCROLL)
        self.scroller.SetBackgroundColour(BG)
        self.scroller.SetScrollRate(5,5)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroller.SetSizer(self.list_sizer)

        ma_s.Add(self.scroller, 1, wx.EXPAND | wx.ALL, 6)

        # Bottom total bar
        bottom = wx.Panel(main_area)
        bottom.SetBackgroundColour(BG)
        b_s = wx.BoxSizer(wx.HORIZONTAL)
        self.total_label = wx.StaticText(bottom, label="Total: 0h")
        self.total_label.SetForegroundColour(TEXT)
        b_s.Add(self.total_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 8)
        bottom.SetSizer(b_s)
        ma_s.Add(bottom, 0, wx.EXPAND | wx.BOTTOM, 6)

        main_area.SetSizer(ma_s)
        c_s.Add(main_area, 1, wx.EXPAND)

        content.SetSizer(c_s)
        main_sizer.Add(content, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        # Connect plus button
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)
        self.refresh_total()

        self.Centre()

    def __update_slot_button(self):
        if self.start_date != self.end_date:
            self.date_slot.SetLabel(f" {self.start_date} to {self.end_date} ")
        else:
            self.date_slot.SetLabel(f" {self.start_date} ")


    def __populate_from_database(self,start_date:datetime.date,end_date:datetime.date):

        def daterange(start: datetime.date, end: datetime.date):
            current = start
            while current <= end:
                yield current
                current += datetime.timedelta(days=1)

        self.list_sizer.Clear(True)

        for d in daterange(start_date, end_date):
            self.add_day_slot(d)
            print(d)

        self.scroller.Layout()
        self.refresh_total()

    def cb_pop_date_slot(self, evt):
        Logger().print("pop date slot")
        dlg = DateRangeDialog(None, self.start_date, self.end_date)
        if dlg.ShowModal() == wx.ID_OK:
            self.start_date, self.end_date = dlg.result
            Logger().print(f"Start: {self.start_date}\nEnd: {self.end_date}")
        dlg.Destroy()
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)

    def cb_slot_backward(self, evt):
        delta = self.end_date - self.start_date
        if self.start_date != self.end_date:
            delta = (self.end_date - self.start_date) + datetime.timedelta(days=1)
            self.start_date = self.start_date - delta
            self.end_date = self.end_date - delta
        else:
            self.start_date = self.start_date - datetime.timedelta(days=1)
            self.end_date = self.end_date - datetime.timedelta(days=1)
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)

    def cb_slot_forward(self, evt):
        if self.start_date != self.end_date:
            delta = (self.end_date - self.start_date) + datetime.timedelta(days=1)
            self.start_date = self.start_date + delta
            self.end_date = self.end_date + delta
        else:
            self.start_date = self.start_date + datetime.timedelta(days=1)
            self.end_date = self.end_date + datetime.timedelta(days=1)
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)

    def add_task(self, task_):
        row = SingleTask(self.scroller, task_)
        self.list_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)

    def add_day_slot(self, day_:datetime.date):
        tasks = self.db.find_tasks(day_,day_)
        slot = SingleSlot(self.scroller,day_, self.db, tasks)
        self.list_sizer.Add(slot, 0, wx.EXPAND | wx.BOTTOM, 6)
        self.scroller.Layout()
        self.refresh_total()

    def refresh_total(self):
        if self.tasks:
            total = sum(t.duration for t in self.tasks)
            self.total_label.SetLabel(f"Total: {total}h")

    def on_add(self, evt):
        # dialog semplice per aggiungere una riga (solo demo)
        dlg = TTTaskDialog(self, None)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                Logger().print("add task")
            except Exception as ex:
                Logger().print("Error adding a task")
        dlg.Destroy()

