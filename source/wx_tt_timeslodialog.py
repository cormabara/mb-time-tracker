import wx
import wx.adv
from datetime import date, timedelta

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
