import tkinter as tk
from tkinter import ttk
import mplgui.helpers.nesteddict
import mplgui.widgets.artistviewer
import mplgui.widgets.artisthierarchy
from tkinter import messagebox
import pickle

class ArtistManager(tk.Toplevel, object):
    def __init__(self, canvas):
        self.canvas = canvas
        super(ArtistManager, self).__init__(
            self.canvas.get_tk_widget(),
            padx = 5,
            pady = 5,
        )
        self.protocol('WM_DELETE_WINDOW', self.hide)
        self.title('Artist Manager')

        self._hierarchy = None
        self._artists = None
        self._current_selection = None

        self._create_widgets()
    
    def _create_widgets(self, *args, **kwargs):
        main_frame = tk.Frame(self, borderwidth = 1, relief = 'sunken')
        self.artist_viewer = mplgui.widgets.artistviewer.ArtistViewer(
            main_frame, width = 30,
        )
        self.hierarchy = mplgui.widgets.artisthierarchy.ArtistHierarchy(
            self, main_frame,
        )
        def onset(*args, **kwargs):
            ret = self.artist_viewer._on_set_pressed(*args, **kwargs)
            if ret != 'break':
                self._reset_button.configure(state = 'normal')
            return ret
        self.artist_viewer._set_button.configure(command = onset)

        button_frame = tk.Frame(self)
        self._reset_button = ttk.Button(
            button_frame,
            text = 'Reset all',
            command = self.reset,
            state = 'disabled',
        )
        self._reset_button.pack(side = 'left', anchor = 'w')
        # spacer
        tk.Label(button_frame, text = '').pack(side = 'left', fill = 'x', expand = True)
        ttk.Button(
            button_frame,
            text = 'Close',
            command = self.withdraw,
        ).pack(side = 'left', anchor = 'e')
        
        self.hierarchy.pack(side='left', fill = 'both', expand = True)
        self.artist_viewer.pack(side = 'left', padx = (5,0), fill = 'y', expand = False)
        main_frame.pack(side = 'top', fill = 'both', expand = True)
        button_frame.pack(side = 'top', fill = 'x', pady=(5,0))

        self.minsize(width = 500 + 300, height = 400)

    def hide(self, *args, **kwargs):
        self.withdraw()
    
    def show(self, *args, **kwargs):
        self.deiconify()

    def reset(self, *args, **kwargs):
        # First ask
        if not messagebox.askyesno(
                'Reset all artists?',
                'Reset all artists?',
                detail = 'This action cannot be undone.',
                parent = self,
        ):
            return
        
        self._reset_button.configure(state = 'disabled')
        self.update()

        self.hierarchy.reset_artists()
        self.artist_viewer._update_widgets()
        
        self.canvas.draw()
        self.canvas.blit()
