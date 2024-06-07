import tkinter as tk
from tkinter import ttk
import mplgui.helpers.nesteddict
import mplgui.widgets.scrolltreeview
import mplgui.widgets.artistviewer
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
        self._original_artists = None
        self._current_selection = None

        self._create_widgets()
        self._create_bindings()
        self.update_hierarchy()

    def _create_widgets(self, *args, **kwargs):
        main_frame = tk.Frame(self, borderwidth = 1, relief = 'sunken')
        self.hierarchy = mplgui.widgets.scrolltreeview.ScrollTreeview(
            main_frame, show = 'tree',
            selectmode = 'browse',
            horizontal_scrollbar = False,
            width = 400,
        )
        self.artist_viewer = mplgui.widgets.artistviewer.ArtistViewer(
            main_frame, width = 30,
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

    def _create_bindings(self, *args, **kwargs):
        self.hierarchy.bind('<<TreeviewSelect>>', self._on_treeview_select, '+')
    
    def _on_treeview_select(self, *args, **kwargs):
        current_selection = self.hierarchy.focus()
        if current_selection == self._current_selection: return
        self._current_selection = current_selection

        for branch, leaf in self._hierarchy.flowers():
            if leaf == current_selection:
                if not isinstance(branch, str):
                    # We have to massage this for some reason.
                    branch = list(branch)
                    for i, b in enumerate(branch):
                        if isinstance(b, tuple) and len(b) == 1:
                            branch[i] = b[0]
                    branch = tuple(branch)
                self.artist_viewer.set_artist(self._artists[branch])
                break

    def _get_hierarchy(self, *args, **kwargs):
        def get(obj, keypath = ()):
            name = repr(obj)
            if isinstance(keypath, str): keypath = tuple([keypath])
            keypath = tuple(list(keypath) + [name])
            if len(keypath) == 1: keypath = keypath[0]
            yield keypath, obj
            
            if hasattr(obj, 'get_children'):
                for child in obj.get_children():
                    yield from get(child, keypath = keypath)

        hierarchy = mplgui.helpers.nesteddict.NestedDict()
        for child in self.canvas.figure.get_children():
            for branch, obj in get(child):
                hierarchy[branch] = {'__object__' : obj}
        
        return hierarchy
    
    def update_hierarchy(self, *args, **kwargs):
        # Clear the hierarchy first
        self.hierarchy.delete(*self.hierarchy.get_children())

        self._artists = self._get_hierarchy()
        if self._original_artists is None:
            self._original_artists = pickle.dumps(self._artists)
        
        # Now populate with new values
        self._hierarchy = mplgui.helpers.nesteddict.NestedDict()
        for branch, leaf in self._artists.flowers():
            _branch = []
            parent = ''
            for key in branch[:-1]:
                _branch += [key]

                if tuple(_branch) in self._hierarchy:
                    parent = self._hierarchy[tuple(_branch)]['__object__']
                else:
                    # Create the parent
                    self._hierarchy[tuple(_branch)] = {
                        '__object__' : self.hierarchy.insert(
                            parent, 'end', text = leaf.__class__.__name__,
                        ),
                    }

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
        
        orig_artists = pickle.loads(self._original_artists)
        
        for branch, leaf in orig_artists.flowers():
            if branch not in self._artists: continue
            # Some values don't change, but that's because of the
            # update_from method in Matplotlib, not our fault.
            self._artists[branch].update_from(leaf)
        
        self.artist_viewer._update_widgets()
        
        self.canvas.draw()
        self.canvas.blit()

