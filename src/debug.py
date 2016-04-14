# Our debugging functionality.
import time

_debug_ = open("dbg.txt", "w")

def debug(msg):
    fdt = time.strftime("%c") + ": "
    _debug_.write(fdt + msg + "\n")

def end():
    _debug_.close()
