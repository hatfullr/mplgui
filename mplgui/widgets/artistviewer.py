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
            relief : str = 'flat',
            borderwidth : int = 0,
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
        def on_up_down(event):
            selection = event.widget.curselection()[0]
            if event.keysym == 'Up': selection += -1
            if event.keysym == 'Down': selection += 1
            if 0 <= selection < event.widget.size():
                event.widget.selection_clear(0, tk.END)
                event.widget.select_set(selection)
        
        self._names.bind('<Down>', on_up_down, '+')
        self._names.bind('<Up>', on_up_down, '+')
        self._names.bind('<<ListboxSelect>>', self._on_select, '+')

        self._variable.trace_add('write', self._on_variable_set)

    def _on_variable_set(self, *args, **kwargs):
        orig = str(self._properties[self._names.get(self._names.curselection())])
        self._set_button.configure(
            state = 'normal' if self._variable.get() != orig else 'disabled',
        )
        
    def _on_select(self, *args, **kwargs):
        if self._names.curselection():
            self._set_button.configure(state = 'disabled')
            self._entry.configure(state = 'normal')
            
            self._variable.set(
                str(self._properties.get(
                    self._names.get(self._names.curselection()),
                    '',
                ))
            )
    
    def _on_set_pressed(self, *args, **kwargs):
        name = self._names.get(self._names.curselection())
        try:
            text = self._variable.get()
            get_attr = getattr(self._artist, 'get_'+name)
            # Do nothing if nothing was changed
            current = self._properties[self._names.get(self._names.curselection())]
            if text == str(current): return 'break'
            set_attr = getattr(self._artist, 'set_'+name)
            try:
                set_attr(text)
            except:
                set_attr(eval(text))
            self._properties[self._names.get(self._names.curselection())] = getattr(self._artist, 'get_'+name)()
            canvas = self._artist.get_figure().canvas
            canvas.draw()
            canvas.blit()
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
        curselection = self._names.curselection()
        previous_name = None
        if curselection:
            previous_name = self._names.get(curselection)
        
        inspector = matplotlib.artist.ArtistInspector(self._artist)
        setters = inspector.get_setters()
        
        self._properties.clear()
        for s in setters:
            getter = 'get_'+s
            if hasattr(self._artist, getter):
                obj = getattr(self._artist, getter)()
                if obj.__class__.__module__ != 'builtins': continue
                self._properties[s] = obj
        
        names = sorted(list(self._properties.keys()))
        
        self._names.delete(0, 'end')
        for name in names:
            self._names.insert('end', name)

        # Reset the selection back to what it was before
        if curselection:
            # Some values don't change, but that's because of the
            # update_from method in Matplotlib, not our fault.
            self._names.select_set(curselection)
        
        self._set_button.configure(state = 'disabled')
        self._entry.configure(state = 'disabled')

