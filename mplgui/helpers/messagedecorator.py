import functools
import matplotlib.pyplot as plt

def message(function = None, level = None):
    assert callable(function) or function is None
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # If there isn't a plot open, don't set a message
            plot_open = plt._pylab_helpers.Gcf.get_active() is not None
            if plot_open: messenger = plt.gcf().canvas.message
            result = None
            for result in func(*args, **kwargs):
                if isinstance(result, str):
                    if result == 'break': return
                    if plot_open: messenger.set(result, level = level)
            return result
        return _wrapper
    return _decorator(function) if callable(function) else _decorator

