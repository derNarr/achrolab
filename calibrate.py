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
# last mod 2013-01-29 11:18 KS

"""
The module calibrate provides the classes to calibrate lightning tubes and
the color of a monitor to each other with a photometer.

"""

import math
import scipy

from setmanual import SetTubesManualPlot, SetTubesManualVision

class Calibrate(object):
    """
    Calibrate capsulates the hardware dependencies to the photometer and to
    the tubes and the monitor.

    This class also implements the calibration procedure. This calibration
    start, when calibrateColorTable or calibrateColorEntry are called.

    1. test if the tubes are calibrated, if not abort
    2. test if the color entry was measured at the monitor, if not skip this
       color entry value
    3. guess starting voltages from color entry values (or use given)
    4. start adjustManualPlot so that you can adjust the tubes by hand and
       see your result measured with the photometer
    5. start adjustManualVision check if the achieved calibration fits to
       your own visual system and adjust if necessary
    6. store final calibration in color entry

    Example
    -------

        >>> from achrolab.eyeone.eyeone import EyeOne
        >>> from achrolab.calibmonitor import CalibMonitor
        >>> from achrolab.calibtubes import CalibTubes
        >>> from achrolab.colortable import ColorTable
        >>> from achrolab.colorentry import ColorEntry
        >>> eyeone = EyeOne()
        >>> calibmonitor = CalibMonitor(eyeone)
        >>> calibtubes = CalibTubes(eyeone)
        >>> calibtubes.calibrate(imi=0.1, n=4, each=1) #doctest: +ELLIPSIS
        <BLANKLINE>
                Note:
                The tubes must be switched on for at least four (!!) hours to come
                in a state where they are not changing the illumination a
                significant amount.
        <BLANKLINE>
        Measurement mode set to SingleEmission.
        Color space set to CIExyY.
        <BLANKLINE>
        Please put EyeOne Pro on calibration plate and press key to start calibration.
        Calibration of EyeOne Pro done.
        <BLANKLINE>
        Please put EyeOne-Pro in measurement positionand hit button to start measurement.
        <BLANKLINE>
        Please put EyeOne Pro in measurement position and press key to start measurement.
        <BLANKLINE>
        Turn off blue and green tubes!
        Press key to start measurement of RED tubes.
        Starting measurement...
        (1024, 4095, 4095)
        (2047, 4095, 4095)
        (3070, 4095, 4095)
        (4093, 4095, 4095)
        <BLANKLINE>
        Turn off red and blue tubes!
        Press key to start measurement of GREEN tubes.
        Starting measurement...
        (4095, 1024, 4095)
        (4095, 2047, 4095)
        (4095, 3070, 4095)
        (4095, 4093, 4095)
        <BLANKLINE>
        Turn off red and green tubes!
        Press key to start measurement of BLUE tubes.
        Starting measurement...
        (4095, 4095, 1024)
        (4095, 4095, 2047)
        (4095, 4095, 3070)
        (4095, 4095, 4093)
        <BLANKLINE>
        Turn ON red, green and blue tubes!
        Press key to start measurement of ALL tubes.
        Starting measurement...
        (1024, 1024, 1024)
        (2047, 2047, 2047)
        (3070, 3070, 3070)
        (4093, 4093, 4093)
        Measurement finished.
        ...
        ...
        >>> calibtubes.is_calibrated = True
        >>> calibrate = Calibrate(calibmonitor, calibtubes)
        <BLANKLINE>
        Initializing search mode complete.
        >>> colortable = ColorTable()
        >>> color1 = ColorEntry("darkgreen", patch_stim_value=(0,100,0))
        >>> color2 = ColorEntry("darkred", patch_stim_value=(100,0,0))
        >>> colortable.addColorEntry(color1)
        >>> colortable.addColorEntry(color2)
        >>> calibrate.calibrateColorTable(colortable)
        >>> print(colortable.color_list[0].monitor_xyY) #doctest: +ELLIPSIS
        (..., ..., ...)
        >>> print(colortable.color_list[0].voltages) #doctest: +ELLIPSIS
        (..., ..., ...)
        >>> print(colortable.color_list[0].tubes_xyY) #doctest: +ELLIPSIS
        (..., ..., ...)

    """

    def __init__(self, calibmonitor, calibtubes):
        """
        Parameters
        ----------
            calibmonitor : calibmonitor.CalibMonitor object
                the CalibMonitor object is used to present the stimuli on the
                monitor and to measure the corresponding values
            calibtubes : calibtubes.CalibTubes object which is calibrated
                the CalibTubes object is used to set the voltages of the
                tubes and to measure the corresponding values

        """
        self.calibmonitor = calibmonitor
        self.calibtubes = calibtubes
        if not calibtubes.is_calibrated:
            print("""STOP: Please calibrate tubes first or initialize
            Calibrate object with CalibTubes where an old parameters file
            is loaded!""")
            # TODO insert reasonable exception here
        self.set_manually_plot = SetTubesManualPlot(self.calibtubes)
        self.set_manually_vision = SetTubesManualVision(self.calibtubes,
                self.calibmonitor)

    def adjustManualPlot(self, xyY, start_voltages=None):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        In order to match the values they are measured with the photometer
        and plotted.

        Returns the final triple (voltages, xyY, spectrum).

        Parameters
        ----------
            xyY : (x, y, Y)
                triple containing the three values for the xyY color
            start_voltages : *None* or (vol_red, vol_green, vol_blue)
                triple containing three values for the voltages if *None*
                starting values are guessed

        """
        if not start_voltages:
            print("Guess voltages via calibration of tubes.")
            start_voltages = self.calibtubes.guessVoltages(xyY[2])
        self.calibtubes.setVoltages(start_voltages)
        self.calibtubes.printNote()
        self.set_manually_plot.start_voltages = start_voltages
        self.set_manually_plot.target_color = xyY
        return self.set_manually_plot.run()

    def adjustManualVision(self, color, start_voltages=None):
        """
        changes the tubes with key strokes in order to match the color and
        luminance of the wall to a given color value.

        The changed values are not measured, they are simply shown on the
        wall and the target value is presented at the monitor. It should be
        possible to adjust the colors with your own visual system.

        Returns the final triple of voltages.

        Parameters
        ----------
            color : color, that can be used by monitor.Monitor.setColor
                this color will be presented by monitor.Monitor.setColor
                and is the target color to which you want to match the
                tubes
            start_voltages : *None* or (vol_red, vol_green, vol_blue)
                triple containing three values for the voltages if *None*
                starting values are guessed

        """
        if not start_voltages:
            print("guess voltages via calibration of the tubes")
            start_voltages = self.calibtubes.guessVoltages(color[2])
        self.calibtubes.setVoltages(start_voltages)
        self.calibtubes.printNote()
        self.set_manually_vision.start_voltages = start_voltages
        self.set_manually_vision.target_color = color
        return self.set_manually_vision.run()


    def calibrateColorTable(self, colortable, each=5):
        """
        convinient function to calibrate a colortable. Changes the
        colortable object!

        Parameters
        ----------
            colortable : colortable.ColorTable
                all color is the ColorTable object will be calibrated
            each : *5* or int
                number of repeated measurements per colorentry

        """
        if not self.calibtubes.is_calibrated:
            print("ERROR Please calibrate tubes and start again.")
            return
        # MONITOR
        self.calibmonitor.startMeasurement()
        for ce in colortable.color_list:
            self._measureColorEntryMonitor(ce, n=each)
        # TUBES
        self.calibtubes.startMeasurement()
        for ce in colortable.color_list:
            start_voltages = ce.voltages
            (voltages, xyY, spectrum) = self.adjustManualPlot(
                    ce.monitor_xyY, start_voltages)
            ce.voltages = voltages
        print("Now the visual calibration starts. Please make sure, that" +
                " you can see the monitor and the illuminated wall at the"
                + " same time.\n")
        for ce in colortable.color_list:
            voltages_vision = self.adjustManualVision(
                    ce.patch_stim_value, ce.voltages)
            ce.voltages = voltages_vision
        self.calibtubes.startMeasurement()
        for ce in colortable.color_list:
            self._measureColorEntryTubes(ce, n=each)


    def calibrateColorEntry(self, colorentry, n=5):
        """
        convenient function to calibrate a single colorentry object.
        Changes the colorentry object!

        Parameters
        ----------
            colorentry : colorentry.ColorEntry
                the ColorEntry object will be calibrated
            n : *5* or int
                number of repeated measurements per condition

        """
        if not self.calibtubes.is_calibrated:
            print("ERROR Please calibrate tubes and start again.")
            return
        # MONITOR
        self.calibmonitor.startMeasurement()
        self._measureColorEntryMonitor(colorentry, n=n)
        # TUBES
        self.calibtubes.startMeasurement()
        start_voltages = colorentry.voltages
        (voltages, xyY, spectrum) = self.adjustManualPlot(
                colorentry.monitor_xyY, start_voltages)
        voltages_vision = self.adjustManualVision(
                colorentry.patch_stim_value, voltages)
        colorentry.voltages = voltages_vision
        self.calibtubes.startMeasurement()
        self._measureColorEntryTubes(colorentry, n=n)

    def _measureColorEntryMonitor(self, colorentry, n=5):
        xyY_list = self.calibmonitor.measureGratingStimColor(
                colorentry.patch_stim_value, n)
        colorentry.monitor_xyY = (
                scipy.mean([xyY[0] for xyY in xyY_list]),
                scipy.mean([xyY[1] for xyY in xyY_list]),
                scipy.mean([xyY[2] for xyY in xyY_list]))
        colorentry.monitor_xyY_sd = (
                math.sqrt(scipy.var([xyY[0] for xyY in xyY_list])),
                math.sqrt(scipy.var([xyY[1] for xyY in xyY_list])),
                math.sqrt(scipy.var([xyY[2] for xyY in xyY_list])))

    def _measureColorEntryTubes(self, colorentry, n=5):
        vol_col_spec_list = self.calibtubes.measureVoltages(
                [colorentry.voltages,],
                imi=0.5, each=n)
        colorentry.tubes_xyY = (
                scipy.mean([vol_col_spec[1][0] for vol_col_spec in
                    vol_col_spec_list]),
                scipy.mean([vol_col_spec[1][1] for vol_col_spec in
                    vol_col_spec_list]),
                scipy.mean([vol_col_spec[1][2] for vol_col_spec in
                    vol_col_spec_list]))
        colorentry.tubes_xyY_sd = (
                math.sqrt(scipy.var([vol_col_spec[1][0] for vol_col_spec in
                    vol_col_spec_list])),
                math.sqrt(scipy.var([vol_col_spec[1][1] for vol_col_spec in
                    vol_col_spec_list])),
                math.sqrt(scipy.var([vol_col_spec[1][2] for vol_col_spec in
                    vol_col_spec_list])))

