import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import mplgui
import os
import matplotlib.backends._backend_tk
import collections
import mplgui.widgets.message
import mplgui.widgets.expandbutton

IMPORT_IMAGE = os.path.join(mplgui.ICONS_DIRECTORY, 'import_large.png')
ERASE_IMAGE = os.path.join(mplgui.ICONS_DIRECTORY, 'erase_large.png')

class AxesToolbar(matplotlib.backends._backend_tk.NavigationToolbar2Tk, object):
    toolitems = (
        ('Import', 'Import data', 'home', '_on_import_pressed'),
        ('Erase', 'Remove all artists', 'home', '_on_erase_pressed'),
    )
    
    def __init__(self, *args, **kwargs):
        self.is_expanded = tk.BooleanVar(value = True)
        
        kwargs['pack_toolbar'] = False
        super(AxesToolbar, self).__init__(*args, **kwargs)
        
        self.axes = None
        self._ondraw_bid = None
        
        self._create_widgets()
        self._create_bindings()

    def _create_widgets(self, *args, **kwargs):
        self._buttons['Import']._image_file = IMPORT_IMAGE
        self._buttons['Erase']._image_file = ERASE_IMAGE
        
        for key, button in self._buttons.items():
            button.configure(relief = 'raised')
            self._set_image_for_button(button)
        
        for widget in self.winfo_children():
            if widget in self._buttons.values(): continue
            widget.destroy()

        self._expand_button = mplgui.widgets.expandbutton.ExpandButton(
            self._buttons['Import'].master,
            width = 1,
            height = 1,
        )
        self._expand_button.pack(
            side = 'left',
            anchor = 'ne',
        )
        self._expand_button.toggle()


    def _create_bindings(self, *args, **kwargs):
        self.canvas.mpl_connect('motion_notify_event', self._update_position)
        self.canvas.mpl_connect('figure_leave_event', self._update_position)
        self._expand_button.bind('<<Expand>>', self._on_expand, '+')
        self._expand_button.bind('<<Collapse>>', self._on_collapse, '+')
        
    def _on_import_pressed(self, *args, **kwargs):
        ImportWindow(self.axes, self.winfo_toplevel())
        self.place_forget()

    def _on_erase_pressed(self, *args, **kwargs):
        if mplgui.widgets.message.ask(
                title = 'Clear the Axes?',
                text = 'Are you sure you want to clear the Axes?',
                detail = 'All artists will be removed from the Axes. This cannot be undone.',
        ):
            for child in self.axes.get_children():
                if child in [
                        self.axes.xaxis, self.axes.yaxis,
                        self.axes.patch,
                        *self.axes.spines.values(),
                ]: continue
                try: child.remove()
                except NotImplementedError: pass
            
            self.canvas.draw()
            self.canvas.blit()

    def _on_expand(self, *args, **kwargs):
        self._expand_button.pack(side = 'right')
        for button in self._buttons.values():
            button.pack(side = 'left')
    
    def _on_collapse(self, *args, **kwargs):
        for button in self._buttons.values():
            button.pack_forget()

    def _update_position(self, event = None):
        if event is not None:
            if hasattr(event, 'inaxes'):
                if event.inaxes is None: self.axes = None
                else:
                    # Ignore colorbars
                    if hasattr(event.inaxes, '_colorbar'): self.axes = None
                    else: self.axes = event.inaxes
            else: self.axes = None
        
        if self.axes is None:
            if self.winfo_ismapped():
                self.place_forget()
                self.canvas.mpl_disconnect(self._ondraw_bid)
                self._ondraw_bid = None
        else:
            pos = self.axes.get_position()
            self.place(
                anchor = 'ne',
                relx = pos.x1,
                rely = 1. - pos.y1,
            )

            if self._ondraw_bid is None:
                self._ondraw_bid = self.canvas.mpl_connect('draw_event', self._update_position)

class ImportWindow(tk.Toplevel, object):
    def __init__(self, axes, *args, **kwargs):
        import mplgui.lib.reader
        
        self.axes = axes
        super(ImportWindow, self).__init__(*args, **kwargs)

        self.title('Import data')
        
        self._readers = collections.OrderedDict()
        default, user = mplgui.lib.reader.get_readers()
        for _class in default:
            self._readers[_class.__name__] = _class
        for _class in user:
            self._readers[_class.__name__] = _class
        
        self._create_widgets()
        self._create_bindings()

    def _create_widgets(self, *args, **kwargs):
        file_frame = tk.Frame(self)
        self.entry = ttk.Entry(
            file_frame,
            state = 'readonly',
            width = 30,
        )
        self.browse_button = ttk.Button(
            file_frame,
            text = 'Browse',
            command = self.browse,
        )
        
        self.entry.pack(side = 'left', expand = True, fill ='x')
        self.browse_button.pack(side = 'left', padx = (5, 0))


        reader_frame = tk.Frame(self)
        ttk.Label(reader_frame, text = 'Reader').pack(side = 'left', padx = (0, 5))
        self.reader_combobox = ttk.Combobox(
            reader_frame,
            state = 'readonly',
            values = list(self._readers.keys()),
        )
        self.reader_combobox.pack(side = 'left', fill='x', expand = True)
        

        buttons_frame = tk.Frame(self)
        ttk.Label(buttons_frame).pack(side = 'left', fill='x', expand = True)
        self.import_button = ttk.Button(
            buttons_frame,
            text = 'Import',
            command = self.do_import,
            state = 'disabled',
        )
        self.import_button.pack(side = 'left', padx = 5)
        ttk.Button(
            buttons_frame,
            text = 'Cancel',
            command = self.destroy,
        ).pack(side = 'left', padx = (0, 5))
        
        file_frame.pack(side='top', fill = 'x', pady = (5, 0), padx = 5)
        reader_frame.pack(side = 'top', fill = 'x', pady = 5, padx = 5)
        buttons_frame.pack(
            side = 'top',
            fill = 'x',
            expand=True,
            pady = 5,
            anchor = 'se',
        )

    def _create_bindings(self, *args, **kwargs):
        def on_combobox_selected(*args, **kwargs):
            if self.entry.get().strip():
                self.import_button.configure(state = 'normal')
            
        self.reader_combobox.bind('<<ComboboxSelected>>', on_combobox_selected, '+')

    def browse(self, *args, **kwargs):
        import mplgui.lib.backend

        filename = filedialog.askopenfilename(
            master = self,
            title = 'Import data...',
        )
        
        self.entry.configure(state = 'normal')
        self.entry.delete(0, 'end')
        self.entry.insert(0, filename)
        self.entry.configure(state = 'readonly')

        if self.entry.get().strip() and self.reader_combobox.get().strip():
            self.import_button.configure(state = 'normal')

    def do_import(self, *args, **kwargs):
        reader = self._readers[self.reader_combobox.get()]()
        reader.read(self.axes, self.entry.get())
        self.axes.get_figure().canvas.draw()
        self.axes.get_figure().canvas.blit()
        self.destroy()
