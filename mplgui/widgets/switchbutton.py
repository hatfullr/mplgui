import tkinter as tk
from tkinter import ttk


class SwitchButton(ttk.Button, object):
    style = None
    def __init__(
            self,
            *args,
            variable = None,
            indicatoron = False,
            offrelief = 'flat',
            overrelief = 'groove',
            borderwidth = 1,
            height = 0,
            command = None,
            **kwargs
    ):
        if SwitchButton.style is None: SwitchButton.initialize_style()
        
        if variable is None: variable = tk.BooleanVar()
        self._variable = variable
        self._command = command
        super(SwitchButton, self).__init__(
            *args,
            style = SwitchButton.style,
            command = self.onpress,
            **kwargs
        )

        # Set initial state
        self.state(['pressed'] if self._variable.get() else ['!pressed'])

        def onchange(*a, **k):
            self.state(['pressed'] if self._variable.get() else ['!pressed'])
        self._variable.trace('w', onchange)
    
    @classmethod
    def initialize_style(cls):
        cls.style = 'SwitchButton.TButton'
        s = ttk.Style()
        s.map(
            cls.style,
            relief = [
                (('pressed','disabled'),'sunken'),
                (('pressed','!disabled'), 'sunken'),
                (('!pressed','disabled'),'raised'),
                (('!pressed','!disabled'),'raised'),
            ],
        )
    
    def toggle(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def onpress(self, *args, **kwargs):
        if 'disabled' not in self.state():
            self._variable.set(not self._variable.get())
        if self._command is not None and self.winfo_ismapped():
            self._command(*args, **kwargs)
