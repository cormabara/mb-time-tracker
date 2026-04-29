from datetime import date

import wx

from mb_logger import Logger
from source.ttdatabase import TTDatabase

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
            self.combo.Bind(wx.EVT_COMBOBOX, self.on_select)
            sizer.Add(self.combo, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)
            self.SetSizer(sizer)
            self.suggest_popup = None

        def populate(self,items):
            self.combo.Clear()
            self.combo.AppendItems(items)

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

        def on_select(self,event):
            Logger().print("on select handler")

    class TtWxInsertDeal(TtWxInsertDbField):

        def __init__(self,parent_,db_):
            super().__init__(parent_,db_,"Deal",db_.get_deals_names())

        def on_pick(self, event):
            super().on_pick(event)

        def on_select(self, event):
            super().on_select(event)
            event.Skip()  # allows parent to receive it

    class TtWxInsertActivity(TtWxInsertDbField):

        def __init__(self,parent_,db_):
            super().__init__(parent_,db_,"Activity",db_.get_activities_names(None))

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

        self.Bind(wx.EVT_COMBOBOX, self.on_deal_change)

    def on_deal_change(self, evt):
        combo = evt.GetEventObject()  # the wx.ComboBox instance
        combo1: wx.ComboBox = combo

        print("Parent received value:", evt.GetString())
        deal = self.db.find_deal_by_name(evt.GetString())
        self.activity.populate(self.db.get_activities_names(evt.GetString()))

    def update(self):
        self.activity.populate(self.db.get_activities_names(self.deal.get_value()))

    def do_submit(self,event):
        time = int(self.time.get_value()) * 60
        deal = self.deal.get_value()
        activity = self.activity.get_value()
        description = self.description.get_value()

        if not time or time < 30 or time > 240:
            Logger().print("invalid time")
            return
        deal_record = self.db.find_deal_by_name(deal)
        if not deal or not deal_record:
            Logger().print("no deal")
            return
        activity_record = self.db.find_activity(activity,deal_record["id"])
        if not activity or not activity_record:
            Logger().print("no activity")
            return
        dt = self.date.GetDate()
        pydate = dt.GetYear(), dt.GetMonth() + 1, dt.GetDay()  # month is 0-based for wx.DateTime
        pydate = date(dt.GetYear(), dt.GetMonth() + 1, dt.GetDay())

        self.db.add_task(pydate, time, deal_record["id"], activity_record["id"], description)
        self.EndModal(wx.ID_OK)
        self.Close()

