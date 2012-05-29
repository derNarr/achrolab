#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tubes.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: (1) Tubes classes, which provide functions for working
#              with the tubes.
#
# input: --
# output: --
#
# created 2010
# last mod 2012-05-29 KS

"""
The tubes class gives an easy interface to handle the tubes and CalibTubes
provides convenient methods to measure and calibrate the tubes.
"""

from eyeone.constants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    COLOR_SPACE_RGB,
                                    TRISTIMULUS_SIZE,
                                    SPECTRUM_SIZE)
from ctypes import c_float
import time
from exceptions import ValueError

from math import exp,log
import numpy as np
from scipy.optimize import curve_fit

from convert import xyY2rgb

import pickle

import devtubes

from colorentry import ColorEntry

from iterativeColorTubes import IterativeColorTubes

# TODO: Paths
#from os import chdir, path
#        chdir(path.dirname(self.__file__))

class Tubes(object):
    """
    Gives high level access to the tubes.

    This class hides all the hardware specifications and has no
    dependencies on the eyeone module.
    """
    def __init__(self):
        """
        Initializes tubes object.

        devtub contains an object with a method setVoltages. This method
        gets a triple of integers and sets the voltages of the tubes. The
        devtubes object takes care of all the hardware stuff.
        """
        self.devtub = devtubes.DevTubes()

    def setVoltages(self, voltages):
        """
        Sets tubes to given voltages.

        If setVoltages gets an ColorEntry object, it extracts the voltages
        from this object and sets the tubes accordingly.

        WARNING: Don't set the tubes directly (e.g. via wasco), because
        the change in voltage has to be smoothly. This prevents the
        fluorescent tubes to accidentally give out.
        """
        if isinstance(voltages, ColorEntry):
            self.devtub.setVoltages(voltages.voltages)
        else:
            self.devtub.setVoltages(voltages) 

    def printNote(self):
        """
        prints a note, that states what is important, when you use the
        tubes.
        """
        print("""
        Note:
        The tubes must be switched on for at least four (!!) hours to come
        in a state where they are not changing the illumination a
        significant amount.
        """)


