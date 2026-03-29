import wx
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
