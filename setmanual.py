#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./setTubesManual.py
#
# (c) 2010 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content:
#
# input: --
# output: --
#
# created
# last mod 2012-06-30 18:29 KS

"""
This module provides a class to manually adjust the tubes. With key strokes
you can adjust the color of the tubes and then with another key stroke
measure the current color with the EyeOne photometer. The measurements and
the target color are plottet in a figure, so that you know in which
direction you should change your illumination.

"""

import matplotlib.pyplot as plt
import numpy as np
import time
from ctypes import c_float

from eyeone.constants import  (eNoError,
                                    SPECTRUM_SIZE,
                                    TRISTIMULUS_SIZE)

def setColorTube(key):
    """
    Defines which color tubes should be changed.

    returns tuple (color channel, index)

    """
    if key == 'r':
        return ('red', 0)
    elif key == 'g':
        return ('green', 1)
    elif key == 'b':
        return ('blue', 2)
    elif key == 'a':
        return ('all', None) #index is out of range, should not be used!
    else:
        pass

def setStepSize(key):
    """
    Defines step size of change.

    """
    if key == '1':
        return 1
    elif key == '2':
        return 5
    elif key == '3':
        return 10
    elif key == '4':
        return 50
    elif key == '5':
        return 100
    else:
        pass

class SetTubesManualBase(object):
    """
    base class for SetTubesManualPlot and SetTubesManualVision implementing
    all the stuff with the tubes.

    """

    def __init__(self, tubes, start_voltages=None, target_color=None):
        """
        :Parameters:

            tubes : tubes.Tubes
                Tubes object to change the voltages of the tubes
            start_voltages : *None* or (vol_r, vol_g, vol_b)
                triple of int containing the start_voltages for the tubes,
                if *None* than the start_voltages has to be assigned before
                method run() is called
            target_color : *None* or (x, y, Y)
                triple of float containing the target color, which was
                measured on the monitor,
                if *None* than the target_color has to be assigned before
                method run() is called

        """
        if start_voltages:
            self.voltages = list(start_voltages)
        else:
            self.voltages = None
        self.target_color = target_color
        self.tub = tubes
        self.imi = 0.5
        self.each = 5 #number of measurements per voltage
        self.colortube = ('red', 0)
        self.step = 10
        self.i = 0 # number of measurement

    def __setattr__(self, name, value):
        """
        cast the voltages to list, if they are set, to make them mutable.
        Additionally, if start_voltages are assigned, then set voltages
        accordingly.

        """
        if name in ("voltages", "start_voltages"):
            if value:
                self.__dict__["voltages"] = list(value)
            else:
                self.__dict__["voltages"] = None
        else:
            self.__dict__[name] = value

    def adjustTube(self):
        """
        Enables up and down arrow to adjust tubes' color step by step (lower if
        down and higher if up).

        """
        key = self.key
        step = self.step
        colortube = self.colortube
        if colortube[0] == "all" and key == "up":
            self.voltages[0] = self.voltages[0] + step
            self.voltages[1] = self.voltages[1] + step
            self.voltages[2] = self.voltages[2] + step
        elif colortube[0] == "all" and key == "down":
            self.voltages[0] = self.voltages[0] - step
            self.voltages[1] = self.voltages[1] - step
            self.voltages[2] = self.voltages[2] - step
        elif not colortube[0] == "all" and key == "up":
            self.voltages[colortube[1]] = self.voltages[colortube[1]] + step
        elif not colortube[0] == "all" and key == "down":
            self.voltages[colortube[1]] = self.voltages[colortube[1]] - step
        else:
            pass
        self.tub.setVoltages(self.voltages)
        self.tellme(str(self.voltages))

    def tellme(self, s):
        """
        function to write *s* to the stdout.

        """
        print(s)

    def run(self):
        """
        Starts program to set tubes by hand. Has to be implemented by
        children.

        """
        pass

    def measureVoltage(self):
        """
        If you want to actually measure the tubes, you have to implement
        this method.

        """
        pass

    def newFigure(self):
        """
        If you want to actually have a plot, than implement this method. It
        should recreate the plot and dismisses all old measurements.

        """
        pass

    def onKeyPress(self, event):
        """
        handles the different key presses and calls the corresponding
        method.

        """
        key = event.key
        self.key = key
        #print(key)
        if key == 'r' or key == 'g' or key == 'b' or key == 'a':
            self.colortube = setColorTube(key)
            self.tellme('Now change ' + self.colortube[0] + ' tubes.')
        elif key == '1' or key == '2' or key == '3' or key == '4' or key == '5':
            self.step = setStepSize(key)
            self.tellme('Step size set to ' + str(self.step))
        elif key == 'up' or key == 'down':
            self.adjustTube()
        elif key == 'space':
            self.measureVoltage()
        elif key == 'c':
            # close and reprint figure
            self.newFigure()
        elif key == 'escape':
            self.stop = True

