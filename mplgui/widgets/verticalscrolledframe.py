import tkinter as tk
from tkinter import ttk
import copy

# https://stackoverflow.com/a/37861801/4954083

class VerticalScrolledFrame(tk.Frame, object):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected 
    to canvas scrollregion.

    2. self._interior is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>._interior
    to get them inserted into canvas
    """
    def __init__(self, *args, **kwargs):
        super(VerticalScrolledFrame, self).__init__(*args, **kwargs)
        
        bg = kwargs.get(
            'background',
            kwargs.get(
                'bg',
                ttk.Style().lookup('TFrame','background'),
            ),
        )
        
        # creating a canvas
        self._canv = tk.Canvas(
            self,
            borderwidth=0,
            highlightthickness=0,
            background=bg,
            name = 'canvas',
        )
        
        # creating a frame to insert to canvas
        kw = copy.deepcopy(kwargs)
        kw['borderwidth'] = 0
        kw['highlightthickness'] = 0
        kw['background'] = bg
        kw['name'] = 'interior'
        self._interior = tk.Frame(
            self._canv,
            **kw
        )
        self._yscrlbr = ttk.Scrollbar(self, name='yscrlbr')
        
        self._yscrlbr.config(command = self._canv.yview)
        self._interior_id = self._canv.create_window(0, 0, window = self._interior, anchor = 'nw')
        self._canv.config(yscrollcommand = self._yscrlbr.set)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._yscrlbr.grid(column = 1, row = 0, sticky = 'nes')
        self._canv.grid(column = 0, row = 0, sticky = 'news')

        self._canv.bind('<Configure>', self._configure_canvas)
        self._interior.bind('<Configure>', self._configure_interior)
        self.bind('<Enter>', self._on_Enter)
        self.bind('<Leave>', self._on_Leave)

        self._bind_buttons = ['<MouseWheel>','<Button-4>','<Button-5>']
        
    def _on_Enter(self, event):
        for button in self._bind_buttons:
            self._canv.bind_all(button,self._on_mousewheel)
        self._yscrlbr.bind("<B1-Motion>",self._on_B1Motion)
    
    def _on_Leave(self, event):
        for button in self._bind_buttons:
            self._canv.unbind_all(button)
        self._yscrlbr.unbind("<B1-Motion>")

    def _on_B1Motion(self, event):
        if self._yscrlbr.get() == (0.0,1.0): return "break"
            
    def _on_mousewheel(self, event):
        if event.num in [4,5]: # Linux
            if event.num == 5:
                self._scroll(1,'units')
            elif event.num == 4:
                self._scroll(-1,'units')
        else: # Windows
            self._scroll(int(-1*(event.delta/120)), "units")

    def _scroll(self,amount,units):
        if self._yscrlbr.get() != (0.0,1.0):
            self._canv.yview_scroll(amount,units)
            
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self._interior.winfo_reqwidth(), self._interior.winfo_reqheight())
        self._canv.config(scrollregion='0 0 %s %s' % size)
        if size[0] != self._canv.winfo_width():
            self._canv.config(width=size[0])
    
    def _configure_canvas(self, event):
        if self._interior.winfo_reqwidth() != self._canv.winfo_width():
            # update the inner frame's width to fill the canvas
            self._canv.itemconfigure(self._interior_id, width=self._canv.winfo_width())
    
