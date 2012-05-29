#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# calibtubes.py
#
# (c) 2012 Konstantin Sering <konstantin.sering [aet] gmail.com>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content:
#
# input: --
# output: --
#
# created 2012-05-29 KS
# last mod 2012-05-29 KS


# buried at 2012-05-29 KS
    # returns (voltages, (x,y,Y))
    def findVoltages(self, color):
        """
        findVoltages tries to find voltages for a given color (as tuple) in
        xyY color space, by using the iterativeColorMatch algorithm of the
        IterativeColorTubes Class.
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltages color: " + str(color))
        (voltages, xyY) = self.ict.iterativeColorMatch(
                color, epsilon=0.01, dilation=1.0, imi=0.5, max_iterations=50)
        return (voltages, xyY)

    def findVoltagesTuning(self, target_color, start_voltages=None):
        """
        findVoltagesTuning tries to find voltages for a given color
        in xyY color space, by using the iterativeColorMatch2 algorithm of the
        IterativeColorTubes Class.
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltagesTuning color: " + str(target_color))
        return self.ict.iterativeColorMatch2(
                target_color, start_voltages=start_voltages,
                iterations=50, stepsize=10, imi=0.5)
        

# buried at 2012-05-29 KS

    def setColor(self, xyY):
        """
        setColor sets the color of the tubes to given xyY values.

        * xyY is a tuple of floats (x,y,Y)
        """
        # set wasco card to correct voltage
        self.setVoltages( self.xyYtoU(xyY) )

    def xyYtoU(self, xyY):
        """
        Calculates a smart guess for corresponding voltages for a given xyY
        color (as tuple).
        """
        xyY = (xyY[0], xyY[1], xyY[2])
        rgb = xyY2rgb(xyY)
        return( (self._sRGBtoU_r(rgb[0]), 
                 self._sRGBtoU_g(rgb[1]),
                 self._sRGBtoU_b(rgb[2])) )

    def _sRGBtoU_r(self, red_sRGB):
        x = float(red_sRGB)
        if x >= self.red_p1:
            print("red channel is on maximum")
            return self.high_threshold
        U_r = (-log((x - self.red_p1)/(self.red_p2 - self.red_p1)) / 
                exp(self.red_p3))
        if U_r < self.low_threshold:
            print("red channel is on minimum")
            return self.low_threshold
        if U_r > self.high_threshold:
            print("red channel is on maximum")
            return self.high_threshold
        return int(U_r)

    def _sRGBtoU_g(self, green_sRGB):
        x = float(green_sRGB)
        if x >= self.green_p1:
            print("green channel is on maximum")
            return self.high_threshold
        U_g = (-log((x - self.green_p1)/(self.green_p2 - self.green_p1)) / 
                exp(self.green_p3))
        if U_g < self.low_threshold:
            print("green channel is on minimum")
            return self.low_threshold
        if U_g > self.high_threshold:
            print("green channel is on maximum")
            return self.high_threshold
        return int(U_g)

    def _sRGBtoU_b(self, blue_sRGB):
        x = float(blue_sRGB)
        if x >= self.blue_p1:
            print("blue channel is on maximum")
            return self.high_threshold
        U_b = (-log((x - self.blue_p1)/(self.blue_p2 - self.blue_p1)) / 
                exp(self.blue_p3))
        if U_b < self.low_threshold:
            print("blue channel is on minimum")
            return self.low_threshold
        if U_b > self.high_threshold:
            print("blue channel is on maximum")
            return self.high_threshold
        return int(U_b)


