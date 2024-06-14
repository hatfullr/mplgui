import mplgui.lib.reader
import matplotlib.axes
import numpy as np

class ScatterReader(mplgui.lib.reader.Reader, object):
    """ Expects two columns of data, where column 0 is x data and column 1 is y
    data. The columns must be separated by whitespace. Only works with text 
    files. Creates a scatter plot. """
    def read(self, ax : matplotlib.axes.Axes, filename : str):
        xy = []
        with open(filename, 'r') as f:
            for line in f:
                xy += [line.strip().split()]
        xy = np.asarray(xy, dtype=object).astype(float)
        return ax.scatter(xy[:,0], xy[:,1])