class SetTubesManualVision(SetTubesManualBase):
    """
    creates an interactive screen, which shows the target color and allows
    to adjust the tubes with key strokes.

    :Example:

        >>> from achrolab.tubes import Tubes
        >>> from achrolab.monitor import Monitor
        >>> tubes = Tubes()
        >>> monitor = Monitor()
        >>> man_vision = SetTubesManualVision(tubes, monitor,
        ...         start_voltages=(1561, 2253, 2181), target_color=(0,
        ...         100, 0))
        >>> final_voltages = man_vision.run()
        <BLANKLINE>
        <BLANKLINE>
        Manual adjustment of tubes` color
        <BLANKLINE>
        Press [up] for higher intensity or press [down] for lower intensity.
        To set tube color and step size press the following buttons:
        Stepsize:
         [1] - 1
         [2] - 5
         [3] - 10
         [4] - 50
         [5] - 100
        Colortube:
         [r] - Red
         [g] - Green
         [b] - Blue
         [a] - all
        Press [escape] to quit (and save last voltages)
        >>> print(final_voltages) #doctest: +ELLIPSIS
        [...,...,...]

    """

    def __init__(self, tubes, monitor, start_voltages=None, target_color=None):
        """
        :Parameters:

            tubes : tubes.Tubes
                Tubes object to change the voltages of the tubes
            monitor : monitor.Monitor
                Monitor object allows presenting the color on the monitor
                and handles key strokes
            start_voltages : *None* or (vol_r, vol_g, vol_b)
                triple of int containing the start_voltages for the tubes,
                if *None* than the start_voltages has to be assigned before
                method run() is called
            target_color : *None* or color, that Monitor.setColor accepts
                if *None* than the target_color has to be assigned before
                method run() is called

        """
        SetTubesManualBase.__init__(self, tubes, start_voltages, target_color)
        self.mon = monitor

    def run(self):
        """
        Starts program to set tubes by hand.

        Returns the final triple of voltages.

        """
        if not (self.target_color and self.voltages):
            raise ValueError("Please assign target_color and start_voltages"
                    + "before calling run()!")
        self.tub.setVoltages(self.voltages)
        self.mon.setColor( self.target_color )
        print('\n\nManual adjustment of tubes` color\n\n' +
              'Press [up] for higher intensity ' +
              'or press [down] for lower intensity.\n' +
              'To set tube color and step size press the following buttons:\n' +
              'Stepsize:\n' +
              ' [1] - 1\n [2] - 5\n [3] - 10\n [4] - 50\n [5] - 100\n' +
              'Colortube:\n [r] - Red\n [g] - Green\n [b] - Blue\n [a] - all'
              + '\nPress [escape] to quit (and save last voltages)')
        self.stop=False
        while not self.stop:
            self.mon.waitForButtonPress()
            self.onKeyPress(self.mon.e)
        return( self.voltages )


