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
# last mod 2012-05-29 KS

"""
This modules provides the class ColorEntry, which stores all important
information for one color.
"""

class ColorEntry(object):
    """
    ColorEntry contains all information for one color that we need in the
    lab.

    It contains:

      * a name
      * the corresponding value for psychopy.PatchStim
      * measured xyY values for monitor
      * standard deviation for xyY values
      * corresponding voltages for color tubes
      * measured xyY values for tubes
      * standard deviation for xyY values
    """

    def __init__(self, name, patch_stim_value=None, voltages=None):
        """
        * name (string) -- "color1"
        * patch_stim_value (float or triple of floats) -- 0.1 or (0.3, -0.3, -0.3)
        * monitor_xyY (triple of floats) -- (0.21, 0.23, 0.9)
        * monitor_xyY_sd (triple of floats) -- (0.02, 0.02, 0.001)
        * voltages (triple of integers) -- (0x000, 0x0F3, 0xFFF)
        * tubes_xyY (triple of floats) -- (0.21, 0.23, 0.9)
        * tubes_xyY_sd (triple of floats) -- (0.02, 0.02, 0.001)
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

