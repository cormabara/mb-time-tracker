import calendar

import wx
import wx.adv
import datetime
from datetime import date, timedelta

from mb_logger import Logger
from mb_wx_gui import MbWxToolbar, MbWxStatusbar
from source.gui.wx_tt_setup_dialog import TtDbSetupDialog
from source.gui.wx_tt_task_dialog import TtTaskDialog
from source.tt_common import get_icon, GuiCol
from source.ttdatabase import TTDatabase




class CategoriesDialog(wx.Dialog):

    ID_DEAL_ADD = wx.NewIdRef()
    ID_DEAL_REMOVE = wx.NewIdRef()
    ID_DEAL_EDIT = wx.NewIdRef()
    ID_ACTIVITY_ADD = wx.NewIdRef()
    ID_ACTIVITY_REMOVE = wx.NewIdRef()
    ID_ACTIVITY_EDIT = wx.NewIdRef()

    def __init__(self, parent):
        super().__init__(parent, title="Time Tracker Preferences", size=(640,480))
        self._build_ui()
        self.deals = []  # list of (name, [activities])
        self._load_sample_data()
        self._update_categories_list()

    def _build_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self)
        page = wx.Panel(notebook)
        notebook.AddPage(page, "Categories and Tags")

        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top: two columns (Categories, Activities)
        columns_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Categories column
        cat_sizer = wx.BoxSizer(wx.VERTICAL)
        cat_label = wx.StaticText(page, label="Categories")
        cat_sizer.Add(cat_label, 0, wx.BOTTOM, 6)
        self.cat_list = wx.ListBox(page, style=wx.LB_SINGLE)
        cat_sizer.Add(self.cat_list, 1, wx.EXPAND)

        # category buttons (horizontal row)
        cat_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cat_add = wx.Button(page, self.ID_DEAL_ADD, label="+")
        self.cat_remove = wx.Button(page, self.ID_DEAL_REMOVE, label="-")
        self.cat_edit = wx.Button(page, self.ID_DEAL_EDIT, label="✎")
        cat_btn_sizer.Add(self.cat_add, 0, wx.RIGHT, 6)
        cat_btn_sizer.Add(self.cat_remove, 0, wx.RIGHT, 6)
        cat_btn_sizer.Add(self.cat_edit, 0)
        cat_sizer.Add(cat_btn_sizer, 0, wx.TOP, 6)

        columns_sizer.Add(cat_sizer, 1, wx.EXPAND | wx.RIGHT, 10)

        # Activities column
        act_sizer = wx.BoxSizer(wx.VERTICAL)
        act_label = wx.StaticText(page, label="Activities")
        act_sizer.Add(act_label, 0, wx.BOTTOM, 6)
        self.act_list = wx.ListBox(page)
        act_sizer.Add(self.act_list, 1, wx.EXPAND)

        act_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.act_add = wx.Button(page, self.ID_ACTIVITY_ADD, label="+")
        self.act_remove = wx.Button(page, self.ID_ACTIVITY_REMOVE, label="-")
        self.act_edit = wx.Button(page, self.ID_ACTIVITY_EDIT, label="✎")
        act_btn_sizer.Add(self.act_add, 0, wx.RIGHT, 6)
        act_btn_sizer.Add(self.act_remove, 0, wx.RIGHT, 6)
        act_btn_sizer.Add(self.act_edit, 0)
        act_sizer.Add(act_btn_sizer, 0, wx.TOP, 6)

        columns_sizer.Add(act_sizer, 1, wx.EXPAND)

        panel_sizer.Add(columns_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # Tags area (large text box for autocomplete tags)
        tags_label = wx.StaticText(page, label="Tags that should appear in autocomplete")
        panel_sizer.Add(tags_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.tags_ctrl = wx.TextCtrl(page, style=wx.TE_MULTILINE)
        panel_sizer.Add(self.tags_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        panel_sizer.AddStretchSpacer()

        page.SetSizer(panel_sizer)
        main_sizer.Add(notebook, 1, wx.EXPAND)

        # Bottom: Close button on right
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        close_btn = wx.Button(self, wx.ID_CLOSE, label="Close")
        btn_sizer.Add(close_btn, 0, wx.ALL, 8)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        # Bind events
        self.cat_list.Bind(wx.EVT_LISTBOX, self.on_deal_selected)
        self.cat_add.Bind(wx.EVT_BUTTON, self.on_deal_add)
        self.cat_remove.Bind(wx.EVT_BUTTON, self.on_deal_remove)
        self.cat_edit.Bind(wx.EVT_BUTTON, self.on_deal_edit)

        self.act_add.Bind(wx.EVT_BUTTON, self.on_act_add)
        self.act_remove.Bind(wx.EVT_BUTTON, self.on_act_remove)
        self.act_edit.Bind(wx.EVT_BUTTON, self.on_act_edit)

        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())

    def _load_sample_data(self):
        # sample data to show behavior
        self.deals = [
            ("Dxxxxxx - Permessi/Fer", ["permesso"]),
            ("Dyyyyyy - VSI (High Per)", ["activity 1", "activity 2"]),
            ("G130GEN12308 - Varie", []),
            ("G130GEN12309 - Training", []),
        ]

    def _update_categories_list(self):
        self.cat_list.Clear()
        for name, _ in self.deals:
            self.cat_list.Append(name)
        # select first if exists
        if self.cat_list.GetCount():
            self.cat_list.SetSelection(0)
            self.on_deal_selected(None)
        else:
            self.act_list.Clear()

    def on_deal_selected(self, event):
        idx = self.cat_list.GetSelection()
        if idx == wx.NOT_FOUND:
            self.act_list.Clear()
            return
        _, activities = self.deals[idx]
        self.act_list.Clear()
        for a in activities:
            self.act_list.Append(a)

    # Category actions
    def on_deal_add(self, event):
        dlg = wx.TextEntryDialog(self, "New category name:", "Add Category")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                self.deals.append((name, []))
                self._update_categories_list()
                self.cat_list.SetSelection(self.cat_list.GetCount()-1)
        dlg.Destroy()

    def on_deal_remove(self, event):
        idx = self.cat_list.GetSelection()
        if idx != wx.NOT_FOUND:
            name = self.deals[idx][0]
            if wx.MessageBox(f"Remove category '{name}'?", "Confirm", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                del self.deals[idx]
                self._update_categories_list()

    def on_deal_edit(self, event):
        idx = self.cat_list.GetSelection()
        if idx == wx.NOT_FOUND: return
        old = self.deals[idx][0]
        dlg = wx.TextEntryDialog(self, "Edit category name:", "Edit Category", value=old)
        if dlg.ShowModal() == wx.ID_OK:
            new = dlg.GetValue().strip()
            if new:
                self.deals[idx] = (new, self.deals[idx][1])
                self._update_categories_list()
                self.cat_list.SetSelection(idx)
        dlg.Destroy()

    # Activity actions
    def on_act_add(self, event):
        idx = self.cat_list.GetSelection()
        if idx == wx.NOT_FOUND:
            wx.MessageBox("Select a category first.")
            return
        dlg = wx.TextEntryDialog(self, "New activity name:", "Add Activity")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue().strip()
            if name:
                self.deals[idx][1].append(name)
                self.on_deal_selected(None)
                self.act_list.SetSelection(self.act_list.GetCount()-1)
        dlg.Destroy()

    def on_act_remove(self, event):
        cidx = self.cat_list.GetSelection()
        aidx = self.act_list.GetSelection()
        if cidx == wx.NOT_FOUND or aidx == wx.NOT_FOUND:
            return
        act = self.deals[cidx][1][aidx]
        if wx.MessageBox(f"Remove activity '{act}'?", "Confirm", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            del self.deals[cidx][1][aidx]
            self.on_deal_selected(None)

    def on_act_edit(self, event):
        cidx = self.cat_list.GetSelection()
        aidx = self.act_list.GetSelection()
        if cidx == wx.NOT_FOUND or aidx == wx.NOT_FOUND:
            return
        old = self.deals[cidx][1][aidx]
        dlg = wx.TextEntryDialog(self, "Edit activity name:", "Edit Activity", value=old)
        if dlg.ShowModal() == wx.ID_OK:
            new = dlg.GetValue().strip()
            if new:
                self.deals[cidx][1][aidx] = new
                self.on_deal_selected(None)
                self.act_list.SetSelection(aidx)
        dlg.Destroy()

class TtDateRangeDialog(wx.Dialog):
    """
    Dialog for selecting a date range in a user-friendly manner.

    The TtDateRangeDialog class provides a graphical interface for selecting
    a range of dates using quick options (Today, Week, Month) and two calendar
    widgets. The dialog ensures that the selected range is valid (the "From"
    date is not later than the "To" date). Users can confirm their selection
    with the "Apply" button.

    Attributes
    ----------
    today_tc : wx.TextCtrl
        Displays the current date in "Today" quick range.
    week_tc : wx.TextCtrl
        Displays the date range for the current week in the "Week" quick range.
    month_tc : wx.TextCtrl
        Displays the date range for the current month in the "Month" quick range.
    cal_from : wx.adv.CalendarCtrl
        Calendar widget for selecting the start date of the range.
    cal_to : wx.adv.CalendarCtrl
        Calendar widget for selecting the end date of the range.
    result : tuple of (date, date) or None
        The selected date range, containing the "From" and "To" dates as Python
        `date` objects. This attribute is populated after the user clicks "Apply"
        and closes the dialog.

    Methods
    -------
    _calculate_week_range(d: date) -> tuple[date, date]
        Calculates the start and end dates of the week for the given date.
    _calculate_month_range(d: date) -> tuple[date, date]
        Calculates the start and end dates of the month for the given date.
    on_apply(event: wx.CommandEvent)
        Event handler for applying the selected date range and closing the dialog.
    on_from_changed(event: wx.adv.CalendarEvent)
        Event handler to enforce validation when the "From" date is changed.
    on_to_changed(event: wx.adv.CalendarEvent)
        Event handler to enforce validation when the "To" date is changed.
    """
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

class TimeTask(wx.Panel):
    """
    Represents a panel for displaying detailed information about a task and its associated duration.

    A TimeTask panel is designed to present the duration and details of a task within an application’s
    user interface. This panel includes a visual representation of the task’s allocated hours,
    along with task-specific metadata including its associated deal, activity, and description.
    It provides a clean and structured layout for organizing task data.

    Attributes:
        duration (float): The duration of the task in hours, calculated from the number of minutes
            provided in the task data.
    """
    def __init__(self, parent, db_,task_):
        super().__init__(parent)

        self.SetBackgroundColour(GuiCol.SIDEBAR.wx())

        def add_separator(s_):
            line = wx.Panel(self, size=(2, -1))
            line.SetBackgroundColour(wx.Colour(150, 150, 150))
            s_.Add(line, 0,wx.EXPAND | wx.LEFT , 5)

        s = wx.BoxSizer(wx.HORIZONTAL)

        box_all = wx.BoxSizer(wx.HORIZONTAL)

        box_info = wx.BoxSizer(wx.VERTICAL)
        deal_name = db_.find_deal_from_id(task_["deal"])
        deal_label = wx.StaticText(self, style=wx.ALIGN_LEFT, label=f"{deal_name}")
        deal_label.MinSize = (400, -1)
        box_info.Add(deal_label, 0, wx.TOP | wx.ALL | wx.EXPAND, 2)
        activity_name = db_.find_activity_from_id(task_["activity"])
        activity_label = wx.StaticText(self, style=wx.ALIGN_LEFT, label=f"{activity_name}")
        box_info.Add(activity_label, 0, wx.BOTTOM | wx.ALL | wx.EXPAND, 2)
        box_all.Add(box_info, 0, wx.TOP | wx.ALL | wx.EXPAND, 2)

        add_separator(box_all)

        box_desc = wx.BoxSizer(wx.VERTICAL)

        description_label = wx.StaticText(self, label=f"{task_["description"]}",style=wx.ALIGN_LEFT)
        description_label.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        box_desc.Add(description_label, 0, wx.BOTTOM | wx.ALL | wx.EXPAND, 2)
        box_all.Add(box_desc, 0, wx.BOTTOM | wx.ALL | wx.EXPAND, 2)

        s.Add(box_all, 1, wx.ALL | wx.EXPAND | wx.RIGHT, 8)

        add_separator(s)

        self.duration = task_["minutes"] / 60
        dur_label = wx.StaticText(self, label=f"{self.duration}h")
        dur_label.SetForegroundColour(GuiCol.TEXT.wx())
        dur_label.SetMinSize((60, -1))
        dur_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        s.Add(dur_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 8)


        self.SetSizer(s)

class DaySlot(wx.Panel):
    """
    Represents a panel for displaying information about a specific day, including tasks scheduled
    for that day.

    The class initializes UI components including a sidebar with date information and a main area
    for displaying tasks. It integrates with a database and works with provided task data to create
    a meaningful and interactive user interface.

    Attributes:
        task_list (list[TimeTask]): A list to store instances of TimeTask associated with the day.

    Parameters:
        parent (wx.Window): The parent window or panel to which this panel belongs.
        date_ (datetime.date): The specific date this slot represents.
        db_ : The database object used to manage task data for the day.
        tasks (list[dict]): A list of task information where each task is represented as a dictionary.

    """
    def __init__(self,parent,date_:datetime.date,db_,tasks:list[dict]):
        super().__init__(parent)
        self.task_list: list[TimeTask] = []
        slot_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sidebar = wx.Panel(self)
        sidebar.SetBackgroundColour(GuiCol.SIDEBAR.wx())
        sidebar.SetMinSize((120, -1))
        day_sizer = wx.BoxSizer(wx.VERTICAL)
        day_lbl_big = wx.StaticText(sidebar, label=calendar.day_name[date_.weekday()] )
        day_lbl_big.SetForegroundColour(GuiCol.TEXT.wx())

        day_lbl_small = wx.StaticText(sidebar, label=f"{date_.year}/{date_.month}/{date_.day}")
        day_lbl_small.SetForegroundColour(GuiCol.TEXT.wx())
        day_sizer.Add(day_lbl_big, 0, wx.BOTTOM, 4)
        day_sizer.Add(day_lbl_small, 0)
        sidebar.SetSizer(day_sizer)

        tasks_area = wx.Panel(self)
        tasks_sizer = wx.BoxSizer(wx.VERTICAL)
        if tasks is not None:
            for task in tasks:
                row = TimeTask(tasks_area, db_, task)
                self.task_list.append(row)
                tasks_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 6)
        tasks_area.SetSizer(tasks_sizer)

        slot_sizer.Add(sidebar, 0, wx.EXPAND)
        slot_sizer.Add(tasks_area, 1, wx.EXPAND | wx.ALL, 6)
        self.SetSizer(slot_sizer)

class TTMainWin(wx.Frame):

    ID_TRACK_SETUP = wx.NewIdRef()
    ID_ABOUT = wx.NewIdRef()

    def __init__(self, db_:TTDatabase, parent=None):
        super().__init__(parent, title="Staubli Time Tracker", size=(1200,600))
        self.day_slot_list: list[DaySlot] = []
        self.db = db_
        today = datetime.date.today()
        self.start_date = today
        self.end_date = today

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top toolbar definition
        top = MbWxToolbar(self,height=32)
        top.SetBackgroundColour(GuiCol.BG.wx())
        self.back = top.add_img_button(get_icon("arrow-left.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_backward)
        self.forw = top.add_img_button(get_icon("arrow-right.png"), position=wx.LEFT, align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_slot_forward)
        self.date_slot = top.add_text_button("Slot button",wx.LEFT,wx.ALIGN_CENTER_VERTICAL,self.cb_pop_date_slot)
        top.add_spacer(4)

        self.today_slot = top.add_text_button("TODAY",wx.LEFT,wx.ALIGN_CENTER_VERTICAL,self.cb_slot_today)
        self.week_slot = top.add_text_button("WEEK",wx.LEFT,wx.ALIGN_CENTER_VERTICAL,self.cb_slot_this_week)
        top.add_spacer(4)

        plus = top.add_img_button(get_icon("plus.png"),position=wx.RIGHT)
        plus.Bind(wx.EVT_BUTTON, self.cb_add_time_task)
        top.add_img_button(get_icon("menu.png"),position=wx.RIGHT,align=wx.ALIGN_CENTER_VERTICAL, callback=self.cb_menu)
        self.menu = wx.Menu()
        self.menu.Append(self.ID_TRACK_SETUP, "Tracking settings")
        self.menu.AppendSeparator()
        self.menu.Append(self.ID_ABOUT, "About")
        self.Bind(wx.EVT_MENU, self.cb_tracking_settings, id=self.ID_TRACK_SETUP)
        self.Bind(wx.EVT_MENU, self.cb_about, id=self.ID_ABOUT)

        main_sizer.Add(top, 0, wx.EXPAND)

        # Content area
        content = wx.Panel(self)
        content.SetBackgroundColour(GuiCol.BG.wx())
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Data list area
        data_area = wx.Panel(content)
        data_area.SetBackgroundColour(GuiCol.BG.wx())
        data_sizer = wx.BoxSizer(wx.VERTICAL)
        data_area.SetSizer(data_sizer)

        # Scrolled list
        self.scroller = wx.ScrolledWindow(data_area, style=wx.VSCROLL)
        self.scroller.SetBackgroundColour(GuiCol.BG.wx())
        self.scroller.SetScrollRate(5,5)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroller.SetSizer(self.list_sizer)
        data_sizer.Add(self.scroller, 1, wx.EXPAND | wx.ALL, 6)
        content_sizer.Add(data_area, 1, wx.EXPAND)
        content.SetSizer(content_sizer)
        main_sizer.Add(content, 1, wx.EXPAND)

        # Bottom total bar
        bottom = MbWxStatusbar(self,height=32)
        bottom.SetBackgroundColour(GuiCol.BG.wx())
        self.total_label = bottom.add_text("Total: 0h")
        self.total_label.SetMinSize((400, -1))
        main_sizer.Add(bottom, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        # prepare the window
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)
        self.__refresh_total()
        self.Centre()

    def __update_slot_button(self):
        if self.start_date != self.end_date:
            self.date_slot.SetLabel(f" {self.start_date} to {self.end_date} ")
        else:
            self.date_slot.SetLabel(f" {self.start_date} ")

    def __populate_from_database(self,start_date:datetime.date,end_date:datetime.date):
        """
        Populates the list of day slots for the specified date range.

        This method is used to dynamically create and add day slots for each
        date in the given range. It iterates from the start date to the end
        date, clearing the current list, and adds slots for individual days
        before updating the layout of the scroller.

        Parameters:
            start_date: datetime.date
                The starting date of the range to be populated.
            end_date: datetime.date
                The ending date of the range to be populated.
        """
        def daterange(start: datetime.date, end: datetime.date):
            current = start
            while current <= end:
                yield current
                current += datetime.timedelta(days=1)

        self.list_sizer.Clear(True)
        self.day_slot_list.clear()
        for d in daterange(start_date, end_date):
            self.__add_day_slot(d)
            Logger().print(d)

        self.scroller.Layout()

    def __refresh_total(self):
        total = 0
        if self.day_slot_list:
            for slot in self.day_slot_list:
                if slot.task_list:
                   total = sum(t.duration for t in slot.task_list) + total

        self.total_label.SetLabel( f"Total: {total} [h]")

    def __update_data(self):
        self.__update_slot_button()
        self.__populate_from_database(self.start_date,self.end_date)
        self.__refresh_total()


    def __add_day_slot(self, day_:datetime.date):
        """
        Adds a new day slot to the interface and updates the view.

        This method initializes a new slot for tasks scheduled on the specified day.
        It retrieves tasks for the day from the database, creates a slot instance,
        adds the slot to the interface, and refreshes the total statistics.

        Parameters:
            day_ (datetime.date): The day for which the slot is being added.
        """
        tasks = self.db.find_tasks(day_,day_)
        slot = DaySlot(self.scroller, day_, self.db, tasks)
        self.list_sizer.Add(slot, 0, wx.EXPAND | wx.BOTTOM, 6)
        self.scroller.Layout()
        self.day_slot_list.append(slot)


    # ---------- Callbacks  ----------

    def cb_pop_date_slot(self, evt):
        Logger().print("pop date slot")
        dlg = TtDateRangeDialog(None, self.start_date, self.end_date)
        if dlg.ShowModal() == wx.ID_OK:
            self.start_date, self.end_date = dlg.result
            Logger().print(f"Start: {self.start_date}\nEnd: {self.end_date}")
        dlg.Destroy()
        self.__update_data()

    def cb_slot_today(self, evt):
        self.start_date = date.today()
        self.end_date = date.today()
        self.__update_data()

    def cb_slot_this_week(self, evt):
        today = date.today()
        self.start_date = today - datetime.timedelta(days=today.weekday())
        self.end_date = self.start_date + datetime.timedelta(days=6)
        self.__update_data()

    def cb_slot_backward(self, evt):
        delta = self.end_date - self.start_date

        if self.start_date != self.end_date:
            delta = (self.end_date - self.start_date) + datetime.timedelta(days=1)
            self.start_date = self.start_date - delta
            self.end_date = self.end_date - delta
        else:
            self.start_date = self.start_date - datetime.timedelta(days=1)
            self.end_date = self.end_date - datetime.timedelta(days=1)
        self.__update_data()

    def cb_slot_forward(self, evt):
        if self.start_date != self.end_date:
            delta = (self.end_date - self.start_date) + datetime.timedelta(days=1)
            self.start_date = self.start_date + delta
            self.end_date = self.end_date + delta
        else:
            self.start_date = self.start_date + datetime.timedelta(days=1)
            self.end_date = self.end_date + datetime.timedelta(days=1)
        self.__update_data()

    def cb_add_time_task(self, evt):
        # dialog semplice per aggiungere una riga (solo demo)
        dlg = TtTaskDialog(self, self.db, None)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                Logger().print("add task")
            except Exception as ex:
                Logger().print("Error adding a task")
        dlg.Destroy()
        self.__update_data()

    def cb_about(self,evt):
        pass

    def cb_menu(self, evt):
        btn = evt.GetEventObject()
        # Get position to popup the menu: below the button
        btn_pos = btn.ClientToScreen((0, btn.GetSize().y))
        self.PopupMenu(self.menu, self.ScreenToClient(btn_pos))

    def cb_tracking_settings(self,evt):
        dlg = TtDbSetupDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

