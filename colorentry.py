#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colorentry.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-11-02, KS

class ColorEntry(object):
    """
    ColorEntry contains all information for one color that we need in the
    lab.

    It contains:
      * a name
      * the corresponding value for psychopy.PatchStim
      * measured xyY values for the monitor
      * standard deviation for the xyY values
      * the corresponding voltages for the color tubes
      * measured xyY values for the tubes
      * standard deviation for the xyY values
    """

    def __init__(self, name, patch_stim_value=None, voltages=None)
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
    
    def findVoltages(self, tubes):
        """
        Try to find the right voltages for given monitor_xyY coordinates
        and overwrites self.voltages and self.tubes_xyY.
        """
        if not self.monitor_xyY:
            print("No monitor_xyY color. Please run measureMonitor.")
            return
        self.voltages = findVoltages(tubes, self.monitor_xyY)

        self.measureTubes(tubes)


    def measureMonitor(self, monitor, n=10):
        """
        Measures the patch_stim_value color n times and overwrites
        slef.monitor_xyY with the mean and self.monitor_xyY_sd with the
        standard deviation (1/n*sum((x-mean(x))**2)) of the measured values.
        """
        xyY_list = monitor.measurePatchStimColor(self.patch_stim_color, n=n)
        x_list = [xyY[0] for xyY in xyY_list]
        y_list = [xyY[1] for xyY in xyY_list]
        Y_list = [xyY[2] for xyY in xyY_list]
        # calculate mean
        self.monitor_xyY = ( sum(x_list)/float(len(x_list)),
                             sum(y_list)/float(len(y_list)),
                             sum(Y_list)/float(len(Y_list)) )
        # calculate standard deviaion 1/n * sum((x-mean(x))**2)
        # should we use 1/(n+1) ?? todo
        self.monitor_xyY_sd = ( 
                sum([(x-self.monitor_xyY[0])**2 for x in x_list])/float(len(x_list))
                sum([(y-self.monitor_xyY[1])**2 for y in y_list])/float(len(y_list))
                sum([(Y-self.monitor_xyY[2])**2 for Y in Y_list])/float(len(Y_list)) )


    def measureTubes(self, tubes, n=10):
        """
        Measures the voltages color n times and overwrites
        self.tubes_xyY with the mean and self.tubes_xyY_sd with the
        standard deviation (1/n*sum((x-mean(x))**2)) of the measured values.
        """
        xyY_list = tubes.measureVoltage(self.voltages, n=n)
        x_list = [xyY[0] for xyY in xyY_list]
        y_list = [xyY[1] for xyY in xyY_list]
        Y_list = [xyY[2] for xyY in xyY_list]
        # calculate mean
        self.tubes_xyY = ( sum(x_list)/float(len(x_list)),
                             sum(y_list)/float(len(y_list)),
                             sum(Y_list)/float(len(Y_list)) )
        # calculate standard deviaion 1/n * sum((x-mean(x))**2)
        # should we use 1/(n+1) ?? todo
        self.tubes_xyY_sd = ( 
                sum([(x-self.tubes_xyY[0])**2 for x in x_list])/float(len(x_list))
                sum([(y-self.tubes_xyY[1])**2 for y in y_list])/float(len(y_list))
                sum([(Y-self.tubes_xyY[2])**2 for Y in Y_list])/float(len(Y_list)) )


