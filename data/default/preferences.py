from mplgui.lib.menubar import FILE,OPEN,SAVE,EXPORT,CLOSE,EDIT,UNDO,REDO

undo_history = 100

# This is how long the messages appear on the plot, such as "Saving...",
# "Saved", "Loading...", etc.
message = {
    'duration' : 1000, # ms
    'place' : {
        'relx' : 1,
        'rely' : 0,
        'anchor' : 'ne',
    },
}

# These are tkinter event bindings (https://tcl.tk/man/tcl/TkCmd/bind.htm)
hotkeys = {
    'MenuBar' : {
        FILE : {
            OPEN : '<Control-o>',
            SAVE : '<Control-s>',
            EXPORT: '<Control-e>',
            CLOSE : '<Alt-F4>',
        },
        EDIT : {
            UNDO : '<Control-z>',
            REDO : '<Control-y>',
        },
    },
}


# Controls the highlighting when the mouse hovers over an Axes. This dict is
# used on each spine of the Axes. Each dict item must correspond to a keyword
# value in the artist constructor.
axes_highlight = {
    'edgecolor' : 'r',
    'facecolor' : 'none',
    'lw' : 1,
    'linestyle' : '--',
    'zorder' : float('inf'),
}
