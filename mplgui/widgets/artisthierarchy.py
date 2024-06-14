import mplgui.widgets.scrolltreeview
import tkinter as tk
from tkinter import ttk
import pickle
import matplotlib.artist

ATTR_BLACKLIST = [
    'figure',
    'picker',
]

def get_artist_information(artist):
    inspector = matplotlib.artist.ArtistInspector(artist)
    info = {}
    for attr in inspector.get_setters():
        if not hasattr(artist, 'get_' + attr): continue
        if attr in ATTR_BLACKLIST: continue
        try: info[attr] = getattr(artist, 'get_' + attr)()
        except: continue
    return info

def set_artist_information(artist, info):
    inspector = matplotlib.artist.ArtistInspector(artist)
    for attr in inspector.get_setters():
        if attr not in info: continue
        if not hasattr(artist, 'set_' + attr): continue
        if attr in ATTR_BLACKLIST: continue
        getattr(artist, 'set_' + attr)(info[attr])

class ArtistHierarchy(mplgui.widgets.scrolltreeview.ScrollTreeview, object):    
    def __init__(
            self,
            manager,
            *args,
            show : str = 'tree',
            selectmode : str = 'browse',
            horizontal_scrollbar : bool = False,
            width : int = 400,
            **kwargs
    ):
        self.manager = manager
        super(ArtistHierarchy, self).__init__(
            *args,
            show = show,
            selectmode = selectmode,
            horizontal_scrollbar = horizontal_scrollbar,
            width = width,
            **kwargs
        )
        self._create_bindings()

        self._previous_selection = None
        self._artists = {}
        self._original_artists = {}
        
        self.populate()

    def _create_bindings(self, *args, **kwargs):
        def on_treeview_select(*args, **kwargs):
            current_selection = self.focus()
            if current_selection == self._previous_selection: return
            self.manager.artist_viewer.set_artist(self._artists[current_selection])
            self._previous_selection = current_selection

        def save_original_artist(*args, **kwargs):
            current_selection = self.focus()
            if current_selection in self._original_artists: return
            self._original_artists[current_selection] = pickle.dumps(get_artist_information(self._artists[current_selection]))
            
        self.bind('<<TreeviewSelect>>', on_treeview_select)
        self.manager.artist_viewer.add_listener('before set', save_original_artist)

    def clear(self, *args, **kwargs):
        self.delete(*self.get_children())

    def refresh(self, *args, **kwargs):
        self.clear()
        self.populate()

    def populate(self, *args, **kwargs):
        for child in self.manager.canvas.figure.get_children():
            self.add_artist(child)
    
    def add_artist(self, artist, parent = ''):
        text = artist.__class__.__name__
        text_modifier = ''
        text_mod_format = ' ({:d})'
        
        existing = [self.item(child, option='text') for child in self.get_children(parent)]
        
        i = 1
        while text + text_modifier in existing:
            text_modifier = text_mod_format.format(i)
            i += 1
        text += text_modifier
        
        obj = self.insert(parent, 'end', text = text)
        self._artists[obj] = artist
        if hasattr(artist, 'get_children'):
            for child in artist.get_children():
                self.add_artist(child, parent = obj)

    def reset_artists(self, *args, **kwargs):
        for key, val in self._original_artists.items():
            set_artist_information(self._artists[key], pickle.loads(val))
        self.manager.canvas.draw()
        self.manager.canvas.blit()

