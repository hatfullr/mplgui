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


