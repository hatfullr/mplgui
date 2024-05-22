import tkinter as tk
from tkinter import ttk

class ScrollTreeview(ttk.Treeview, object):
    def __init__(
            self,
            master,
            *args,
            horizontal_scrollbar : bool = True,
            vertical_scrollbar : bool = True,
            width : int = 400,
            **kwargs
    ):
        self._container = tk.Frame(master, width = width)
        super(ScrollTreeview, self).__init__(self._container, *args, **kwargs)
        self._initialize(horizontal_scrollbar, vertical_scrollbar)
    
    def pack(self, *args, **kwargs):
        return self._container.pack(*args, **kwargs)
    def place(self, *args, **kwargs):
        return self._container.place(*args, **kwargs)
    def grid(self, *args, **kwargs):
        return self._container.grid(*args, **kwargs)
    
    def _initialize(
            self,
            horizontal_scrollbar : bool,
            vertical_scrollbar : bool,
    ):
        self.scrollbars = {}
        if vertical_scrollbar:
            self.vertical_scrollbar = ttk.Scrollbar(
                self._container,
                orient = 'vertical',
                command = self.yview,
            )
            self.configure(yscrollcommand = self.vertical_scrollbar)
            self.vertical_scrollbar.grid(row = 0, column = 1, sticky = 'ns')
            self.rowconfigure(0, weight = 1)
        if horizontal_scrollbar:
            self.horizontal_scrollbar = ttk.Scrollbar(
                self._container,
                orient = 'horizontal',
                command = self.xview,
            )
            self.configure(xscrollcommand = self.horizontal_scrollbar)
            self.horizontal_scrollbar.grid(row = 1, column = 0, sticky = 'we')
            self.columnconfigure(0, weight = 1)
        
        super(ScrollTreeview, self).grid(row = 0, column = 0, sticky = 'news')
        
        self._container.columnconfigure(0, weight = 1)
        self._container.rowconfigure(0, weight = 1)

    def get_all_children(self, *args, **kwargs):
        def get(item):
            yield item
            for child in self.get_children(item):
                yield from get(child)

        children = []
        for child in self.get_children():
            for c in get(child):
                children += [c]
        
        return children
