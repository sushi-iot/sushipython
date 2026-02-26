# Frozen MicroPython modules

This folder contains the *frozen* modules, these are classic ".py" modules embedded into SushiPython firmware.  
It's possible extend/edit these modules just loading the modified .py file into MicroPython file system, in this way the frozen version will be replaced by the ones save into the disk.


## Files description

* `sushi_menu.py` : User menu management  
* `sushi_utils.py` : System setup, status & utilities  
* `sushi_defs.py` : Not a module itself. Contains definitions used by `sushi_utils` module