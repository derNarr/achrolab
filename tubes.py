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
# last mod 2012-07-11 19:02 KS

"""
The tubes class gives an easy interface to handle the tubes and CalibTubes
provides convenient methods to measure and calibrate the tubes.

"""

import devtubes
from colorentry import ColorEntry


# TODO: Paths
#from os import chdir, path
#        chdir(path.dirname(self.__file__))

class Tubes(object):
    """
    Gives high level access to the tubes.

    This class hides all the hardware specifications and has no
    dependencies on the eyeone module.

    :Example:

        >>> tub = Tubes(dummy=True)
        >>> tub.setVoltages((1000, 1000, 1000))
        >>> tub.printNote()
        <BLANKLINE>
                Note:
                The tubes must be switched on for at least four (!!) hours to come
                in a state where they are not changing the illumination a
                significant amount.
        <BLANKLINE>


    """
    def __init__(self, dummy=False):
        """
        Initializes tubes object.

        devtub contains an object with a method setVoltages. This method
        gets a triple of integers and sets the voltages of the tubes. The
        devtubes object takes care of all the hardware stuff.

        :Parameters:

            dummy : *False* or True
                If dummy=True no wasco runtimelibraries will be loaded.

        """
        self.devtub = devtubes.DevTubes(dummy=dummy)

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

