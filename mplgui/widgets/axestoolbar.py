import tkinter as tk
from tkinter import ttk

class AxesToolbar(tk.Frame, object):
    def __init__(
            self,
            canvas,
            *args,
            **kwargs
    ):
        self.canvas = canvas
        super(AxesToolbar, self).__init__(*args, **kwargs)
        self._create_widgets()

        self.canvas.mpl_connect('axes_enter_event', self._on_mouse_enter_axes)
        self.canvas.mpl_connect('axes_leave_event', self._on_mouse_leave_axes)

    def _create_widgets(self, *args, **kwargs):
        self.import_button = ttk.Button(
            self,
            text = 'i',
            command = self._on_import_pressed,
            width = 1,
        )

        self.import_button.pack(side = 'left')

    def _on_mouse_enter_axes(self, event):
        pos = event.inaxes.get_position()
        self.place(
            anchor = 'ne',
            relx = pos.x1,
            rely = pos.y0,
        )

    def _on_mouse_leave_axes(self, event):
        self.place_forget()

    def _on_import_pressed(self, *args, **kwargs):
        pass
