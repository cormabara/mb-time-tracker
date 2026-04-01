import wx
import wx.adv
import datetime
import threading

from ttdatabase import TTDatabase


class Mainframe(wx.Frame):
    def __init__(self, db_:TTDatabase):
        super().__init__(None, title="Hamster Client (wxPython)", size=(700,500))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Status
        self.status = wx.StaticText(panel, label="Ready")
        vbox.Add(self.status, flag=wx.ALL|wx.EXPAND, border=5)

        # Activities list
        vbox.Add(wx.StaticText(panel, label="Activities"), flag=wx.LEFT, border=5)
        self.activities = wx.ListBox(panel)
        vbox.Add(self.activities, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=5)

        # Controls
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.note_ctrl = wx.TextCtrl(panel)
        self.note_ctrl.SetHint("Note (optional)")
        hbox.Add(self.note_ctrl, proportion=1, flag=wx.RIGHT, border=5)

        self.start_btn = wx.Button(panel, label="Start")
        self.stop_btn = wx.Button(panel, label="Stop selected timeslot")
        hbox.Add(self.start_btn, flag=wx.RIGHT, border=5)
        hbox.Add(self.stop_btn)
        vbox.Add(hbox, flag=wx.ALL|wx.EXPAND, border=5)

        # Timeslots
        vbox.Add(wx.StaticText(panel, label="Recent timeslots"), flag=wx.LEFT, border=5)
        self.timeslots = wx.ListBox(panel)
        vbox.Add(self.timeslots, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=5)

        panel.SetSizer(vbox)

        # Events
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.activities.Bind(wx.EVT_LISTBOX_DCLICK, self.on_start)

        # Refresh periodically in background
        self.poll_interval_ms = 5000
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(self.poll_interval_ms)
        self.refresh_in_background()

    def set_status(self, text):
        wx.CallAfter(self.status.SetLabel, text)

    def refresh_in_background(self):
        def job():
            try:
                wx.CallAfter(self.populate_lists, activities, times)
                self.set_status("Synced")
            except Exception as e:
                self.set_status(f"Error: {e}")
        threading.Thread(target=job, daemon=True).start()

    def populate_lists(self, activities, times):
        self.activities.Clear()
        for a in activities:
            self.activities.Append(f"{a['id']}: {a.get('name','Unnamed')}")
        self.timeslots.Clear()
        for t in times:
            self.timeslots.Append(f"{t['id']}: act {t.get('activity_id')} {t.get('started_at')} - {t.get('ended_at')}")

    def on_timer(self, _evt):
        self.refresh_in_background()

    def on_start(self, evt):
        sel = self.activities.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageBox("Select an activity to start.", "Info", wx.OK|wx.ICON_INFORMATION)
            return
        item = self.activities.GetString(sel)
        activity_id = int(item.split(":")[0])
        note = self.note_ctrl.GetValue().strip()
        def job():
            try:
                res = self.api.start_timeslot(activity_id, note)
                wx.CallAfter(wx.MessageBox, f"Started timeslot {res.get('id')}", "Started", wx.OK|wx.ICON_INFORMATION)
                self.refresh_in_background()
            except Exception as e:
                wx.CallAfter(wx.MessageBox, str(e), "Error", wx.OK|wx.ICON_ERROR)
        threading.Thread(target=job, daemon=True).start()

    def on_stop(self, evt):
        sel = self.timeslots.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageBox("Select a timeslot to stop.", "Info", wx.OK|wx.ICON_INFORMATION)
            return
        item = self.timeslots.GetString(sel)
        timeslot_id = int(item.split(":")[0])
        def job():
            try:
                res = self.api.stop_timeslot(timeslot_id)
                wx.CallAfter(wx.MessageBox, f"Stopped timeslot {res.get('id')}", "Stopped", wx.OK|wx.ICON_INFORMATION)
                self.refresh_in_background()
            except Exception as e:
                wx.CallAfter(wx.MessageBox, str(e), "Error", wx.OK|wx.ICON_ERROR)
        threading.Thread(target=job, daemon=True).start()


