import os
import importlib.metadata as metadata
import importlib.util as util

__version__ = metadata.version('mplgui')

if __file__.endswith(os.path.join('mplgui', 'mplgui','__init__.py')):
    SOURCE_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
else:
    SOURCE_DIRECTORY = os.path.dirname(os.path.dirname(util.find_spec('mplgui').origin))

try: del metadata
except: pass

try: del util
except: pass

try: del os
except: pass

import matplotlib
matplotlib.use('tkagg')

try: del matplotlib
except: pass
