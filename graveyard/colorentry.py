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

# buried at 2012-05-29 KS
    def measureMonitor(self, monitor, n=10):
        """
        Measures patch_stim_value for certain color n times and overwrites
        self.monitor_xyY with the mean and self.monitor_xyY_sd with the
        standard deviation (1/n*sum((x-mean(x))**2)) of measured values.
        """
        xyY_list = monitor.measurePatchStimColor(self.patch_stim_value, n=n)
        x_list = [xyY[0] for xyY in xyY_list]
        y_list = [xyY[1] for xyY in xyY_list]
        Y_list = [xyY[2] for xyY in xyY_list]
        # calculate mean
        self.monitor_xyY = (sum(x_list)/float(len(x_list)),
                            sum(y_list)/float(len(y_list)),
                            sum(Y_list)/float(len(Y_list)))
        # calculate standard deviaion 1/n * sum((x-mean(x))**2)
        # should we use 1/(n+1) ?? todo
        self.monitor_xyY_sd = (  
                sum([(x-self.monitor_xyY[0])**2 for x in x_list])/float(len(x_list)),
                sum([(y-self.monitor_xyY[1])**2 for y in y_list])/float(len(y_list)),
                sum([(Y-self.monitor_xyY[2])**2 for Y in Y_list])/float(len(Y_list)) )


    def measureTubes(self, tubes, n=10, return_only=False):
        """
        Measures voltages for certain color n times and overwrites
        self.tubes_xyY with the mean and self.tubes_xyY_sd with the
        standard deviation (1/n*sum((x-mean(x))**2)) of measured values.

          * return_only (boolean) -- if return_only is True, function
            does NOT change self.tubes_xyY and self.tubes_xyY_sd. Instead
            it returns a tuple, which contains xyY values and sd values,
            both stored in a tuple of three -- ((x,y,Y),(x_sd,y_sd,Y_sd)).
        """
        if not self.voltages:
            print("No voltages available. Please run findVoltages or set voltages manually.")
            return
        xyY_list = tubes.measureVoltages(self.voltages, n=n)
        x_list = [xyY[0] for xyY in xyY_list]
        y_list = [xyY[1] for xyY in xyY_list]
        Y_list = [xyY[2] for xyY in xyY_list]
        # calculate mean
        if return_only:
            # return tuple (xyY, voltages)
            return((sum(x_list)/float(len(x_list)),
                    sum(y_list)/float(len(y_list)),
                    sum(Y_list)/float(len(Y_list))),
                   (sum([(x-self.tubes_xyY[0])**2 for x in x_list])/float(len(x_list)),
                    sum([(y-self.tubes_xyY[1])**2 for y in y_list])/float(len(y_list)),
                    sum([(Y-self.tubes_xyY[2])**2 for Y in Y_list])/float(len(Y_list)) ) )
        else :
            self.tubes_xyY = ( sum(x_list)/float(len(x_list)),
                               sum(y_list)/float(len(y_list)),
                               sum(Y_list)/float(len(Y_list)) )
            # calculate standard deviaion 1/n * sum((x-mean(x))**2)
            # should we use 1/(n+1) ?? todo
            self.tubes_xyY_sd = (
                    sum([(x-self.tubes_xyY[0])**2 for x in x_list])/float(len(x_list)),
                    sum([(y-self.tubes_xyY[1])**2 for y in y_list])/float(len(y_list)),
                    sum([(Y-self.tubes_xyY[2])**2 for Y in Y_list])/float(len(Y_list)))

   
    def findVoltages(self, tubes):
        """
        Tries to find the right voltages (by calling the tubes.findVoltages
        function) for given monitor_xyY
        coordinates and overwrites self.voltages and self.tubes_xyY.
        """
        if not self.monitor_xyY:
            print("No monitor_xyY color. Please run measureMonitor.")
            return
        (self.voltages, self.tubes_xyY) = tubes.findVoltages(self.monitor_xyY)
        self.tubes_xyY_sd = None

        self.measureTubes(tubes)

    def findVoltagesTuning(self, tubes):
        """
        Fine-tunes voltages towards the target monitor color, by calling
        the tubes.findVoltagesTuning function. 
        """
        if not self.monitor_xyY:
            print("No monitor_xyY color. Please run measureMonitor.")
            return

        (self.voltages, self.tubes_xyY) = tubes.findVoltagesTuning(
                self.monitor_xyY, self.voltages)
        self.tubes_xyY_sd = None

        self.measureTubes(tubes)

