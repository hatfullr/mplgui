import tkinter as tk
import matplotlib.backends.backend_tkagg
import matplotlib.backends._backend_tk
import matplotlib.figure
import mplgui.lib.pickler
import mplgui.lib.message
from mplgui.helpers.messagedecorator import message
import os

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



class FigureCanvas(matplotlib.backends.backend_tkagg.FigureCanvasTkAgg, object):
    def __init__(self, *args, **kwargs):
        import mplgui.lib.menubar

        self._toolbar = None
        self._manager = None
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
    def manager(self): return self._manager
    @manager.setter
    def manager(self, value):
        # Do nothing if the manager hasn't changed
        if value is self._manager: return
        self._manager = value
        self._on_manager_changed()

    @property
    def toolbar(self): return self._toolbar
    @toolbar.setter
    def toolbar(self, value):
        # Do nothing if the toolbar hasn't changed
        if value is self._toolbar: return
        self._toolbar = value
        self._on_toolbar_changed()

    def _on_manager_changed(self, *args, **kwargs):
        if self.manager is None: return
        # Override the "window.destroy" functionality to ask the user if they
        # want to quit when they have unsaved changes.
        
        # This is after Matplotlib has set their own protocol, so we can
        # interrupt that here.
        # https://github.com/matplotlib/matplotlib/blob/92a4b8d3c43bc9543d6f864e92e46367d11485fc/lib/matplotlib/backends/_backend_tk.py#L545
        def destroy(*args, **kwargs):
            from tkinter import messagebox
            # Only ask to close if the widget is currently mapped
            if self.manager.window.winfo_ismapped():
                if self.get_state() != self._base_state:
                    if not askquit(detail = 'You have unsaved changes.'):
                        return
            orig_protocol(*args, **kwargs)
            self.manager.window.quit() # This seems to be required
        
        orig_protocol = self.manager.destroy
        self.manager.destroy = destroy
    
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
            self._data = mplgui.lib.pickler.unpickle(canvas_or_bytes)
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
        import matplotlib.pyplot as plt
        if fig is None: fig = plt.gcf()

        yield 'Loading state...'

        current_state = fig.canvas.get_state()
        differences = self - current_state
        if not differences: return
        
        # This has to go first
        if 'figure' in differences:
            fig.canvas.get_tk_widget().destroy()
            fig.canvas = FigureCanvas(self._data['figure'])
            fig.canvas.get_tk_widget().pack()
        
        for key in differences:
            if key == 'figure': continue
            
            if key == 'name':
                fig.canvas.set_name(self._data['name'])
            elif key == 'filename':
                fig.canvas.set_filename(self._data['filename'])
            else:
                raise NotImplementedError("Unimplemented key '%s'" % key)

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
        self._data['figure'].canvas.set_filename(path)
        self._data['filename'] = self._data['figure'].canvas.get_filename()
        yield 'Saving...'
        data = mplgui.lib.pickler.pickle(self._data)
        with open(path, 'wb') as f:
            f.write(data)
        yield 'Saved'
    
