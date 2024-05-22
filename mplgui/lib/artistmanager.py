import tkinter as tk
from tkinter import ttk
import mplgui.helpers.nesteddict
import mplgui.widgets.scrolltreeview
import mplgui.widgets.artistviewer

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
        self.update_hierarchy()

    def _create_widgets(self, *args, **kwargs):
        self.hierarchy = mplgui.widgets.scrolltreeview.ScrollTreeview(
            self, show = 'tree',
            selectmode = 'browse',
            horizontal_scrollbar = False,
            width = 400,
        )
        self.artist_viewer = mplgui.widgets.artistviewer.ArtistViewer(
            self, width = 30,
        )
        
        self.hierarchy.pack(side='left', fill = 'both', expand = True)
        self.artist_viewer.pack(side = 'left', padx = (5,0), fill = 'y', expand = False)

        self.minsize(width = 500 + 300, height = 400)


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
            name = obj.__class__.__name__
            if isinstance(keypath, str): keypath = tuple([keypath])
            keypath = tuple(list(keypath) + [name])
            if len(keypath) == 1: keypath = keypath[0]
            yield keypath, obj
            
            if hasattr(obj, 'get_children'):
                for child in obj.get_children():
                    yield from get(child, keypath = keypath)

        hierarchy = mplgui.helpers.nesteddict.NestedDict()
        for child in self.canvas.figure.get_children():
            hierarchy[child.__class__.__name__] = {'__object__' : child}
            for branch, obj in get(child):
                if branch not in hierarchy:
                    hierarchy[branch] = {'__object__' : obj}
        return hierarchy
    
    def update_hierarchy(self, *args, **kwargs):
        # Clear the hierarchy first
        self.hierarchy.delete(*self.hierarchy.get_children())

        self._artists = self._get_hierarchy()
        
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
                            parent, 'end', text = key,
                        ),
                    }

    def hide(self, *args, **kwargs):
        self.withdraw()
    
    def show(self, *args, **kwargs):
        self.deiconify()
