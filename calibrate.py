#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# calibrate.py
#
# (c) 2012 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# created 2012-05-29 KS
# last mod 2012-05-29 KS
#

"""
The module calibrate provides the classes to calibrate lightning tubes and
the color of a monitor to each other with a photometer.
"""

class Calibrate(object):
    """
    Calibrate capsulates the hardware dependencies to the photometer and to
    the tubes and the monitor.

    This class also implements the calibration procedure.
    """

    def __init__(self, eyeone, monitor, tubes):
        self.eyeone = eyeone
        self.monitor = monitor
        self.tubes = tubes

    def calibrateTubes(self):
        """
        measure the different colors of the tubes separately.

        With these measurements we guess the starting point of our
        matching between monitor color and tubes color.
        """
        tubes.printNote()
        # TODO

    def guessVoltages(self):
        """
        guesses the voltages for the tubes for a given color.
        """
        # TODO

    def setManualPlot(self):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        In order to match the values they are measured with the photometer
        and plotted.
        """
        # TODO

    def setManualVision(self):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        The changed values are not measured, they are simply shown on the
        wall and the target value is presented at the monitor. It should be
        possible to adjust the colors with your own visual system.
        """
        # TODO

    def _setManual(self):
        """
        non-public method containing the key stroke and tubes setting
        things needed in setManual* methods.
        """
        # TODO
 

