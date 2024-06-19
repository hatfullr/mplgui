import matplotlib.patches
import matplotlib.axes
import copy
import matplotlib.transforms

class AxesHighlight(matplotlib.collections.PathCollection, object):
    """
    Used to create a highlight effect around the Axes this artist is on.
    """
    def __init__(self, axes : matplotlib.axes.Axes | type(None) = None):
        import mplgui
        super(AxesHighlight, self).__init__(
            [],
            **mplgui.preferences.axes_highlight
        )
        if axes is not None: self.set_axes(axes)
    
    def set_axes(self, axes : matplotlib.axes.Axes):
        # Remove us from the figure if we are moving across figures or the axes
        # is being set to None
        visible_before = self.get_visible()
        if self._axes is not None:
            if axes is None or axes.get_figure() != self._axes.get_figure():
                self.remove()
        if self._axes is None: # Add it to the figure for the first time
            axes.get_figure().add_artist(self)
            self.set_visible(visible_before)
            axes.get_figure().canvas.draw_idle()
        
        self._axes = axes
        if axes is not None:
            self.set_transform(axes.transAxes)
        
        self.update_paths()
    
    def update_paths(self, *args, **kwargs):
        if self._axes is None:
            self.set_paths([])
            return
        
        transform_inverted = self.get_transform().inverted()
        paths = []
        for spine in self._axes.spines.values():
            if not spine.get_visible(): continue
            paths += [spine.get_path().transformed(spine.get_transform()).transformed(transform_inverted)]
        self.set_paths(paths)
        
    def toggle(self, *args, **kwargs):
        self.set_visible(not self.get_visible())

