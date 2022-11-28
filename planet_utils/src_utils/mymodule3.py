"""
Module containing a third class.
"""
from planet_utils.mymodule1 import myClass1
from planet_utils.planet import *

class myClass3(myClass1):
  """This is the third class."""
  pass

class b:
    OK = "\033[92m"  # GREEN
    WARNING = "\033[96m"  # YELLOW
    FAIL = "\033[91m"  # RED
    RESET = "\033[0m"  # RESET COLOR


def mouse_event(event):
    print("x: {} and y: {}".format(np.round(event.xdata), np.round(event.ydata)))
    # global ix, iy
    ix, iy = event.xdata, event.ydata

    # global coords
    coords.append((ix, iy))
    pd.DataFrame(coords).to_csv("test_events.txt")
    print(coords)
    print(value_to_print)
    return coords