class SetTubesManualPlot(SetTubesManualBase):
    """
    creates an interactive figure with matplotlib, so that you can adjust
    the tubes and plot you measurements in this figure.

    :Example:

        >>> from achrolab.eyeone.eyeone import EyeOne
        >>> from achrolab.calibtubes import CalibTubes
        >>> eyeone = EyeOne()
        >>> calibtubes = CalibTubes(eyeone)
        >>> man_plot = SetTubesManualPlot(calibtubes, start_voltages=(1561,
        ...         2253, 2181), target_color=(0.298, 0.321, 64.1))
        Measurement mode set to SingleEmission.
        Color space set to CIExyY.
        <BLANKLINE>
        Please put EyeOne Pro on calibration plate and press key to start calibration.
        Calibration of EyeOne Pro done.
        <BLANKLINE>
        Please put EyeOne-Pro in measurement positionand hit button to start measurement.
        <BLANKLINE>
        Initializing search mode complete.
        >>> final_measurement = man_plot.run() #doctest: +ELLIPSIS
        <BLANKLINE>
        <BLANKLINE>
        Wait until first measurement is done.
        Get to the red cross
        xyY: ...,...,...
        <BLANKLINE>
        <BLANKLINE>
        Manual adjustment of tubes` color
        <BLANKLINE>
        Press [up] for higher intensity or press [down] for lower intensity.
        To set tube color and step size press the following buttons:
        Stepsize:
         [1] - 1
         [2] - 5
         [3] - 10
         [4] - 50
         [5] - 100
        Colortube:
         [r] - Red
         [g] - Green
         [b] - Blue
         [a] - all
        To trigger measurement press [space].
        Press [c] to redraw figure.
        Press [escape] to quit (and save last voltages)
        >>> print(final_measurement) #doctest: +ELLIPSIS
        ([...,...,...], [...,...,...], [...])

    """

    def __init__(self, calibtubes, start_voltages=None, target_color=None):
        """
        :Parameters:

            calibtubes : calibtubes.CalibTubes
                CalibTubes object to change the voltages of the tubes and
                to get access to an eyeone.eyeone.EyeOne instance
            start_voltages : *None* or (vol_r, vol_g, vol_b)
                triple of int containing the start_voltages for the tubes,
                if *None* than the start_voltages has to be assigned before
                method run() is called
            target_color : *None* or (x, y, Y)
                triple of float containing the target color, which was
                measured on the monitor,
                if *None* than the target_color has to be assigned before
                method run() is called

        """
        SetTubesManualBase.__init__(self, calibtubes, start_voltages,
                target_color)
        self.eyeone = calibtubes.eyeone
        self.fig = None
        self.last_vol_xyY_spect = None

        # calibrate EyeOne
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()
        self.tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where EyeOne
                                                       # saves tristim.
        self.spectrum = (c_float * SPECTRUM_SIZE)()    # memory where EyeOne
                                                       # saves spectrum.
        print('\nInitializing search mode complete.')


    def tellme(self, s):
        """
        function to write *s* to the stdout and to the tile of the plot.

        """
        print(s)
        self.plot_xy.set_title(s,fontsize=16)
        plt.draw()

    def run(self):
        """
        Starts program to set tubes by hand.

        Returns the final triple (voltages, xyY, spectrum).

        """
        if not (self.target_color and self.voltages):
            raise ValueError("Please assign target_color and start_voltages"
                    + "before calling run()!")
        self.tub.setVoltages(self.voltages)
        # open file to write data while manual search
        with open('./calibdata/measurements/measure_tubes_manual_' +
                time.strftime("%Y%m%d_%H%M") + '.txt', 'w') as self.calibfile:
            self.calibfile.write("volR, volG, volB, x, y, Y," +
                    ", ".join(["l" + str(x) for x in range(1,37)]) + "\n")

            #set figures
            print('\n\nWait until first measurement is done.')
            self.newFigure()
            print(
            '\n\nManual adjustment of tubes` color\n\n'
            + 'Press [up] for higher intensity '
            + 'or press [down] for lower intensity.\n'
            + 'To set tube color and step size press the following buttons:\n'
            + 'Stepsize:\n'
            + ' [1] - 1\n [2] - 5\n [3] - 10\n [4] - 50\n [5] - 100\n'
            + 'Colortube:\n [r] - Red\n [g] - Green\n [b] - Blue\n [a] - all'
            + '\nTo trigger measurement press [space].'
            + '\nPress [c] to redraw figure.'
            + '\nPress [escape] to quit (and save last voltages)')
            self.stop=False
            while not self.stop:
                plt.waitforbuttonpress()
            # cast all data to python float and deep copy them
            voltages = self.last_vol_xyY_spect[0][:]
            color = [float(x) for x in self.last_vol_xyY_spect[1]]
            spectrum = [float(x) for x in self.last_vol_xyY_spect[2]]
            return( (voltages, color, spectrum) )

    def newFigure(self):
        """
        closes figure and recreates it.

        This is necessary because sometimes the figure hangs and does not
        respond to drawing command.

        """
        if self.fig:
            plt.close(self.fig)
        self.fig = plt.figure(1)
        plt.clf()
        self.plot_xy = plt.subplot(1,2,1)
        self.plot_xy.axis([0.29, 0.31, 0.29, 0.31])
        self.plot_xy.plot(self.target_color[0], self.target_color[1], "rx")
        self.plot_xy.set_aspect(1)
        self.plot_Y = plt.subplot(1,2,2)
        self.plot_Y.axis([0, 10, 19, 23])
        self.plot_Y.axhline(y=self.target_color[2], color="r", xmin=0,
                xmax=1000)
        self.tellme('Get to the red cross')
        self.fig.canvas.mpl_connect('key_press_event', self.onKeyPress)
        # reset self.i
        self.i = 0
        # measure once to draw current point
        self.measureVoltage()


    def measureVoltage(self):
        """
        measures the voltages *each* times.

        TODO this function might be replaced by
        calibtubes.CalibTubes.measureVoltages()

        """
        xyY_list = list()
        self.i += 1
        for i in range(self.each):
            self.tub.setVoltages(self.voltages)
            #print(self.voltages)
            time.sleep(self.imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ."
                        %str(self.voltages))
            if(self.eyeone.I1_GetTriStimulus(self.tri_stim, 0) != eNoError):
                print("Failed to get tristim for voltage %s ."
                        %str(self.voltages))
            if(self.eyeone.I1_GetSpectrum(self.spectrum, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(self.voltages))
            # write data
            self.calibfile.write(", ".join([str(x) for x in self.voltages]) +
                            ", " + ", ".join([str(x) for x in self.tri_stim]) +
                            ", " + ", ".join([str(x) for x in self.spectrum]) +
                            "\n")
            self.calibfile.flush()
            # store measurement for last return (voltages could change,
            # even when you don't measure, so you need a copy here!)
            self.last_vol_xyY_spect = (self.voltages, self.tri_stim,
                    self.spectrum)
            xyY_list.append( self.tri_stim )
        x_mean = np.mean([x[0] for x in xyY_list])
        y_mean = np.mean([x[1] for x in xyY_list])
        Y_mean = np.mean([x[2] for x in xyY_list])
        print("xyY: " + str(x_mean) + "," + str(y_mean) + "," + str(Y_mean))
        self.plot_xy.plot(x_mean, y_mean, "bx")
        self.plot_Y.plot(self.i, Y_mean, "bx")
        plt.draw()

