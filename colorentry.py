#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colorentry.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: a ColorEntry object contains all information about one color,
# needed in the lab
#
# input: --
# output: --
#
# created 2010
# last mod 2013-01-29 11:19 KS

"""
This modules provides the class ColorEntry, which stores all important
information for one color.

"""

class ColorEntry(object):
    """
    ColorEntry contains all information for one color that we need in the
    lab.

    Attributes:
        name: string
            name of the color

        patch_stim_value: float, triple or string
            a value that can be used to set the color of psychopy.GratingStim

        monitor_xyY: triple of floats
            measured xyY values for monitor

        monitor_xyY_sd: triple of floats
            standard deviation for xyY values

        voltages: triple of int
            corresponding voltages for color tubes

        tubes_xyY: triple of floats
            measured xyY values for tubes

        tubes_xyY_sd: triple of floats
            standard deviation for xyY values

    Example:

    >>> ce1 = ColorEntry(name="grey1", patch_stim_value="#404040FF")
    >>> ce2 = ColorEntry(name="grey2", voltages=(0xA00, 0xA00, 0xA00))

    """

    def __init__(self, name, patch_stim_value=None, voltages=None):
        """
        Initializes the ColorEntry instance.

        Parameters:
            name: string
                name of the color

            patch_stim_value: *None*, float, triple or string
                default value that is used to set the color of psychopy.GratingStim
            voltages: *None* or triple of int
                default voltages for color tubes

        """
        # general
        self.name = name

        # monitor values
        self.patch_stim_value = patch_stim_value
        self.monitor_xyY = None
        self.monitor_xyY_sd = None

        # tubes values
        self.voltages = voltages
        self.tubes_xyY = None
        self.tubes_xyY_sd = None