class TTDayFrame(wx.Frame):

    def __init__(self,db_, *args, **kw):
        super().__init__(None,*args, **kw)

        # colori
        bg_color = "#2f2f2f"       # sfondo generale
        sidebar_color = "#3a3a3a"  # pannello laterale
        topbar_color = "#252525"   # barra superiore
        text_color = "#dcdcdc"

        self.SetBackgroundColour(bg_color)
        self.SetSize((900, 520))
        self.SetTitle("Hamster Time Tracker - Mock")

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top bar
        topbar = wx.Panel(self, style=wx.BORDER_NONE)
        topbar.SetBackgroundColour(topbar_color)
        topbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        topbar.SetSizer(topbar_sizer)
        topbar.SetMinSize((-1, 40))

        # Left: back arrow icon (simple button)
        back_btn = wx.Button(topbar, label=u"\u25C0", style=wx.BU_EXACTFIT)
        back_btn.SetBackgroundColour(topbar_color)
        back_btn.SetForegroundColour(text_color)
        back_btn.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        topbar_sizer.Add(back_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)

        # Center: date chooser (read-only combo-like)
        date_label = wx.StaticText(topbar, label=datetime.date.today().strftime("%B %d, %Y"))
        date_label.SetForegroundColour(text_color)
        topbar_sizer.AddStretchSpacer(1)
        topbar_sizer.Add(date_label, 0, wx.ALIGN_CENTER_VERTICAL)
        topbar_sizer.AddStretchSpacer(1)

        # Right: plus and menu icons
        plus_btn = wx.Button(topbar, label="+", style=wx.BU_EXACTFIT)
        plus_btn.SetBackgroundColour(topbar_color)
        plus_btn.SetForegroundColour(text_color)
        menu_btn = wx.Button(topbar, label="≡", style=wx.BU_EXACTFIT)
        menu_btn.SetBackgroundColour(topbar_color)
        menu_btn.SetForegroundColour(text_color)
        topbar_sizer.Add(plus_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)
        topbar_sizer.Add(menu_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 6)

        main_sizer.Add(topbar, 0, wx.EXPAND)

        # Content area: horizontal split (sidebar + main)
        content_panel = wx.Panel(self)
        content_panel.SetBackgroundColour(bg_color)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_panel.SetSizer(content_sizer)

        # Sidebar
        sidebar = wx.Panel(content_panel)
        sidebar.SetBackgroundColour(sidebar_color)
        sidebar.SetMinSize((120, -1))
        sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        sidebar.SetSizer(sidebar_sizer)
        # esempio elementi sidebar (vuoto grigio scuro come nell'immagine)
        for i in range(6):
            item = wx.Panel(sidebar, size=(-1, 40))
            item.SetBackgroundColour(sidebar_color)
            sidebar_sizer.Add(item, 0, wx.EXPAND | wx.ALL, 2)

        content_sizer.Add(sidebar, 0, wx.EXPAND)

        # Main area (scuro)
        main_area = wx.Panel(content_panel)
        main_area.SetBackgroundColour("#2f2f2f")
        main_area_sizer = wx.BoxSizer(wx.VERTICAL)
        main_area.SetSizer(main_area_sizer)

        # Lista mock (ListCtrl o semplici pannelli)
        list_scroller = wx.ScrolledWindow(main_area, style=wx.VSCROLL)
        list_scroller.SetScrollRate(5, 5)
        list_scroller.SetBackgroundColour("#2f2f2f")
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_scroller.SetSizer(list_sizer)

        # Aggiungo elementi di esempio
        for i in range(8):
            row = wx.Panel(list_scroller)
            row.SetBackgroundColour("#3a3a3a")
            row_s = wx.BoxSizer(wx.HORIZONTAL)
            row.SetSizer(row_s)
            lbl = wx.StaticText(row, label=f"Task example {i+1}")
            lbl.SetForegroundColour(text_color)
            time_lbl = wx.StaticText(row, label="00:30")
            time_lbl.SetForegroundColour(text_color)
            row_s.Add(lbl, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
            row_s.Add(time_lbl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)
            list_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 4)

        main_area_sizer.Add(list_scroller, 1, wx.EXPAND | wx.ALL, 6)

        # Bottom total bar
        bottom_bar = wx.Panel(main_area)
        bottom_bar.SetBackgroundColour(bg_color)
        bottom_s = wx.BoxSizer(wx.HORIZONTAL)
        bottom_bar.SetSizer(bottom_s)
        total_label = wx.StaticText(bottom_bar, label="Total:")
        total_label.SetForegroundColour(text_color)
        total_time = wx.StaticText(bottom_bar, label="4:00")
        total_time.SetForegroundColour(text_color)
        bottom_s.Add(total_label, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 8)
        bottom_s.AddStretchSpacer(1)
        bottom_s.Add(total_time, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)

        main_area_sizer.Add(bottom_bar, 0, wx.EXPAND | wx.BOTTOM, 6)

        content_sizer.Add(main_area, 1, wx.EXPAND)

        main_sizer.Add(content_panel, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()
        self.Centre()

