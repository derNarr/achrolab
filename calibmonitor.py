#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./calibmonitor.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: all functions for monitor stuff
#
# input: --
# output: --
#
# created 2010
# last mod 2013-01-29 11:18 KS

"""
This module provides the class CalibMonitor which handles measuring of the
monitor.

"""

from eyeone.constants import eNoError, TRISTIMULUS_SIZE
from ctypes import c_float
import time
from monitor import Monitor


class CalibMonitor(Monitor):
    """
    Provides an easy interface to measure psychopy.visual.GratingStim
    colors with an i1 Pro.

    Example:

    >>> from eyeone import eyeone
    >>> eyeone = eyeone.EyeOne(dummy=True)
    >>> mon = CalibMonitor(eyeone)
    >>> mon.measureGratingStimColor("#FF0000FF", n=2) # doctest: +ELLIPSIS
    Measurement mode set to SingleEmission.
    Color space set to CIExyY.
    <BLANKLINE>
    Please put i1 Pro on calibration plate and press key to start calibration.
    Calibration of i1 Pro done.
    <BLANKLINE>
    Please put i1 Pro in measurement position and hit button to start measurement.
    <BLANKLINE>
    Please put i1 Pro in measurement position for MONITOR and press key to start
    measurement. (Measure through the Box! Not directly on the monitor.)
    Starting measurement...
    [(...), ...]

    """

    def __init__(self, eyeone, psychopy_win=None):
        Monitor.__init__(self, psychopy_win)
        self.eyeone = eyeone
        self.eyeone_calibrated = False

    def startMeasurement(self):
        """
        Simply prompts to move i1 Pro to measurement position and
        waits for button response.

        """
        print("\nPlease put i1 Pro in measurement position for" + " MONITOR and press key to start measurement. (Measure through the Box! Not directly on the monitor.)")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")

    def measureGratingStimColor(self, grating_stim_value, n=1):
        """
        Measures grating_stim_value on monitor.

        Parameters:
            grating_stim_value: triple, float or string
                psychopy.visual.GratingStim color value

            n: *1* or any other positive integer
                number of measurements (positive integer)

        Returns list of tuples of xyY values [(x1, y1, Y1), (x2, y2, Y2), ...]

        """
        #if not self.eyeone.is_calibrated:
        #    self.eyeone.calibrate()
        #    self.startMeasurement()

        self.setColor(grating_stim_value)
        xyY_list = []
        tri_stim = (c_float * TRISTIMULUS_SIZE)()

        #start measurement
        for i in range(n):
            self.grating_stim.draw()
            self.psychopy_win.flip()
            time.sleep(.5)

            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed.")
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus.")
            xyY_list.append( tuple(tri_stim) )

        return xyY_list

    def measureColor(self, color, n=1):
        """
        Converts xyY color (triple of floats) to psychopy.visual.GratingStim
        color and measures color on monitor.

        Parameters:
            color: triple of float
                xyY color list or tuple of three floats

            grating_stim_value: triple, float or string
                psychopy.visual.GratingStim color value

            n: *1* or any other positive integer
                number of measurements

        Returns:
        Returns list of tuples of xyY values [(x1, y1, Y1), (x2, y2, Y2), ...]

        """
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()
            self.startMeasurement()
        print("measureColor is not implemented yet.")
        # TODO measureColor
        pass

