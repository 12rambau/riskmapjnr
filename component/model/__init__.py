# if you only have few widgets, a module is not necessary and you can simply use a model.py file
# in a big module with lot of custom models, it can make sense to split things in separate files for the sake of maintenance

# if you use a module import all the functions here to only have 1 call to make
from .fcc_model import *
