import tkinter as tk
import matplotlib.backends.backend_tkagg
import matplotlib.backends._backend_tk
import matplotlib.figure
import mplgui.lib.message
import mplgui.lib.artistmanager
from mplgui.helpers.messagedecorator import message
import matplotlib.pyplot as plt
import os
import pickle

def showerror():
    import mplgui.lib.message
    mplgui.lib.message.ErrorMessage()

def askquit(
        title = 'Quit?',
        text = 'Are you sure you want to quit?',
        **kwargs
):
    from tkinter import messagebox
    return messagebox.askyesno(title, text, **kwargs)

class FigureManager(matplotlib.backends._backend_tk.FigureManagerTk, object):
    def __init__(self, *args, **kwargs):
        super(FigureManager, self).__init__(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        if self.window.winfo_ismapped():
            if self.canvas.get_state() != self.canvas._base_state:
                if not askquit(detail = 'You have unsaved changes.'):
                    return
        return super(FigureManager, self).destroy(*args, **kwargs)
        

class FigureCanvas(matplotlib.backends.backend_tkagg.FigureCanvasTkAgg, object):
    manager_class = FigureManager
    
    def __init__(self, *args, **kwargs):
        import mplgui.lib.menubar

        self._toolbar = None
        self._manager = None
        self._artist_manager = None

        super(FigureCanvas, self).__init__(*args, **kwargs)
        
        self._state_index = tk.IntVar(value = 0)

        mplgui.lib.menubar.MenuBar(
            self.get_tk_widget(),
            fig = self.figure,
        )

        self._base_state = None
        self._states = []
        self._recording_changes = True
        self._undo_history = mplgui.preferences.undo_history
        
        self.message = mplgui.lib.message.Message(self.get_tk_widget().winfo_toplevel())
    
    @property
    def toolbar(self): return self._toolbar
    @toolbar.setter
    def toolbar(self, value):
        # Do nothing if the toolbar hasn't changed
        if value is self._toolbar: return
        self._toolbar = value
        self._on_toolbar_changed()
    
    def _on_toolbar_changed(self, *args, **kwargs):
        # Remove the "save" button in the toolbar. The functionality is now
        # represented in the File -> Export menu. Refer to
        # https://github.com/matplotlib/matplotlib/blob/55cf8c70214be559268719f0f1049f98c6c6731a/lib/matplotlib/backends/_backend_tk.py#L597
        if self.toolbar is None: return
        if not hasattr(self.toolbar, '_buttons'): return
        if 'Save' not in self.toolbar._buttons.keys(): return
        
        # Figure out what kind of object the spacers are
        spacer = self.toolbar._Spacer()
        spacer_type = type(spacer)
        spacer.destroy()
            
        # The pack slaves are ordered from left-to-right. Find the 'Save' button
        # and delete it. If there is a spacer to its left, delete that too.
        previous_slave = None
        for i, slave in enumerate(self.toolbar.pack_slaves()):
            if slave is self.toolbar._buttons['Save']:
                if isinstance(previous_slave, spacer_type):
                    previous_slave.pack_forget()
                slave.pack_forget()
                break
            previous_slave = slave
    
    def record_change(self, *args, **kwargs):
        if not self._recording_changes: return

        # Discard states that become obfuscated after an undo
        current_index = self._state_index.get()
        self._states = self._states[:current_index + 1]
        
        for _ in range(max(self._undo_history, 1), len(self._states) + 1):
            del self._states[0]
        
        self._states += [State(self)]
        if current_index != len(self._states) - 1:
            self._state_index.set(len(self._states) - 1)

    @message(level = -1)
    def redo(self, *args, **kwargs):
        current = self._state_index.get()
        new = min(max(current + 1, 0), len(self._states) - 1)
        if current == new: return # The message will not be sent
        yield 'Redo' # The message
        self._recording_changes = False
        self._states[new].load(fig = self.figure)
        self._recording_changes = True
        self._state_index.set(new)

    @message(level = -1)
    def undo(self, *args, **kwargs):
        current = self._state_index.get()
        new = min(max(current - 1, 0), len(self._states) - 1)
        if current == new: return # The message will not be sent
        yield 'Undo' # Show the message
        self._recording_changes = False
        self._states[new].load(fig = self.figure)
        self._recording_changes = True
        self._state_index.set(new)
        

    # Getters ----------------------------------

    def get_artist_manager(self):
        if self._artist_manager is not None: return self._artist_manager
        self._artist_manager = mplgui.lib.artistmanager.ArtistManager(self)
        return self._artist_manager
    
    def get_filename(self):
        title = self.get_window_title()
        if ' (' in title:
            t = title.split(' (')[-1]
            if '.mpl' in t: return t[:-1]
    
    def get_name(self):
        title = self.get_window_title()
        current = self.get_filename()
        if current: return title.split(' (%s)' % current)[0]
        return title

    def get_state(self):
        """
        Return the most recent :class:`~.State` object, which is a snapshot of 
        the current figure and its meta data.
        
        Returns
        -------
        state : :class:`~.State`
            The current figure state.
        """
        if not self._states:
            self.record_change()
            self._base_state = self._states[0]
        return self._states[self._state_index.get()]

    def get_window_title(self):
        return self.get_tk_widget().winfo_toplevel().title()
    
    # ------------------------------------------


    
    
    # Setters ----------------------------------
    
    def set_filename(self, filename):
        filename = os.path.basename(filename)
        name = self.get_name()
        if name is None: title = '(%s)' % filename
        else: title = name + ' (%s)' % filename
        self.set_window_title(title)
        self.record_change()
    
    def set_name(self, name):
        filename = self.get_filename()
        if filename is None: title = name
        else: title = name + ' (%s)' % filename
        self.set_window_title(title)
        self.figure.set_label(name)
        self.record_change()

    def set_undo_history(self, value : int):
        for _ in range(max(value, 1), len(self._states)):
            del self._states[0]
        self._undo_history = max(value, 0)
    
    def set_window_title(self, title):
        self.get_tk_widget().winfo_toplevel().title(title)
    
    # ------------------------------------------
    
    
    

        
    

    
        


class State(object):
    """
    A State is a snapshot of the canvas which can be used to completely restore
    the canvas.
    """

    # These keys are ignored when comparing two States in __eq__
    ignore = [
        'filename',
    ]
    
    def __init__(self, canvas_or_bytes):
        if isinstance(canvas_or_bytes, FigureCanvas):
            self._data = {
                'name' : canvas_or_bytes.get_name(),
                'filename' : canvas_or_bytes.get_filename(),
                'figure' : canvas_or_bytes.figure,
            }
        elif isinstance(canvas_or_bytes, bytes):
            # Check if a figure has been opened yet at all
            previous_canvas = None
            if plt._pylab_helpers.Gcf.get_active() is not None:
                # A figure is currently open
                previous_canvas = plt.gcf().canvas # Get the current open canvas
            
            self._data = pickle.loads(canvas_or_bytes)
            # When the window has not been shown yet,
            # The act of unpickling the data automatically creates a new window
            # thanks to __setstate__ in the Figure class. We can't make
            # matplotlib use a different default Figure class, so we need to
            # correct its behavior here.
            if previous_canvas:
                previous_figure = self.figure
                self.load(fig = previous_canvas.figure)
        else:
            raise TypeError("Argument 'canvas_or_bytes' must be of type mplgui.lib.backend.FigureCanvas or bytes, not '%s'" % type(canvas_or_bytes).__name__)

    def __sub__(self, other):
        """
        Returns a list of keys that are either mising or different between the
        two State objects.
        """
        if not isinstance(other, State):
            raise NotImplementedError("Subtraction is only allowed between two State objects")
        
        diff = []
        for key, val in self._data.items():
            if key in diff: continue
            if (key in other._data.keys() and
                (val == other._data[key] or val is other._data[key])):
                continue
            diff += [key]
        for key, val in other._data.items():
            if key in diff: continue
            if (key in self._data.keys() and
                (val == self._data[key] or val is self._data[key])):
                continue
            diff += [key]
        return diff

    def __eq__(self, other):
        if not isinstance(other, State): return False
        diff = self - other
        for key in State.ignore:
            if key in diff: diff.remove(key)
        return len(diff) == 0

    @property
    def figure(self): return self._data['figure']


    @message
    def load(
            self,
            fig : matplotlib.figure.Figure | type(None) = None,
    ):
        """
        Load this State to the given figure.
        
        Other Parameters
        ----------------
        fig : :class:`matplotlib.figure.Figure`, None, default = None
            The figure to load the state into. If `None`, the figure is obtained
            using :meth:`matplotlib.pyplot.gcf`.
        """
        if fig is None: fig = plt.gcf()

        yield 'Loading state...'

        current_state = fig.canvas.get_state()
        differences = self - current_state
        if not differences: return
        
        if 'figure' in differences:
            fig.clear()
            self.figure.set_canvas(fig.canvas)
            fig.canvas.figure = self.figure
            # Update the contents of the figure
            self.figure.canvas.draw()
            self.figure.canvas.blit()
        
        fig.canvas.set_name(self._data['name'])
        fig.canvas.set_filename(self._data['filename'])
        
        fig._base_state = self
        yield 'Loaded state'

    @message
    def save(self, path : str):
        """
        Save the state to disk. This sets the ``'filename'`` key in the data.
        
        Parameters
        ----------
        path : str
            The path to the state on the file system. If it does not end with
            extension `'.mpl'`, then `'.mpl'` is added to the end of the path.
        
        See Also
        --------
        :func:`~.load`
        """
        self.figure.canvas.set_filename(path)
        self._data['filename'] = self.figure.canvas.get_filename()
        yield 'Saving...'
        with open(path, 'wb') as f:
            pickle.dump(self._data, f)
        yield 'Saved'
    
