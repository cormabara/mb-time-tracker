"""
Provides a wx.Dialog for managing categories and activities.

This module defines the TtDbSetupDialog class, which allows users to
interact with and manage two main sections: categories and activities.
The dialog includes functionality to view a list of entries, and interact
with them using options to add, edit, or remove items. Additionally,
the dialog is configurable with a parent window and integrates buttons
for closing the interface.

Classes:
    TtDbSetupDialog: Represents a dialog encompassing categories and
    activities management functionalities.

Functions:
    Not applicable (methods are encapsulated within the TtDbSetupDialog class).
"""

import wx


class TtDbSetupDialog(wx.Dialog):
    """
    Dialog for managing categories and activities in a structured manner.

    This class represents a dialog window that allows users to view, add, edit,
    and remove categories and activities. The dialog includes two main columns
    for categories and activities, each with their own set of controls and buttons
    for interaction. Users can switch between tabs, manage data, and close the dialog
    using the provided buttons.

    Attributes:
        ID_DEAL_ADD: Unique identifier for the "Add Category" button.
        ID_DEAL_REMOVE: Unique identifier for the "Remove Category" button.
        ID_DEAL_EDIT: Unique identifier for the "Edit Category" button.
        ID_ACTIVITY_ADD: Unique identifier for the "Add Activity" button.
        ID_ACTIVITY_REMOVE: Unique identifier for the "Remove Activity" button.
        ID_ACTIVITY_EDIT: Unique identifier for the "Edit Activity" button.

    Parameters:
        parent_ (wx.Window): The parent window of this dialog.
    """
    ID_DEAL_ADD = wx.NewIdRef()
    ID_DEAL_REMOVE = wx.NewIdRef()
    ID_DEAL_EDIT = wx.NewIdRef()
    ID_ACTIVITY_ADD = wx.NewIdRef()
    ID_ACTIVITY_REMOVE = wx.NewIdRef()
    ID_ACTIVITY_EDIT = wx.NewIdRef()

    def __init__(self,parent_):
        super().__init__(parent_)
        self._build_ui()

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

        self.act_add.Bind(wx.EVT_BUTTON, self.on_activity_add)
        self.act_remove.Bind(wx.EVT_BUTTON, self.on_activity_remove)
        self.act_edit.Bind(wx.EVT_BUTTON, self.on_activity_edit)

        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())

    def on_deal_selected(self, event):
        pass

    def on_deal_add(self, event):
        pass

    def on_deal_remove(self,event):
        pass

    def on_deal_edit(self,event):
        pass

    def on_activity_add(self,event):
        pass

    def on_activity_remove(self,event):
        pass

    def on_activity_edit(self,event):
        pass
