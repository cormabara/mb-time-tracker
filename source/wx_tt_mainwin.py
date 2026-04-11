import calendar

import wx
import wx.adv
import datetime
from datetime import date, timedelta

from mb_logger import Logger
from mb_wx_gui import MbWxToolbar, MbWxStatusbar
from source.tt_common import get_icon
from source.ttdatabase import TTDatabase

# Helper per colore/stile
BG = "#2f2f2f"
SIDEBAR = "#3a3a3a"
TOPBAR = "#252525"
ROW_BG = "#343434"
TEXT = "#dcdcdc"
ACCENT = "#b6e3c6"


class DateRangeDialog(wx.Dialog):
    def __init__(self, parent, start_,end_):
        super().__init__(parent, title="Choose time slot", size=(560, 300))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Quick ranges (Today, Week, Month) as read-only text-like buttons
        quick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        quick_sizer.Add(wx.StaticText(self, label="Today:"), flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=8)
        self.today_tc = wx.TextCtrl(self, value=date.today().strftime("%B %d, %Y"), style=wx.TE_READONLY)
        quick_sizer.Add(self.today_tc, flag=wx.RIGHT, border=20)

        quick_sizer.Add(wx.StaticText(self, label="Week:"), flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=8)
        week_range = self._week_range(date.today())
        self.week_tc = wx.TextCtrl(self, value=f"{week_range[0].strftime('%B %d')} – {week_range[1].strftime('%B %d, %Y')}", style=wx.TE_READONLY)
        quick_sizer.Add(self.week_tc, flag=wx.RIGHT, border=20)

        quick_sizer.Add(wx.StaticText(self, label="Month:"), flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=8)
        month_range = self._month_range(date.today())
        self.month_tc = wx.TextCtrl(self, value=f"{month_range[0].strftime('%B %d')} – {month_range[1].strftime('%B %d, %Y')}", style=wx.TE_READONLY)
        quick_sizer.Add(self.month_tc, proportion=1, flag=wx.EXPAND)

        main_sizer.Add(quick_sizer, flag=wx.ALL|wx.EXPAND, border=8)

        # Calendars area
        cal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_col = wx.BoxSizer(wx.VERTICAL)
        left_col.Add(wx.StaticText(self, label="From:"), flag=wx.BOTTOM, border=6)
        self.cal_from = wx.adv.CalendarCtrl(self, style=wx.adv.CAL_SHOW_HOLIDAYS)
        left_col.Add(self.cal_from, flag=wx.EXPAND)

        cal_sizer.Add(left_col, proportion=1, flag=wx.ALL|wx.EXPAND, border=8)

        middle = wx.BoxSizer(wx.VERTICAL)
        middle.AddStretchSpacer()
        middle.Add(wx.StaticText(self, label="to"), flag=wx.ALIGN_CENTER)
        middle.AddStretchSpacer()
        cal_sizer.Add(middle, flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, border=6)

        right_col = wx.BoxSizer(wx.VERTICAL)
        right_col.Add(wx.StaticText(self, label="To:"), flag=wx.BOTTOM, border=6)
        self.cal_to = wx.adv.CalendarCtrl(self, style=wx.adv.CAL_SHOW_HOLIDAYS)
        right_col.Add(self.cal_to, flag=wx.EXPAND)

        cal_sizer.Add(right_col, proportion=1, flag=wx.ALL|wx.EXPAND, border=8)

        main_sizer.Add(cal_sizer, proportion=1, flag=wx.EXPAND)

        # Apply button aligned right
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        apply_btn = wx.Button(self, label="Apply")
        apply_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        btn_sizer.Add(apply_btn, flag=wx.ALL, border=8)
        main_sizer.Add(btn_sizer, flag=wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()

        # Initialize calendars to sensible defaults
        self.cal_from.SetDate(start_)
        self.cal_to.SetDate(end_)

        # Bind calendar selection events to enforce range validity
        self.cal_from.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.on_from_changed)
        self.cal_to.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.on_to_changed)

    def _week_range(self, d):
        # assuming week starts Monday
        start = d - timedelta(days=d.weekday())
        end = start + timedelta(days=6)
        return start, end

    def _month_range(self, d):
        start = d.replace(day=1)
        if d.month == 12:
            end = d.replace(day=31)
        else:
            next_month = d.replace(month=d.month+1, day=1)
            end = next_month - timedelta(days=1)
        return start, end

    def on_from_changed(self, event):
        from_dt = self.cal_from.GetDate()
        to_dt = self.cal_to.GetDate()
        if from_dt.IsLaterThan(to_dt):
            # move 'to' forward to match 'from'
            self.cal_to.SetDate(from_dt)

    def on_to_changed(self, event):
        from_dt = self.cal_from.GetDate()
        to_dt = self.cal_to.GetDate()
        if to_dt.IsEarlierThan(from_dt):
            # move 'from' back to match 'to'
            self.cal_from.SetDate(to_dt)

    def on_apply(self, event):
        from_dt = self.cal_from.GetDate()
        to_dt = self.cal_to.GetDate()
        # Convert wx.DateTime to python date
        py_from = date(from_dt.GetYear(), from_dt.GetMonth()+1, from_dt.GetDay())
        py_to = date(to_dt.GetYear(), to_dt.GetMonth()+1, to_dt.GetDay())
        if py_from > py_to:
            py_to = py_from

        # Return values via EndModal / attribute
        self.result = (py_from, py_to)
        self.EndModal(wx.ID_OK)
        self.Close()

