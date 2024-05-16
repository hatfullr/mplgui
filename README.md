# MPLGUI

A Python library which extends the functionality of Matplotlib by implementing a
full graphical user interface in the form of a menu bar on each Figure. After
importing this package, all Matplotlib figures will have a menu bar. Here is an
example:

```python3
import matplotlib.pyplot as plt
import mplgui

fig, ax = plt.subplots()

plt.show()
```

This package works by defining a new type of Matplotlib backend, which is
enforced upon import with `matplotlib.use('mplgui')`. The `mplgui` backend
inherits from the `TkAgg` backend and extends its functionality. As such, `tk`
is required by this package.



