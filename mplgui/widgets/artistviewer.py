import tkinter as tk
from tkinter import ttk
import matplotlib.artist
import mplgui.widgets.verticalscrolledframe
import mplgui.lib.backend

class ArtistViewer(tk.Frame, object):
    def __init__(
            self,
            *args,
            width : int = 200,
            relief : str = 'sunken',
            borderwidth : int = 1,
            **kwargs
    ):
        self._artist = None
        super(ArtistViewer, self).__init__(
            *args,
            width = width,
            relief = relief,
            borderwidth = borderwidth,
            **kwargs
        )
        self._variable = tk.StringVar()
        self._properties = {}
        self._create_widgets()
        self._create_bindings()

    def _create_widgets(self, *args, **kwargs):
        self._names = tk.Listbox(
            self,
            selectmode = 'single',
            exportselection = False,
        )

        frame = tk.Frame(self)
        
        self._entry = ttk.Entry(
            frame,
            textvariable = self._variable,
        )
        self._set_button = ttk.Button(
            frame,
            text = 'Set',
            width = 4,
            command = self._on_set_pressed,
        )
        self._entry.pack(side = 'left', fill = 'x', expand = True)
        self._set_button.pack(side = 'left', padx = (5, 0))
        self._names.pack(side = 'top', fill = 'both', expand = True)
        frame.pack(side = 'top', fill = 'x')

    def _create_bindings(self, *args, **kwargs):
        self._names.bind('<<ListboxSelect>>', self._on_select, '+')

    def _on_select(self, *args, **kwargs):
        self._set_button.configure(state = 'normal')
        self._entry.configure(state = 'normal')

        self._variable.set(
            self._properties.get(
                self._names.get(self._names.curselection()),
                '',
            ),
        )
    
    def _on_set_pressed(self, *args, **kwargs):
        name = self._names.get(self._names.curselection())
        try:
            attr = getattr(self._artist, 'set_'+name)
            try:
                attr(self._variable.get())
            except:
                attr(eval(self._variable.get()))
            print("Now drawing", self._variable.get())
            canvas = self._artist.get_figure().canvas
            canvas.draw()#renderer = canvas.get_renderer())
            #fig.canvas.
            #self._artist.get_figure().canvas.get_tk_widget().update()
        except:
            mplgui.lib.backend.showerror()
        
        

    def get_artist(self): return self._artist
    
    def set_artist(
            self,
            artist : matplotlib.artist.Artist,
    ):
        self._artist = artist
        self._update_widgets()

    def _update_widgets(self, *args, **kwargs):
        inspector = matplotlib.artist.ArtistInspector(self._artist)
        setters = inspector.get_setters()

        self._properties.clear()
        for s in setters:
            getter = 'get_'+s
            if hasattr(self._artist, getter):
                self._properties[s] = getattr(self._artist, getter)()

        names = sorted(list(self._properties.keys()))

        self._names.delete(0, 'end')
        for name in names:
            self._names.insert('end', name)

        self._set_button.configure(state = 'disabled')
        self._entry.configure(state = 'disabled')

