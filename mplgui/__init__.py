import os
import importlib.metadata as metadata
import importlib.util as util
import matplotlib
from mplgui.helpers.apidecorator import api
import warnings
import traceback

__version__ = metadata.version('mplgui')
__author__ = 'Roger Hatfull'
__github__ = 'https://github.com/hatfullr/mplgui'

if __file__.endswith(os.path.join('mplgui', 'mplgui','__init__.py')):
    SOURCE_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
else:
    SOURCE_DIRECTORY = os.path.dirname(os.path.dirname(util.find_spec('mplgui').origin))

DATA_DIRECTORY = os.path.join(SOURCE_DIRECTORY, 'data')
USER_DIRECTORY = os.path.join(DATA_DIRECTORY, 'user')
DEFAULT_DIRECTORY = os.path.join(DATA_DIRECTORY, 'default')
DEFAULT_PREFERENCES = os.path.join(DEFAULT_DIRECTORY, 'preferences.py')
USER_PREFERENCES = os.path.join(USER_DIRECTORY, 'preferences.py')

# Load preferences
spec = util.spec_from_file_location('preferences', DEFAULT_PREFERENCES)
preferences = util.module_from_spec(spec)
spec.loader.exec_module(preferences)
del spec

if os.path.exists(USER_PREFERENCES):
    spec = util.spec_from_file_location('preferences', USER_PREFERENCES)
    user = util.module_from_spec(spec)
    spec.loader.exec_module(user)
    preferences.__dict__.update(user.__dict__)
    del spec, user

BACKEND_IMPORTED = False
try:
    matplotlib.use('module://mplgui.lib.backend')
    BACKEND_IMPORTED = True
except ImportError:
    traceback.format_exc()
    warnings.warn('mplgui was imported but failed to switch the Matplotlib backend. The GUI will not be visible and API functions will not be available.')


if BACKEND_IMPORTED:
    @api
    def open(
            path : str,
            fig : matplotlib.figure.Figure | type(None) = None,
    ):
        """
        Open the project from disk and fill the current figure with its 
        contents.
        All unsaved changes in the current project are discarded. Consider using
        :func:`~.save` first.

        If there is currently no created figure and ``fig = None``, then a new 
        one will be created during the call to :meth:`matplotlib.pyplot.gcf`.

        Parameters
        ----------
        path : str
            The path to the project on the file system.

        Other Parameters
        ----------------
        fig : :class:`matplotlib.figure.Figure`, None, default = None
            The figure to which the opened project will be loaded. If `None`, 
            the current figure is obtained using :meth:`matplotlib.pyplot.gcf`.

        Returns
        -------
        state : :class:`~.lib.backend.State`
            A State object, which contains the meta data and the figure. To 
            access the figure, use :meth:`~.lib.backend.State.get` to obtain the
            unpickled data, then use key ``state['figure']``.

        See Also
        --------
        :func:`~.save`
        """
        import builtins
        import mplgui.lib.backend
        with builtins.open(path, 'rb') as f:
            content = f.read()
        state = mplgui.lib.backend.State(content)
        state.load(fig = fig)
        return state

    @api
    def save(
            path : str,
            fig : matplotlib.figure.Figure | type(None) = None,
    ):
        """
        Save the project to disk.

        Parameters
        ----------
        path : str
            The path to the project on the file system. If it does not end with
            extension `'.mpl'`, then `'.mpl'` is added to the end of the path.

        Other Parameters
        ----------------
        fig : :class:`matplotlib.figure.Figure`, None, default = None
            The figure to save. If `None`, the current figure is obtained using
            :meth:`matplotlib.pyplot.gcf`.

        See Also
        --------
        :func:`~.open`
        """
        import matplotlib.pyplot as plt

        if fig is None: fig = plt.gcf()
        if not path.endswith('.mpl'): path += '.mpl'

        state = fig.canvas.get_state()
        state.save(path)
        fig.canvas._base_state = state

    @api
    def undo_history(
            value : int | type(None) = None,
            fig : matplotlib.figure.Figure | type(None) = None,
    ):
        """
        Set the length of the undo history on the given figure.

        Other Parameters
        ----------
        value : int, None, default = None
            The new length of the undo history. If the value is less than the 
            figure's current undo history, then the oldest undo states are 
            deleted. If `None` then the undo history is reverted back to the 
            default defined in preferences.

        fig : :class:`matplotlib.figure.Figure`, None, default = None
            The figure to affect. If `None` then the figure is obtained from
            :meth:`matplotlib.pyplot.gcf`.
        """
        import matplotlib.pyplot as plt
        if fig is None: fig = plt.gcf()
        if value is None: value = preferences.undo_history
        fig.canvas.set_undo_history(value)


# Scrub the namespace
try: del os
except: pass

try: del metadata
except: pass

try: del util
except: pass

try: del matplotlib
except: pass

try: del api
except: pass

try: del warnings
except: pass

try: del traceback
except: pass






