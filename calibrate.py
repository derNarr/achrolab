#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# calibrate.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: (1) Calibrate
#          (2) calibrateColorTable
#          (3) calibrateColorEntry
#
# input: --
# output: --
#
# created 2012-05-29 KS
# last mod 2012-05-29 22:22 KS

"""
The module calibrate provides the classes to calibrate lightning tubes and
the color of a monitor to each other with a photometer.
"""

class Calibrate(object):
    """
    Calibrate capsulates the hardware dependencies to the photometer and to
    the tubes and the monitor.

    This class also implements the calibration procedure. This calibration
    start, when calibrateColorTable or calibrateColorEntry are called.

    * test if the tubes are calibrated, if not abort
    * test if the color entry was measured at the monitor, if not skip this
      color entry value
    * guess starting voltages from color entry values (or use given)
    * start adjustManualPlot so that you can adjust the tubes by hand and
      see your result measured with the photometer
    * start adjustManualVision check if the achieved calibration fits to
      your own visual system and adjust if necessary
    * store final calibration in color entry
    """

    def __init__(self, eyeone, calibmonitor, calibtubes):
        """
        :Parameters:

            eyeone : eyeone.EyeOne object to measure the colors
            calibmonitor : CalibMonitor object
            calibtubes : CalibTubes object which is calibrated.
        """
        self.eyeone = eyeone
        self.calibmonitor = calibmonitor
        self.calibtubes = calibtubes
        if not calibtubes.is_calibrated:
            print("""STOP: Please calibrate tubes first or initialize
            Calibrate object with CalibTubes where an old parameters file
            is loaded!""")
            # TODO insert reasonable exception here

    def adjustManualPlot(self, xyY, start_voltages=None):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        In order to match the values they are measured with the photometer
        and plotted.

        :Parameters:

        xyY : triple containing the three values for the xyY color
        start_voltages : triple containing three values for the voltages,
        if None starting values are guessed
        """

        if not start_voltages:
            print("Guess voltages via calibration of tubes.")
            start_voltages = self.calibtubes.guessVoltages(xyY[2])

        self.calibtubes.setVoltages(start_voltages)
        self.calibtubes.printNote()
        
        # TODO

    def adjustManualVision(self, xyY, start_voltages=None):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        The changed values are not measured, they are simply shown on the
        wall and the target value is presented at the monitor. It should be
        possible to adjust the colors with your own visual system.

        :Parameters:

        xyY : triple containing the three values for the xyY color
        start_voltages : triple containing three values for the
        voltages, if None starting values are guessed
        """
        if not start_voltages:
            print("guess voltages via calibration of the tubes")
            start_voltages = self.calibtubes.guessVoltages(xyY[2])
        # TODO

    def _adjustManual(self):
        """
        non-public method containing the key stroke and tubes setting
        things needed in setManual* methods.
        """
        # TODO
 
def calibrateColorTable(colortable):
    """
    convinient function to calibrate a colortable. Changes the colortable
    object!
    """
    # TODO

def calibrateColorEntry(colorentry):
    """
    convinient function to calibrate a single colorentry object. Changes
    the colorentry object!
    """
    # TODO

