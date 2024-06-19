import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import mplgui
import os
import matplotlib.backends._backend_tk
import collections
import mplgui.widgets.message
import mplgui.widgets.expandbutton
import mplgui.lib.axeshighlight
import mplgui.widgets.tooltip

IMPORT_IMAGE = os.path.join(mplgui.ICONS_DIRECTORY, 'import_large.png')
ERASE_IMAGE = os.path.join(mplgui.ICONS_DIRECTORY, 'erase_large.png')

class AxesToolbar(matplotlib.backends._backend_tk.NavigationToolbar2Tk, object):
    toolitems = (
        ('Import', 'Import data', 'home', '_on_import_pressed'),
        ('Erase', 'Remove all artists', 'home', '_on_erase_pressed'),
    )
    
    def __init__(self, *args, **kwargs):
        kwargs['pack_toolbar'] = False
        super(AxesToolbar, self).__init__(*args, **kwargs)
        
        self._highlight = mplgui.lib.axeshighlight.AxesHighlight()
        self.axes = None
        self._spacers = []
        
        self._create_widgets()
        self._create_bindings()

    def _create_widgets(self, *args, **kwargs):
        self._buttons['Import']._image_file = IMPORT_IMAGE
        self._buttons['Erase']._image_file = ERASE_IMAGE
        
        self._buttons['Import'].master.configure(
            relief = 'raised', padx = 2, pady = 2,
        )
        
        for button in self._buttons.values():
            button.pack_forget()
        
        for key, button in self._buttons.items():
            button.configure(relief = 'raised')
            if key == 'Expand': continue
            self._set_image_for_button(button)
        
        for widget in self.winfo_children():
            if widget in self._buttons.values(): continue
            widget.destroy()

        self._highlight_on = tk.BooleanVar()
        height = self._buttons['Import'].winfo_reqheight()

        self._expand_button = mplgui.widgets.expandbutton.ExpandButton(
            self,
            width = 0,
            height = height,
            use_text = False,
        )
        self._expand_button.toggle()
        self._expand_tooltip = mplgui.widgets.tooltip.ToolTip(
            self._expand_button, text = 'Collapse',
        )
        
        self._highlight_on = tk.BooleanVar(value = True)
        def command(*args, **kwargs):
            self._highlight.toggle()
            self.canvas.draw_idle()
            
        self._highlight_button = mplgui.widgets.switchbutton.SwitchButton(
            self,
            text = 'H',
            variable = self._highlight_on,
            command = command,
            width = 2,
        )
        highlight_tooltip = mplgui.widgets.tooltip.ToolTip(
            self._highlight_button,
            text = 'Unhighlight',
        )
        def hglt(*args, **kwargs):
            if self._highlight_on.get():
                highlight_tooltip.text = 'Unhighlight'
            else: highlight_tooltip.text = 'Highlight'
        self._highlight_on.trace('w', hglt)
        
        self.pack()

    
    def _create_bindings(self, *args, **kwargs):
        self.canvas.mpl_connect('axes_enter_event', self._on_axes_enter)
        self.canvas.mpl_connect('axes_leave_event', self._on_axes_leave)
        self._expand_button.bind('<<Expand>>', self._on_expand, '+')
        self._expand_button.bind('<<Collapse>>', self._on_collapse, '+')
        
    def _on_import_pressed(self, *args, **kwargs):
        ImportWindow(self.axes, self.winfo_toplevel())
        self.hide()
    
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
    
    def _on_expand(self, *args, **kwargs):
        self._expand_tooltip.text = 'Collapse'
        self.pack()
    
    def _on_collapse(self, *args, **kwargs):
        for spacer in self._spacers: spacer.destroy()
        self._spacers = []
        for button in self._buttons.values(): button.pack_forget()
        self._highlight_button.pack_forget()
        self._expand_button.pack(side = 'right', padx = 0)
        self._expand_tooltip.text = 'Expand'
    
    def _on_axes_enter(self, event):
        self.show(event.inaxes)

    def _on_axes_leave(self, event):
        self.hide()

    def _Spacer(self):
        return tk.Frame(master=self, height='18p', relief=tk.RIDGE, bg='DarkGray')

    def pack(self, *args, **kwargs):
        for spacer in self._spacers: spacer.destroy()
        self._spacers = []
        
        self._expand_button.pack(side = 'right', padx = ('6p',0))
        self._highlight_button.pack(side = 'right')
        self._spacers += [self._Spacer()]
        self._spacers[-1].pack(side = 'right', padx='3p')
        for button in self._buttons.values():
            button.pack(side = 'left')
        
    def hide(self, *args, **kwargs):
        if self.winfo_ismapped():
            self.place_forget()
            
            need_draw = self._highlight.get_visible()
            self._highlight.set_visible(False)
            if need_draw: self.canvas.draw_idle()
        
        self.axes = None

    def show(self, axes):
        if hasattr(axes, '_colorbar'): return
        
        pos = axes.get_position()
        self.place(
            anchor = 'ne',
            relx = pos.x1,
            rely = 1. - pos.y1,
        )

        if self._highlight.axes != axes:
            self._highlight.set_axes(axes)
        need_draw = self._highlight.get_visible() != self._highlight_on.get()
        self._highlight.set_visible(self._highlight_on.get())
        if need_draw: self.canvas.draw_idle()
        self.axes = axes

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
