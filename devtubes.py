#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./devtubes.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: the DevTubes class provides all low level functionality of for
# the tubes.
#
# input: --
# output: --
#
# created 2010
# last mod 2013-01-01 10:40 KS

from __future__ import print_function
import sys
from wasco.wasco import Wasco
from wasco.constants import DAOUT2, DAOUT3, DAOUT4
import time


class DevTubes(object):
    """
    DevTubes encapsulates all functions controlling fluorescent tubes in the
    booth. It provides all low level functionality.

    Example:

    >>> devtub = DevTubes(dummy=True)
    >>> devtub.setVoltages((1000, 1000, 1000))

    """
    def __init__(self, dummy=False):
        """Setting some "global" variables.

        If dummy=True no wasco runtimelibraries will be loaded.

        """

        self.wascocard = Wasco(dummy=dummy)    # create wasco object
        self.wasco_boardId = self.wascocard.boardId

        self.red_out = DAOUT3
        self.green_out = DAOUT4
        self.blue_out = DAOUT2
        self.low_threshold = 0x200 # min voltages must be integer
        self.low_warning = 0x400 # low warning voltages must be integer
        self.high_threshold = 0xFFF # max voltages must be integer

        # voltage which is set at the moment
        self.U_r = self.high_threshold
        self.U_b = self.high_threshold
        self.U_g = self.high_threshold


    def setVoltages(self, U_rgb):
        """
        setVoltages sets voltage in list or tuple of U_rgb to wasco card.
        U_rgb should contain three integers between self.low_threshold and
        self.high_threshold.

        """
        #set the wasco-card stepwise to the right voltage
        U_r_new = int(U_rgb[0])
        U_g_new = int(U_rgb[1])
        U_b_new = int(U_rgb[2])

        # warning
        if U_r_new < self.low_warning:
            print("WARNING: red channel is below recommended range (" +
                    str(self.low_warning) +")", file=sys.stderr)
        if U_g_new < self.low_warning:
            print("WARNING: green channel is below recommended range (" +
                    str(self.low_warning) +")", file=sys.stderr)
        if U_b_new < self.low_warning:
            print("WARNING: blue channel is below recommended range (" +
                    str(self.low_warning) +")", file=sys.stderr)

        # hard threshold
        if U_r_new < self.low_threshold:
            print("red channel is on minimum (" + str(self.low_threshold)
                    +")", file=sys.stderr)
            U_r_new = self.low_threshold
        if U_r_new > self.high_threshold:
            print("red channel is on maximum (" + str(self.high_threshold)
                    +")", file=sys.stderr)
            U_r_new = self.high_threshold
        if U_g_new < self.low_threshold:
            print("green channel is on minimum (" + str(self.low_threshold)
            +")", file=sys.stderr)
            U_g_new = self.low_threshold
        if U_g_new > self.high_threshold:
            print("green channel is on maximum (" + str(self.high_threshold)
                    +")", file=sys.stderr)
            U_g_new = self.high_threshold
        if U_b_new < self.low_threshold:
            print("blue channel is on minimum (" + str(self.low_threshold)
                    +")", file=sys.stderr)
            U_b_new = self.low_threshold
        if U_b_new > self.high_threshold:
            print("blue channel is on maximum (" + str(self.high_threshold)
                    +")", file=sys.stderr)
            U_b_new = self.high_threshold

        diff_r = U_r_new - self.U_r
        diff_g = U_g_new - self.U_g
        diff_b = U_b_new - self.U_b

        steps = max( abs(diff_r), abs(diff_g), abs(diff_b))
        steps = int(steps*0.2)

        if steps == 0:
            return

        slope_r = diff_r/float(steps)
        slope_g = diff_g/float(steps)
        slope_b = diff_b/float(steps)

        for i in range(steps):
            time.sleep(0.0001)
            self.wascocard.wasco_outportW(self.wasco_boardId,
                    self.red_out, int(self.U_r + slope_r*i))
            self.wascocard.wasco_outportW(self.wasco_boardId,
                    self.green_out, int(self.U_g + slope_g*i))
            self.wascocard.wasco_outportW(self.wasco_boardId,
                    self.blue_out, int(self.U_b + slope_b*i))
        self.U_r = U_r_new
        self.U_g = U_g_new
        self.U_b = U_b_new
        return

