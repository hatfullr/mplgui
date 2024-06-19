# https://github.com/matplotlib/matplotlib/blob/1ff14f140546b8df3f17543ff8dac3ddd210c0f1/lib/matplotlib/backends/_backend_tk.py#L834-L881
# Heavily edited

import tkinter as tk

class ToolTip:
    """
    Tooltip recipe from
    http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
    """
    def __init__(self, widget, text = ''):
        self.widget = widget
        self._text = text
        self._label = None
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        widget.bind('<Enter>', self.show)
        widget.bind('<Leave>', self.hide)

    @property
    def text(self): return self._text
    @text.setter
    def text(self, value):
        if self._text == value: return
        self._text = value
        if self._label is not None:
            self._label.configure(text = value)
            self._label.update_idletasks()
    
    def show(self, *args, **kwargs):
        """Display text in tooltip window."""
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.widget.winfo_width()
        y = y + self.widget.winfo_rooty()
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        self._label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         relief=tk.SOLID, borderwidth=1)
        self._label.pack(ipadx=1)
    
    def hide(self, *args, **kwargs):
        tw = self.tipwindow
        self.tipwindow = None
        self._label = None
        if tw:
            tw.destroy()
