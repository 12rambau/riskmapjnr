# if you only have few widgets, a module is not necessary and you can simply use a scripts.py file
# in a big module with lot of custom scripts, it can make sense to split things in separate files for the sake of maintenance

from .fcc import *

# if you use a module import all the functions here to only have 1 call to make
from .grid import *
