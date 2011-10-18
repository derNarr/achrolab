#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./devtubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and
# Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-10-14 DW

from wasco.wasco import Wasco
from wasco.WascoConstants import DAOUT1_16, DAOUT2_16, DAOUT3_16
import time


class DevTubes(object):
    """
    DevTubes encapsulates all functions controlling fluorescent tubes in the
    booth. It provides all low level functionality.
    """
    def __init__(self):
        """Setting some "global" variables.
        
        If dummy=True no wasco runtimelibraries will be loaded.
        """

        self.wascocard = Wasco()    # create wasco object
        self.wasco_boardId = self.wascocard.boardId 

        self.red_out = DAOUT3_16
        self.green_out = DAOUT1_16
        self.blue_out = DAOUT2_16
        self.low_threshold = 0x400 # min voltages must be integer
        self.high_threshold = 0xFFF # max voltages must be integer


        # set default values for the sRGBtoU transformation function
        self.red_p1 =   278.03951766
        self.red_p2 =  -139.315857925
        self.red_p3 =    -6.59992420598      
        self.green_p1 = 272.879675867
        self.green_p2 = -97.9412320578
        self.green_p3 =  -6.84536739156 
        self.blue_p1 =  263.734050868
        self.blue_p2 = -187.047396719
        self.blue_p3 =   -6.45686046205

        # voltage wich is set at the moment
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
        if U_r_new < self.low_threshold:
            print("red channel is on minimum (" + str(self.low_threshold) +")")
            U_r_new = self.low_threshold
        if U_r_new > self.high_threshold:
            print("red channel is on maximum (" + str(self.high_threshold)
                    +")")
            U_r_new = self.high_threshold
        if U_g_new < self.low_threshold:
            print("green channel is on minimum (" + str(self.low_threshold)
            +")")
            U_g_new = self.low_threshold
        if U_g_new > self.high_threshold:
            print("green channel is on maximum (" + str(self.high_threshold)
                    +")")
            U_g_new = self.high_threshold
        if U_b_new < self.low_threshold:
            print("blue channel is on minimum (" + str(self.low_threshold)
                    +")")
            U_b_new = self.low_threshold
        if U_b_new > self.high_threshold:
            print("blue channel is on maximum (" + str(self.high_threshold)
                    +")")
            U_b_new = self.high_threshold

        diff_r = U_r_new - self.U_r
        diff_g = U_g_new - self.U_g
        diff_b = U_b_new - self.U_b

        steps = max( abs(diff_r), abs(diff_g), abs(diff_b))

        if steps == 0:
            return

        slope_r = diff_r/float(steps)
        slope_g = diff_g/float(steps)
        slope_b = diff_b/float(steps)

        for i in range(steps):
            time.sleep(0.001)
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

