import tkinter as tk
import collections

class MenuBar(tk.Menu, object):
    mapping = collections.OrderedDict({
        'File' : {
            'Open project' : 'self.show_open',
            'Save project' : 'self.save',
            'Save project as...' : 'self.show_save_as',
            'Separator 0' : None,
            'Close' : quit,
        },
        'Edit' : {
            'Undo' : 'self.fig.canvas.undo',
            'Redo' : 'self.fig.canvas.redo',
            'Separator 0' : None,
            'Set figure name' : 'self.set_figure_name',
        },
        'About' : 'self.show_about',
    })
    
    def __init__(self, *args, fig = None, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)
        self.fig = fig
        self.master.winfo_toplevel()['menu'] = self
        self._add_commands()
        self._bind_functions()

        self.savepath = None

        

    def _bind_functions(self, *args, **kwargs):
        self.fig.canvas._state_index.trace_add(
            'write', self.update_undo_and_redo,
        )
        self.master.bind('<Map>', self._on_map, '+')

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
    
    def show_about(self, *args, **kwargs):
        import mplgui
        tk.messagebox.showinfo(
            master = self.master,
            title = 'About',
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
                title = 'Open project',
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
                title = 'Save project as...',
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
                'Set figure name',
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
            'Undo' : 'normal',
            'Redo' : 'normal',
        }
        if nstates == 0:
            for key, val in states.items(): states[key] = 'disabled'
        else:
            if index == 0: states['Undo'] = 'disabled'
            if index + 1 >= nstates: states['Redo'] = 'disabled'
        
        for name, state in states.items():
            self.menus['Edit'].entryconfig(name, state = state)
        
