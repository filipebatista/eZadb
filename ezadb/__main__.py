import platform
import sys
from ezadb.gui.EzADBGui import EzADBGui
from ezadb.utils.Log import Log

try:
    import tkinter as tk  # for python 3

except:
    import Tkinter as tk  # for python 2


def start_ezadb():
    print("python version: {0} on {1}".format(
        platform.python_version(), sys.platform))
    root = tk.Tk()
    root.withdraw()
    app = EzADBGui(root)
    root.title("eZADB - Easy Android Debug Bridge")
    root.wm_resizable(False, False)

    root.deiconify()
    app.run()


if __name__ == '__main__':
    try:
        start_ezadb()
    except:
        Log.error(None, "__main__: Unexpected error={ex}".format(ex=sys.exc_info()))
