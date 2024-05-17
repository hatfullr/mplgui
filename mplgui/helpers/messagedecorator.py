import functools
import matplotlib.pyplot as plt

def message(function = None, level = None):
    assert callable(function) or function is None
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            messenger = plt.gcf().canvas.message
            result = None
            for result in func(*args, **kwargs):
                if isinstance(result, str):
                    if result == 'break': return
                    messenger.set(result, level = level)
            return result
        return _wrapper
    return _decorator(function) if callable(function) else _decorator

