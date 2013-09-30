#!/usr/bin/env python3
import signal
from gi.repository import Gtk
from gui.MainWindow import MainWindow

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
