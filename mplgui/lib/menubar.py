import tkinter as tk
import collections
import pathlib
from mplgui.helpers.messagedecorator import message
import os

# Labels for robust referencing
FILE = 'File'
EDIT = 'Edit'
ABOUT = 'About'

OPEN = 'Open project...'
SAVE = 'Save project'
SAVE_AS = 'Save project as...'
EXPORT = 'Export image'
EXPORT_AS = 'Export image as...'
CLOSE = 'Close'
UNDO = 'Undo'
REDO = 'Redo'
SET_FIGURE_NAME = 'Set figure name'

class MenuBar(tk.Menu, object):
    mapping = collections.OrderedDict({
        FILE : {
            OPEN : 'self.show_open',
            SAVE : 'self.save',
            SAVE_AS : 'self.show_save_as',
            'Separator 0' : None,
            EXPORT : 'self.export',
            EXPORT_AS : 'self.export_as',
            'Separator 1' : None,
            CLOSE : 'self.close',
        },
        EDIT : {
            UNDO : 'self.fig.canvas.undo',
            REDO : 'self.fig.canvas.redo',
            'Separator 0' : None,
            SET_FIGURE_NAME : 'self.set_figure_name',
        },
        ABOUT : 'self.show_about',
    })
    
    def __init__(self, *args, fig = None, **kwargs):
        self.fig = fig
        super(MenuBar, self).__init__(*args, **kwargs)
        self.master.winfo_toplevel()['menu'] = self
        self._add_commands()
        self._bind_functions()

        self.savepath = None
        self._export_filename = None
        self._export_extension = None

    def _bind_functions(self, *args, **kwargs):
        self.fig.canvas._state_index.trace_add(
            'write', self.update_undo_and_redo,
        )

    def _bind_hotkeys(self, *args, **kwargs):
        import mplgui
        
        # Bind the hotkeys
        hotkeys = mplgui.preferences.hotkeys.get(self.__class__.__name__, {})
        for main, obj in hotkeys.items():
            if main not in MenuBar.mapping.keys(): continue
            if main not in self.menus.keys(): continue

            if not isinstance(obj, dict):
                self.master.bind(obj, self._get_command(MenuBar.mapping[main]))
                continue
            
            for name, keystroke in obj.items():
                if name not in MenuBar.mapping[main].keys(): continue
                self.master.bind(keystroke, self._get_command(MenuBar.mapping[main][name]), '+')
                self.menus[main].entryconfig(
                    name,
                    accelerator = self._get_hotkey_accelerator(keystroke),
                )
    
    def _get_command(self, obj, *args, **kwargs):
        if not isinstance(obj, str): return obj
        _locals = locals()
        _locals['self'] = self
        return eval(obj, _locals, globals())

    def _add_commands(self, *args, **kwargs):
        import mplgui
        
        self.menus = {}
        for main, obj in MenuBar.mapping.items():
            if not isinstance(obj, dict):
                self.menus[main] = self.add_command(
                    label = main, command = self._get_command(obj),
                )
                continue
            
            self.menus[main] = tk.Menu(self, tearoff = False)
            for key, command in obj.items():
                if command is None:
                    self.menus[main].add_separator()
                    continue
                self.menus[main].add_command(
                    label = key,
                    command = self._get_command(command),
                )
            
            self.add_cascade(
                label = main,
                menu = self.menus[main],
            )

    def _get_hotkey_accelerator(self, string):
        if not string: return string
        if string.startswith('<') and len(string) > 1: string = string[1:]
        if string.endswith('>') and len(string) > 1: string = string[:-1]
        return string.replace(
            'Control-','Ctrl+'
        ).replace(
            'Shift-', 'Shift+',
        ).replace(
            'Alt-', 'Alt+',
        )

    def _on_map(self, *args, **kwargs):
        self._bind_hotkeys()
        self.update_undo_and_redo()

    def close(self, *args, **kwargs):
        import matplotlib.pyplot as plt
        plt.close(self.fig)
    
    def show_about(self, *args, **kwargs):
        import mplgui
        tk.messagebox.showinfo(
            master = self.master,
            title = ABOUT,
            message = 'MPLGUI v' + mplgui.__version__,
            detail = "Created by {author:s}\n{github:s}".format(
                author = mplgui.__author__,
                github = mplgui.__github__,
            ),
        )

    def show_open(self, *args, **kwargs):
        import mplgui.lib.backend
        try:
            from tkinter import filedialog
            import mplgui
            
            fname = filedialog.askopenfilename(
                master = self.master,
                title = OPEN,
                filetypes = [('MPLGUI', '.mpl')],
                defaultextension = '.mpl',
            )
            if fname in ['', ()]: return

            mplgui.open(fname, fig = self.fig)
            self.savepath = fname
        except:
            mplgui.lib.backend.showerror()

    def show_save_as(self, *args, **kwargs):
        import mplgui.lib.backend
        try:
            from tkinter import filedialog
            import mplgui
        
            self.savepath = filedialog.asksaveasfilename(
                master = self.master,
                title = SAVE_AS,
                filetypes = [('MPLGUI', '.mpl')],
                defaultextension = '.mpl',
                initialfile = self.fig.canvas.get_name(),
            )
            if self.savepath in ['', ()]:
                self.savepath = None
                return

            mplgui.save(self.savepath, fig = self.fig)
        except:
            mplgui.lib.backend.showerror()

    def save(self, *args, **kwargs):
        import mplgui.lib.backend
        try:
            if self.savepath is None: self.show_save_as()
            else:
                mplgui.save(self.savepath, fig = self.fig)
        except:
            mplgui.lib.backend.showerror()

    def set_figure_name(self, *args, **kwargs):
        import mplgui.lib.backend
        try:
            from tkinter import simpledialog
            
            old_name = self.fig.canvas.get_name()
            if old_name is None: old_name = ''
            new_name = simpledialog.askstring(
                SET_FIGURE_NAME,
                'Enter the new figure name',
                initialvalue = old_name,
                parent = self.master,
            )
            if new_name is None or new_name == old_name: return

            self.fig.canvas.set_name(new_name)
        except:
            mplgui.lib.backend.showerror()
    
    def update_undo_and_redo(self, *args, **kwargs):
        index = self.fig.canvas._state_index.get()
        nstates = len(self.fig.canvas._states)
        states = {
            UNDO : 'normal',
            REDO : 'normal',
        }
        if nstates == 0:
            for key, val in states.items(): states[key] = 'disabled'
        else:
            if index == 0: states[UNDO] = 'disabled'
            if index + 1 >= nstates: states[REDO] = 'disabled'
        
        for name, state in states.items():
            self.menus[EDIT].entryconfig(name, state = state)
    
    @message(level = 0)
    def export(self, *args, **kwargs):
        if self._export_filename is None:
            self.export_as(*args, **kwargs)
            return
        yield "Exporting image..."
        self.fig.savefig(self._export_filename, format = self._export_extension)
        yield "Exported image"
    
    def export_as(self, *args, **kwargs):
        import mplgui.lib.backend
        try:
            from tkinter import filedialog
            import mplgui
            
            # Copying the code from https://github.com/matplotlib/matplotlib/blob/55cf8c70214be559268719f0f1049f98c6c6731a/lib/matplotlib/backends/_backend_tk.py#L837
            filetypes = self.fig.canvas.get_supported_filetypes_grouped()
            tk_filetypes = [
                (name, " ".join(f"*.{ext}" for ext in exts))
                for name, exts in sorted(filetypes.items())
            ]
            
            default_extension = self.fig.canvas.get_default_filetype()
            default_filetype = self.fig.canvas.get_supported_filetypes()[default_extension]
            filetype_variable = tk.StringVar(
                self.fig.canvas.get_tk_widget(), default_filetype,
            )
            
            defaultextension = ''
            
            initialfile = pathlib.Path(self.fig.canvas.get_default_filename()).stem
            
            self._export_filename = filedialog.asksaveasfilename(
                master = self.master,
                title = EXPORT_AS,
                filetypes = tk_filetypes,
                defaultextension = defaultextension,
                initialfile = self.fig.canvas.get_name(),
                typevariable = filetype_variable,
            )
            if self._export_filename in ['', ()]:
                self._export_filename = None
                self._export_extension = None
                return

            self._export_extension = None
            if pathlib.Path(self._export_filename).suffix[1:] == "":
                self._export_extension = filetypes[filetype_variable.get()][0]
            
            self.menus[FILE].entryconfig(
                list(MenuBar.mapping[FILE].keys()).index(EXPORT),
                label = '{:s} ({:s})'.format(EXPORT, os.path.basename(self._export_filename)),
            )
            
            self.export()
        except:
            mplgui.lib.backend.showerror()
