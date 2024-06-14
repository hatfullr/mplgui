import matplotlib.axes

class Reader(object):
    """ Reads data from a given file. """
    def read(self, ax : matplotlib.axes.Axes, filename : str):
        """ Override this in subclasses. Returns a Matplotlib artist. """
        raise NotImplementedError


def get_readers():
    import mplgui
    import os
    import importlib.metadata as metadata
    import importlib.util as util
    import inspect
    
    default = os.path.join(mplgui.DEFAULT_DIRECTORY, 'readers')
    user = os.path.join(mplgui.USER_DIRECTORY, 'readers')

    defaults = []
    users = []
    if os.path.exists(default):
        for _file in sorted(os.listdir(default)):
            if not _file.endswith('.py'): continue
            path = os.path.join(default, _file)
            spec = util.spec_from_file_location('default', path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _class in inspect.getmembers(module, inspect.isclass):
                if issubclass(_class, Reader):
                    defaults += [_class]

    if os.path.exists(user):
        for _file in sorted(os.listdir(user)):
            if not _file.endswith('.py'): continue
            path = os.path.join(user, _file)
            spec = util.spec_from_file_location('user', path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _class in inspect.getmembers(module, inspect.isclass):
                if issubclass(_class, Reader):
                    users += [_class]
    
    return defaults, users
