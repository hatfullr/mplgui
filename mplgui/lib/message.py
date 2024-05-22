import tkinter as tk
import _tkinter
from tkinter import ttk
import textwrap
import traceback
import sys
import mplgui

class Message(ttk.Label, object):
    def __init__(
            self,
            *args,
            duration : int | float | type(None) = None,
            **kwargs
    ):
        if duration is None:
            duration = mplgui.preferences.message['duration']
        
        self.duration = duration

        self.level = None
        
        super(Message, self).__init__(*args, **kwargs)
        self._wait_then_hide_id = None

        self._bind_functions()

        self.hide()

    def _bind_functions(self, *args, **kwargs):
        self.bind('<Enter>', self.cancel_wait_then_hide, '+')
        self.bind('<Leave>', self.wait_then_hide, '+')

    def cancel_wait_then_hide(self, *args, **kwargs):
        if self._wait_then_hide_id is not None:
            self.after_cancel(self._wait_then_hide_id)
        self._wait_then_hide_id = None

    def wait_then_hide(self, *args, **kwargs):
        if self._wait_then_hide_id is not None: self.cancel_wait_then_hide()
        self._wait_then_hide_id = self.after(self.duration, self.hide)
    
    def set(self, value, level = None):
        if self.level is not None:
            if level is None: return
            if level < self.level: return
        self.level = level
        try:
            if self.winfo_ismapped():
                self.configure(text = value)
                self.show()
        except _tkinter.TclError:
            pass
    
    def get(self, *args, **kwargs):
        return str(self.cget('text'))
    
    def hide(self, *args, **kwargs):
        self.cancel_wait_then_hide()
        self.place_forget()
        self.level = None
    
    def show(self, *args, **kwargs):
        self.cancel_wait_then_hide()
        self.place(**mplgui.preferences.message.get('place', {}))
        self.wait_then_hide()

    
    

class ErrorMessage(tk.Toplevel,object):
    width = 600
    height = 400
    
    def __init__(self):
        style = ttk.Style()

        details = traceback.format_exc()
        
        super(ErrorMessage, self).__init__(
            background=style.lookup('TFrame','background',state=['!disabled']),
            pady=5,
            padx=5,
        )
        
        self.withdraw()

        self.configure(width = ErrorMessage.width, height = ErrorMessage.height)
        
        # Set other window options
        self.title('Error')
        self.resizable(False, False)
        self.tk.call('wm', 'iconphoto', self._w, '::tk::icons::error')
        
        # Create the widgets
        message_frame = tk.Frame(
            self,
            background=self.cget('background'),
        )
        text_frame = ttk.Frame(self)
        button_frame = ttk.Frame(self)
        textbox = tk.Text(
            text_frame,
            wrap = 'word',
        )

        error_icon = tk.Label(
            message_frame,
            image = '::tk::icons::error',
            background = self.cget('background'),
        )
        
        message = ttk.Label(
            message_frame,
            text = str(sys.exc_info()[1]),
            justify = 'left',
            background = self.cget('background'),
            wraplength = ErrorMessage.width,
        )
        
        ok_button = ttk.Button(
            button_frame,
            text="Ok",
            command = self.destroy,
        )
        
        vscrollb = ttk.Scrollbar(text_frame,command=textbox.yview)
        
        
        textbox.insert('1.0', details)
        textbox.config(
            state = 'disabled',
            yscrollcommand = vscrollb.set,
        )

        self.minsize(width=ErrorMessage.width,height=ErrorMessage.height)
        self.maxsize(width=ErrorMessage.width,height=ErrorMessage.height)
        
        # Pack the widgets
        error_icon.pack(side = 'left', padx = 10, pady = 10)
        message.pack(side = 'left', anchor='w')
        message_frame.pack(side='top',fill='x',pady=(0,5))
        ok_button.pack(side='left', anchor = 'e', expand = True)
        button_frame.pack(side='bottom', fill='x', expand = True)
        text_frame.pack(side='bottom',pady=5)

        vscrollb.pack(side='right',fill='y')
        textbox.pack(fill = 'both', expand = True)
        
        self.grab_set()
        self.transient()
        self.deiconify()

