Installing Forge
================

Requirements
------------
- Python 3 : http://www.python.org/
- GTK+ : http://www.gtk.org/ 
- PyGObject : https://wiki.gnome.org/PyGObject

- An installation of Blades of Avernum, for the graphics files and core scripts. 
  Currently, only the Windows version is supported (no resource forks).    

Linux
-----
Tested with Ubuntu 13.04 and Debian jessie/sid.

    sudo aptitude install python3 python3-gi

Windows
-------
Download the stable builds from the above websites, and hope for the best.

Setup
-----
Run this Python script, and enter the appropriate path of the BoA installation.

    ./setup.py


Running the Map Viewer
======================

Run this Python script:

    ./main.py

You will be able to open any *.bas file that is in its proper location; that is, 
in the same directory with the scenario data script and all the custom graphics.

Navigation
----------

The map can be scrolled with the arrow keys as well as by dragging the mouse.
The scroll wheel can be used to zoom. 