class TtTaskDialog(wx.Dialog):

    class TtWxInsertField(wx.Panel):

        def __init__(self, parent_, title_):
            super().__init__(parent_)
            sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, label=title_)
            sizer.Add(title,0, flag=wx.ALL, border=0)
            self.text = wx.TextCtrl(self, value="", style=wx.TE_MULTILINE | wx.BORDER_NONE)
            self.text.SetMinSize((200,-1))
            sizer.Add(self.text, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)
            self.SetSizer(sizer)
        def get_value(self):
            return self.text.GetValue()

    class TtWxInsertDbField(wx.Panel):

        def __init__(self, parent_, db_,title_,items_):
            super().__init__(parent_)
            self.db = db_
            sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, label=title_)
            sizer.Add(title,0, flag=wx.ALL, border=0)
            self.items = items_
            self.combo = wx.ComboBox(self, choices=self.items,style=wx.CB_DROPDOWN)
            self.combo.SetMinSize((200,-1))
            self.combo.Bind(wx.EVT_TEXT, self.on_text)

            sizer.Add(self.combo, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)
            self.SetSizer(sizer)
            self.suggest_popup = None

        def get_value(self):
            return self.combo.GetValue()

        def show_suggestions(self):
            Logger().print("show suggestions")
            matches = self.items
            if not matches:
                if self.suggest_popup:
                    self.suggest_popup.Destroy()
                return
            if not self.suggest_popup:
                self.suggest_popup = wx.PopupWindow(self.combo, flags=wx.BORDER_NONE)
                self.lb = wx.ListBox(self.suggest_popup, choices=matches)
                self.lb.Bind(wx.EVT_LISTBOX_DCLICK, self.on_pick)
                self.lb.Bind(wx.EVT_LISTBOX, self.on_pick)  # Enter selection
                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(self.lb, 1, wx.EXPAND)
                self.suggest_popup.SetSizerAndFit(sizer)
                sx, sy = self.combo.ClientToScreen((0, self.combo.GetSize().y))
                self.suggest_popup.Position((sx, sy), (0, 0))  # second arg is optional anchor; works with screen coords
                self._suppress_list_events = True
                self.suggest_popup.Show(True)
                wx.CallAfter(self._enable_list_events)
            else:
                self.lb.Clear()
                self.lb.AppendItems(matches)
                self.suggest_popup.Layout()

        def _enable_list_events(self):
            self._suppress_list_events = False

        def hide_suggestions(self):
            Logger().print("hide suggestions")
            if self.suggest_popup:
                Logger().print("destroy suggestions")
                self.suggest_popup.Destroy()
                self.suggest_popup = None

        def on_text(self, event):
            text = self.combo.GetValue()
            # update self.items based on text...
            # if text == "" or any(text in str(it) for it in self.items):
            #     self.show_suggestions()
            # elif self.suggest_popup :
            #     self.hide_suggestions()
            # event.Skip()

        def on_pick(self, event):
            if getattr(self, "_suppress_list_events", False):
                return
            Logger().print("on pick handler")
            val = event.GetString()
            self.combo.SetValue(val)
            self.combo.SetInsertionPointEnd()
            self.hide_suggestions()

    class TtWxInsertDeal(TtWxInsertDbField):

        def __init__(self,parent_,db_):
            super().__init__(parent_,db_,"Deal",db_.get_deals_names())

        def on_pick(self, event):
            super().on_pick(event)

    class TtWxInsertActivity(TtWxInsertDbField):

        def __init__(self,parent_,db_):
            super().__init__(parent_,db_,"Activity",db_.get_activities_names())

        def on_pick(self, event):
            super().on_pick(event)

    class TtWxInsertDescription(wx.Panel):

        def __init__(self, parent_, title_):
            super().__init__(parent_)
            sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, label=title_)
            sizer.Add(title,proportion=0, flag=wx.ALL, border=0)
            self.text = wx.TextCtrl(self, value="", style=wx.TE_MULTILINE | wx.BORDER_NONE)
            self.text.SetMinSize((-1, int(12 * 4 + 6)))
            sizer.Add(self.text,proportion=1, flag=wx.EXPAND|wx.ALL, border=4)
            self.SetSizer(sizer)
        def get_value(self):
            return self.text.GetValue()

    class TtWxInsertTime(wx.Panel):

        def __init__(self, parent_):
            super().__init__(parent_)
            sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, label="time[h]")
            sizer.Add(title, 0, wx.ALL, 0)
            self.text = wx.SpinCtrlDouble(self, id=wx.ID_ANY, value="2.0", min=0.0, max=8.0,inc=0.5, style=0)
            sizer.Add(self.text, 1, wx.ALL, 4)
            self.SetSizer(sizer)
        def get_value(self):
            return self.text.GetValue()

    def __init__(self, parent,db_,task_):
        super().__init__(parent)
        s_main = wx.BoxSizer(wx.VERTICAL)
        self.db: TTDatabase = db_
        panel_high = wx.Panel(self)
        sub_high = wx.BoxSizer(wx.HORIZONTAL)
        self.time = self.TtWxInsertTime(panel_high)
        sub_high.Add(self.time, 0, wx.ALL, 4)
        self.deal = self.TtWxInsertDeal(panel_high,db_)
        sub_high.Add(self.deal, 0, wx.ALL, 4)
        panel_high.SetSizer(sub_high)
        self.activity = self.TtWxInsertActivity(panel_high,db_)
        sub_high.Add(self.activity, 0, wx.ALL, 4)
        s_main.Add(panel_high, 0, wx.ALL, 4)

        panel_middle = wx.Panel(self)
        sub_middle = wx.BoxSizer(wx.VERTICAL)
        self.date = wx.adv.CalendarCtrl(panel_middle, style=wx.adv.CAL_SHOW_HOLIDAYS)
        sub_middle.Add(self.date, proportion=1, flag=wx.EXPAND|wx.ALL, border=4)
        panel_middle.SetSizer(sub_middle)
        s_main.Add(panel_middle, proportion=1, flag=wx.EXPAND|wx.ALL, border=4)

        panel_low = wx.Panel(self)
        sub_low = wx.BoxSizer(wx.VERTICAL)
        self.description = self.TtWxInsertDescription(panel_low,"Description")
        sub_low.Add(self.description, proportion=1, flag=wx.EXPAND|wx.ALL, border=4)
        panel_low.SetSizer(sub_low)
        s_main.Add(panel_low, proportion=1, flag=wx.EXPAND|wx.ALL, border=4)

        btn_submit =wx.Button(self,label="Submit", size=(-1, 30))
        btn_submit.Bind(wx.EVT_BUTTON, lambda evt: self.do_submit(evt))
        s_main.Add(btn_submit, proportion=0, flag=wx.EXPAND|wx.ALL, border=4)
        self.SetSizer(s_main)
        self.Layout()
        self.Fit()

        if task_:
            self.date.SetDate(task_["date"])
            self.description.text.SetValue(task_["description"])
            self.time.text.SetValue(task_["minutes"])
            self.activity.text.SetValue(task_["activity"])
            self.deal.text.SetValue(task_["deal"])

    def do_submit(self,event):
        time = int(self.time.get_value()) * 60
        deal = self.deal.get_value()
        activity = self.activity.get_value()
        description = self.description.get_value()

        if not time or time < 30 or time > 240:
            Logger().print("invalid time")
            return
        deal_record = self.db.find_deal(deal)
        if not deal or not deal_record:
            Logger().print("no deal")
            return
        if not activity or not self.db.find_activity(activity,deal_record["id"]):
            Logger().print("no activity")
            return
        dt = self.date.GetDate()
        pydate = dt.GetYear(), dt.GetMonth() + 1, dt.GetDay()  # month is 0-based for wx.DateTime
        pydate = date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        self.db.add_task(pydate, time, deal, activity, description)
        self.EndModal(wx.ID_OK)
        self.Close()


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

        # Top toolbar definition
        top = MbWxToolbar(self,height=32)
        top.SetBackgroundColour(BG)
        self.back = top.add_img_button(get_icon("arrow-left.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_backward)
        self.forw = top.add_img_button(get_icon("arrow-right.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_forward)
        self.date_slot = top.add_text_button("Slot button",wx.LEFT,wx.ALIGN_CENTER_VERTICAL,self.cb_pop_date_slot)
        top.add_spacer(4)
        plus = top.add_img_button(get_icon("plus.png"),position=wx.RIGHT)
        plus.Bind(wx.EVT_BUTTON, self.on_add)
        top.add_img_button(get_icon("menu.png"),position=wx.RIGHT)
        main_sizer.Add(top, 0, wx.EXPAND)


        # Content area
        content = wx.Panel(self)
        content.SetBackgroundColour(BG)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)


        # Data list area
        data_area = wx.Panel(content)
        data_area.SetBackgroundColour(BG)
        data_sizer = wx.BoxSizer(wx.VERTICAL)
        data_area.SetSizer(data_sizer)
        # Scrolled list
        self.scroller = wx.ScrolledWindow(data_area, style=wx.VSCROLL)
        self.scroller.SetBackgroundColour(BG)
        self.scroller.SetScrollRate(5,5)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroller.SetSizer(self.list_sizer)
        data_sizer.Add(self.scroller, 1, wx.EXPAND | wx.ALL, 6)
        content_sizer.Add(data_area, 1, wx.EXPAND)
        content.SetSizer(content_sizer)
        main_sizer.Add(content, 1, wx.EXPAND)

        # Bottom total bar
        bottom = MbWxStatusbar(self,height=32)
        bottom.SetBackgroundColour(BG)
        self.total_label = bottom.add_text("Total: 0h")
        main_sizer.Add(bottom, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        # prepare the window
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
        if len(tasks) != 0 or self.list_sizer.GetItemCount() == 0:
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
        dlg = TtTaskDialog(self, self.db, None)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                Logger().print("add task")
            except Exception as ex:
                Logger().print("Error adding a task")
        dlg.Destroy()

