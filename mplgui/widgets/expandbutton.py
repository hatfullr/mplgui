from tkinter import ttk
import tkinter as tk


class ExpandButton(tk.Checkbutton, object):
    def __init__(
            self,
            *args,
            direction = 'horizontal',
            expand = None,
            textvariable = None,
            variable = None,
            indicatoron = False,
            offrelief = 'flat',
            overrelief = 'groove',
            borderwidth = 1,
            **kwargs
    ):
        self._textvariable = tk.StringVar()
        
        if variable is None: variable = tk.BooleanVar()
        self._variable = variable
        super(ExpandButton, self).__init__(
            *args,
            textvariable = self._textvariable,
            variable = self._variable,
            indicatoron = indicatoron,
            offrelief = offrelief,
            overrelief = overrelief,
            borderwidth = borderwidth,
            **kwargs
        )
        self._expandedvalue = None
        self._collapsedvalue = None
        if expand is None:
            if direction == 'horizontal': expand = 'left'
            else: expand = 'down'
        self.set_direction(direction, expand)

        def on_var_changed(*args, **kwargs):
            if variable.get():
                self._textvariable.set(self._expandedvalue)
                self.event_generate('<<Expand>>')
            else:
                self._textvariable.set(self._collapsedvalue)
                self.event_generate('<<Collapse>>')
        
        variable.trace_add('write', on_var_changed)

    def set_direction(self, value, expand):
        if value not in ['horizontal', 'vertical']:
            raise ValueError("'direction' must be one of 'horizontal' or 'vertical', not '%s'" % str(value))

        if value == 'horizontal' and expand not in ['left', 'right']:
            raise ValueError("'expand' must be one of 'left' or 'right' when 'direction' is 'horizontal', not '%s'" % str(expand))
        if value == 'vertical' and expand not in ['up', 'down']:
            raise ValueError("'expand' must be one of 'up' or 'down' when 'direction' is 'vertical', not '%s'" % str(expand))
        
        self._direction = value
        
        if self._direction == 'horizontal':
            if expand == 'left':
                self._expandedvalue = '>'
                self._collapsedvalue = '<'
            else:
                self._expandedvalue = '<'
                self._collapsedvalue = '>'
        else:
            if expand == 'up':
                self._expandedvalue = 'v'
                self._collapsedvalue = '^'
            else:
                self._expandedvalue = '^'
                self._collapsedvalue = 'v'

        if self._variable.get(): self._textvariable.set(self._expandedvalue)
        else: self._textvariable.set(self._collapsedvalue)
