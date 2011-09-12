<<<<<<< HEAD
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./devtubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and
# Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-05-31, KS

from wasco.wasco import wasco, boardId
from wasco.WascoConstants import DAOUT1_16, DAOUT2_16, DAOUT3_16

from eyeone.EyeOne import EyeOne
from eyeone.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_RGB,
                                    TRISTIMULUS_SIZE)

from math import exp,log

from colormath.color_objects import xyYColor

import rpy2.robjects as robjects

import time,pickle

from ctypes import c_float


# want to run R-commands with R("command")
R = robjects.r


class Tubes(object):
    """The class Tubes encapsulates all functions controlling the light
    tubes in the box. It provides all the low level functionality."""
    def __init__(self, eyeone, dummy=False):
        """Setting some "global" variables and store eyeone object.
        
        If dummy=True no wasco runtimelibraries will be loaded."""
        self.dummy = dummy

        self.wascocard = wasco
        self.wasco_boardId = boardId 

        self.red_out = DAOUT3_16
        self.green_out = DAOUT1_16
        self.blue_out = DAOUT2_16
        self.low_threshold = 0x400 # min voltages must be integer
        self.high_threshold = 0xFFF # max voltages must be integer

        self.IsCalibrated = False

        # EyeOne Pro
        self.eyeone = eyeone

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


    def setColor(self, xyY):
        """setColor sets the color of the tubes to the given xyY values.
        * xyY is a tuple of floats (x,y,Y)"""
        #set the wasco-card to the right voltage
        self.setVoltages( self.xyYtoU(xyY) )

    def calibrate(self, imi=0.5):
        """calibrate calibrates the tubes with the EyeOne Pro. The EyeOne
        Pro should be connected to the computer. The calibration takes
        around 2 minutes.
        * imi -- is the inter measurement interval in seconds."""
        # TODO generate logfile for every calibration

        # set EyeOne Pro variables
        if(self.eyeone.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("Measurement mode set to single emission.")
        else:
            print("Failed to set measurement mode.")
            return
        if(self.eyeone.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_RGB) ==
                eNoError):
            print("Color space set to RGB.")
        else:
            print("Failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put EyeOne Pro on calibration plate and "
        + "press key to start calibration.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eyeone.I1_Calibrate() == eNoError):
            print("Calibration of EyeOne Pro done.")
        else:
            print("Calibration of EyeOne Pro failed. Please RESTART"
            + " calibration of tubes.")
            return
        
        ## Measurement
        print("\nPlease put EyeOne Pro in measurement position and "
        + "press key to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")

        # define some variables
        # generating the tested voltages (r, g, b)
        voltages = list()
        for i in range(50):
            voltages.append( ((0x400 + 61 * i), 0x0, 0x0) )
        for i in range(50):
            voltages.append( (0x0, (0x400 + 61 * i), 0x0) )
        for i in range(50):
            voltages.append( (0x0, 0x0, (0x400 + 61 * i)) )

        tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where the EyeOne
                                            # Pro saves the tristim.
        rgb_list = list()
        
        for voltage in voltages:
            self.setVoltages(voltage)
            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ." %str(voltage))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(voltage))
            rgb_list.append(list(tri_stim))
        
        print("Measurement finished.")
        self.setVoltages( (0x0, 0x0, 0x0) ) # to signal that the
                                           # measurement is over
        
        # get python objects into R -- maybe there is a better way TODO
        voltage_r = robjects.IntVector([x[0] for x in voltages])
        voltage_g = robjects.IntVector([x[1] for x in voltages])
        voltage_b = robjects.IntVector([x[2] for x in voltages])
        rgb_r = robjects.FloatVector([x[0] for x in rgb_list])
        rgb_g = robjects.FloatVector([x[1] for x in rgb_list])
        rgb_b = robjects.FloatVector([x[2] for x in rgb_list])
        
        R("voltage_r <- " + voltage_r.r_repr())
        R("voltage_g <- " + voltage_g.r_repr())
        R("voltage_b <- " + voltage_b.r_repr())
        R("rgb_r <- " + rgb_r.r_repr())
        R("rgb_g <- " + rgb_g.r_repr())
        R("rgb_b <- " + rgb_b.r_repr())
        
        print("Data read into R")

        ## fit a gamma function (using nls() in R) -- formula based on
        ## PXlab manual:
        ## y(x) = (ax + s)^gamma (cf. Brainard et al. (2002), gamma.pdf)
        
        try:
            ## red channel
            R('''
            len3 <- floor(length(voltage_r)/3)
            idr <- rgb_r >= 10 #only use rgb values greater 10 
            idr[-(2:len3)] = FALSE # area measured the red values
            rgb_r_small <- rgb_r[idr]
            voltage_r_small <- voltage_r[idr]
            nls_r <- nls(rgb_r_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_r_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_r <- nls(rgb_r_small ~ p1 + p2*voltage_r_small,
            #             start=c(p1=0, p2=1))
            ''')
            ## green channel
            R('''
            idg <- rgb_g >= 10 #only use rgb values greater 10
            idg[-((len3+1):(2*len3))] = FALSE # area measured the green values
            rgb_g_small <- rgb_g[idg]
            voltage_g_small <- voltage_g[idg]
            nls_g <- nls(rgb_g_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_g_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_g <- nls(rgb_g_small ~ p1 + p2*voltage_g_small,
            #             start=c(p1=0, p2=1))
            ''')
            ## blue channel
            R('''
            idb <- rgb_b >= 10 #only use rgb values greater 10
            idb[-((2*len3+1):(3*len3))] = FALSE # area measured the blue values
            rgb_b_small <- rgb_b[idb]
            voltage_b_small <- voltage_b[idb]
            nls_b <- nls(rgb_b_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_b_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_b <- nls(rgb_b_small ~ p1 + p2*voltage_b_small,
            #             start=c(p1=0, p2=1))
            ''')
            
            print("Parameters estimated.")
        except:
            print("Failed to estimate parameters, saved data anyway.")
            # save all created R objects to the file calibration_tubes.RData
            R('save(list=ls(), file="calibdata/calibration/calibration_tubes' + 
                    time.strftime("%Y%m%d_%H%M") + '.RData")')
            return

        # extract estimated parameters in R to make them easier available
        # in python
        R('''
        p_r <- coef(nls_r)
        p_g <- coef(nls_g)
        p_b <- coef(nls_b)
        ''')
        
        # save all created R objects to the file calibration_tubes.RData
        R('save(list=ls(), file="calibdata/calibration/calibration_tubes' + 
                time.strftime("%Y%m%d_%H%M") + '.RData")')

        # save the estimated parameters to the tube object
        self.red_p1 = R['p_r'][0]
        self.red_p2 = R['p_r'][1]
        self.red_p3 = R['p_r'][2]
        self.green_p1 = R['p_g'][0]
        self.green_p2 = R['p_g'][1]
        self.green_p3 = R['p_g'][2]
        self.blue_p1 = R['p_b'][0]
        self.blue_p2 = R['p_b'][1]
        self.blue_p3 = R['p_b'][2]

        print("red_p1" + str(self.red_p1)) 
        print("red_p2" + str(self.red_p2)) 
        print("red_p3" + str(self.red_p3))
        print("green_p1" + str(self.green_p1))
        print("green_p2" + str(self.green_p2))
        print("green_p3" + str(self.green_p3))
        print("blue_p1" + str(self.blue_p1))
        print("blue_p2" + str(self.blue_p2))
        print("blue_p3" + str(self.blue_p3))
        
        # finished calibration :)
        self.IsCalibrated = True
        print("Calibration of tubes finished.")

    #def _sRGBtoU_r(self, red_sRGB):
    #    x = float(red_sRGB)
    #    return ((x - self.red_p1)/self.red_p2)

    #def _sRGBtoU_g(self, green_sRGB):
    #    x = float(green_sRGB)
    #    return ((x - self.green_p1)/self.green_p2)

    #def _sRGBtoU_b(self, blue_sRGB):
    #    x = float(blue_sRGB)
    #    return ((x - self.blue_p1)/self.blue_p2)

    # returns tuple

    def xyYtoU(self, xyY):
        """
        Calculates a smart guess for the corresponding voltages for a
        given xyY color (as tuple).
        ATTENTION at the moment this function maybe gives wrong values!!!
        """
        # TODO remove xyYColor from code, by calibrating tubes with a
        # coordinate transformation voltages <-> xyY
        # ATTENTION at the moment this function maybe gives wrong values!!!
        xyY = xyYColor(xyY[0], xyY[1], xyY[2])
        rgb = xyY.convert_to("rgb", target_rgb="sRGB", clip=False)
        return( (self._sRGBtoU_r(rgb.rgb_r), 
                 self._sRGBtoU_g(rgb.rgb_g),
                 self._sRGBtoU_b(rgb.rgb_b)) )

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

    def setVoltage(self, U_rgb):
        """DEPRECATED version. Please use setVoltages (with s in the
        end)."""
        print("DEPRECATED -- use devtubes.Tubes.setVoltages instead")
        return self.setVoltages(U_rgb)

    def setVoltages(self, U_rgb):
        """setVoltage set the voltage in the list or tuple of U_rgb to the 
        wasco card.
        U_rgb should contain three integers between self.low_threshold and 
        self.high_threshold."""
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

    def saveParameter(self, filename="./lastParameterTubes.pkl"):
        """Saves the for the interpolation function used parameter."""
        # TODO what to do, if file don't exists? Throw exception?
        f = open(filename, 'wb')
        pickle.dump(self.red_p1, f)
        pickle.dump(self.red_p2, f)
        pickle.dump(self.red_p3, f)
        pickle.dump(self.green_p1, f)
        pickle.dump(self.green_p2, f)
        pickle.dump(self.green_p3, f)
        pickle.dump(self.blue_p1, f)
        pickle.dump(self.blue_p2, f)
        pickle.dump(self.blue_p3, f)
        f.close()

    def loadParameter(self, filename="./lastParamterTubes.pkl"):
        """Loads the for the interpolation function used parameter."""
        # TODO warn if a file get replaced?
        f = open(filename, 'rb')
        self.red_p1   = pickle.load(f)
        self.red_p2   = pickle.load(f)
        self.red_p3   = pickle.load(f)
        self.green_p1 = pickle.load(f)
        self.green_p2 = pickle.load(f)
        self.green_p3 = pickle.load(f)
        self.blue_p1  = pickle.load(f)
        self.blue_p2  = pickle.load(f)
        self.blue_p3  = pickle.load(f)
        f.close()


    def plotCalibration(self):
        """plotCalibration plots the in the calibration"""
        if(not self.IsCalibrated):
            return
        # the in this R code used variables are created in calibrate()
        # idr, idg, idb, voltage_r, voltage_g,
        # voltage_b, rgb_r, rgb_g, rgb_b, p_r, p_g, p_b

        # plot calibration curves and data points for each channel
        R('pdf("calibdata/calibration/calibration_curves_rgb_tubes'+time.strftime("%Y%m%d_%H%M")
            +'.pdf", width=9, height=8)')

        R('''
        par(mfrow=c(3,3))
        len3 <- floor(length(voltage_r)/3)
        # only red voltage
        plot(voltage_r[1:len3], rgb_r[1:len3], col="red", ylim=c(0,256),
            pch=19,
            main="red channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="red rgb-value")
        points(voltage_r[1:len3], rgb_g[1:len3], pch=21, col="green")
        points(voltage_r[1:len3], rgb_b[1:len3], pch=21, col="blue")
        #curve(p_r[1] + p_r[2]*x, col="red", add=T, xlab="", ylab="")
        curve(p_r[1] + (p_r[2] - p_r[1])*exp(-exp(p_r[3])*x), col="red",
            add=T, xlab="", ylab="")
        
        # only green voltage
        plot(voltage_g[(len3+1):(2*len3)], rgb_g[(len3+1):(2*len3)], 
            col="green", ylim=c(0,256), pch=19,
            main="green channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="green rgb-value")
        points(voltage_g[(len3+1):(2*len3)], rgb_r[(len3+1):(2*len3)], pch=21,
              col="red")
        points(voltage_g[(len3+1):(2*len3)], rgb_b[(len3+1):(2*len3)], pch=21,
              col="blue")
        #curve(p_g[1] + p_g[2]*x, col="green", add=T, xlab="", ylab="")
        curve(p_g[1] + (p_g[2] - p_g[1])*exp(-exp(p_g[3])*x), col="green",
            add=T, xlab="", ylab="")
        
        # only blue voltage
        plot(voltage_b[(2*len3+1):(3*len3)], rgb_b[(2*len3+1):(3*len3)],
            col="blue", ylim=c(0,256), pch=19,
            main="blue channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="blue rgb-value")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_g[(2*len3+1):(3*len3)], 
            pch=21, col="green")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_r[(2*len3+1):(3*len3)], 
            pch=21, col="red")
        #curve(p_b[1] + p_b[2]*x, col="blue", add=T, xlab="", ylab="")
        curve(p_b[1] + (p_b[2] - p_b[1])*exp(-exp(p_b[3])*x), col="blue",
            add=T, xlab="", ylab="")
        
        # residual plots free y-scale
        #pred_r <- p_r[1] + p_r[2]*voltage_r
        #pred_g <- p_g[1] + p_g[2]*voltage_g
        #pred_b <- p_b[1] + p_b[2]*voltage_b

        pred_r <- p_r[1] + (p_r[2] - p_r[1])*exp(-exp(p_r[3])*voltage_r)
        pred_g <- p_g[1] + (p_g[2] - p_g[1])*exp(-exp(p_g[3])*voltage_g)
        pred_b <- p_b[1] + (p_b[2] - p_b[1])*exp(-exp(p_b[3])*voltage_b)

        resid_r <- rgb_r - pred_r
        resid_g <- rgb_g - pred_g
        resid_b <- rgb_b - pred_b

        plot(voltage_r[1:len3], resid_r[1:len3], pch=19, col="red",
            type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        
        # residual plots fixed y-scale
        plot(voltage_r[1:len3], resid_r[1:len3], pch=19, col="red",
            ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)

        dev.off()
        ''')


if(__name__=="__main__"):
    eyeone = EyeOne()
    tubes = Tubes(eyeone)
    tubes.calibrate(imi=1.0)

    tubes.saveParameter()
    filename="./calibdata/calibration/parameterTubes"+time.strftime("%Y%m%d_%H%M")+".pkl"
    tubes.saveParameter(filename)
    
    tubes.plotCalibration()


    #farbe = (0.5, 0.5, 1.0)
    #tubes.setColor(farbe)
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.8) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.5) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.3) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.1) )

=======
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./devtubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and
# Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-05-31, KS

from wasco.wasco import wasco, boardId
from wasco.WascoConstants import DAOUT1_16, DAOUT2_16, DAOUT3_16

from eyeone.EyeOne import EyeOne
from eyeone.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_RGB,
                                    TRISTIMULUS_SIZE)

from math import exp,log

from colormath.color_objects import xyYColor

import rpy2.robjects as robjects

import time,pickle

from ctypes import c_float


# want to run R-commands with R("command")
R = robjects.r


class Tubes(object):
    """The class Tubes encapsulates all functions controlling the light
    tubes in the box. It provides all the low level functionality."""
    def __init__(self, eyeone, dummy=False):
        """Setting some "global" variables and store eyeone object.
        
        If dummy=True no wasco runtimelibraries will be loaded."""
        self.dummy = dummy

        self.wascocard = wasco
        self.wasco_boardId = boardId 

        self.red_out = DAOUT3_16
        self.green_out = DAOUT1_16
        self.blue_out = DAOUT2_16
        self.low_threshold = 0x400 # min voltages must be integer
        self.high_threshold = 0xFFF # max voltages must be integer

        self.IsCalibrated = False

        # EyeOne Pro
        self.eyeone = eyeone

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


    def setColor(self, xyY):
        """setColor sets the color of the tubes to the given xyY values.
        * xyY is a tuple of floats (x,y,Y)"""
        #set the wasco-card to the right voltage
        self.setVoltages( self.xyYtoU(xyY) )

    def calibrate(self, imi=0.5):
        """calibrate calibrates the tubes with the EyeOne Pro. The EyeOne
        Pro should be connected to the computer. The calibration takes
        around 2 minutes.
        * imi -- is the inter measurement interval in seconds."""
        # TODO generate logfile for every calibration

        # set EyeOne Pro variables
        if(self.eyeone.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("Measurement mode set to single emission.")
        else:
            print("Failed to set measurement mode.")
            return
        if(self.eyeone.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_RGB) ==
                eNoError):
            print("Color space set to RGB.")
        else:
            print("Failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put EyeOne Pro on calibration plate and "
        + "press key to start calibration.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eyeone.I1_Calibrate() == eNoError):
            print("Calibration of EyeOne Pro done.")
        else:
            print("Calibration of EyeOne Pro failed. Please RESTART"
            + " calibration of tubes.")
            return
        
        ## Measurement
        print("\nPlease put EyeOne Pro in measurement position and "
        + "press key to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")

        # define some variables
        # generating the tested voltages (r, g, b)
        voltages = list()
        for i in range(50):
            voltages.append( ((0x400 + 61 * i), 0x0, 0x0) )
        for i in range(50):
            voltages.append( (0x0, (0x400 + 61 * i), 0x0) )
        for i in range(50):
            voltages.append( (0x0, 0x0, (0x400 + 61 * i)) )

        tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where the EyeOne
                                            # Pro saves the tristim.
        rgb_list = list()
        
        for voltage in voltages:
            self.setVoltages(voltage)
            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ." %str(voltage))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(voltage))
            rgb_list.append(list(tri_stim))
        
        print("Measurement finished.")
        self.setVoltages( (0x0, 0x0, 0x0) ) # to signal that the
                                           # measurement is over
        
        # get python objects into R -- maybe there is a better way TODO
        voltage_r = robjects.IntVector([x[0] for x in voltages])
        voltage_g = robjects.IntVector([x[1] for x in voltages])
        voltage_b = robjects.IntVector([x[2] for x in voltages])
        rgb_r = robjects.FloatVector([x[0] for x in rgb_list])
        rgb_g = robjects.FloatVector([x[1] for x in rgb_list])
        rgb_b = robjects.FloatVector([x[2] for x in rgb_list])
        
        R("voltage_r <- " + voltage_r.r_repr())
        R("voltage_g <- " + voltage_g.r_repr())
        R("voltage_b <- " + voltage_b.r_repr())
        R("rgb_r <- " + rgb_r.r_repr())
        R("rgb_g <- " + rgb_g.r_repr())
        R("rgb_b <- " + rgb_b.r_repr())
        
        print("Data read into R")

        ## fit a gamma function (using nls() in R) -- formula based on
        ## PXlab manual:
        ## y(x) = (ax + s)^gamma (cf. Brainard et al. (2002), gamma.pdf)
        
        try:
            ## red channel
            R('''
            len3 <- floor(length(voltage_r)/3)
            idr <- rgb_r >= 10 #only use rgb values greater 10 
            idr[-(2:len3)] = FALSE # area measured the red values
            rgb_r_small <- rgb_r[idr]
            voltage_r_small <- voltage_r[idr]
            nls_r <- nls(rgb_r_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_r_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_r <- nls(rgb_r_small ~ p1 + p2*voltage_r_small,
            #             start=c(p1=0, p2=1))
            ''')
            ## green channel
            R('''
            idg <- rgb_g >= 10 #only use rgb values greater 10
            idg[-((len3+1):(2*len3))] = FALSE # area measured the green values
            rgb_g_small <- rgb_g[idg]
            voltage_g_small <- voltage_g[idg]
            nls_g <- nls(rgb_g_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_g_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_g <- nls(rgb_g_small ~ p1 + p2*voltage_g_small,
            #             start=c(p1=0, p2=1))
            ''')
            ## blue channel
            R('''
            idb <- rgb_b >= 10 #only use rgb values greater 10
            idb[-((2*len3+1):(3*len3))] = FALSE # area measured the blue values
            rgb_b_small <- rgb_b[idb]
            voltage_b_small <- voltage_b[idb]
            nls_b <- nls(rgb_b_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_b_small),
                         start=c(p1=1000, p2=-100, p3=-7))
            #nls_b <- nls(rgb_b_small ~ p1 + p2*voltage_b_small,
            #             start=c(p1=0, p2=1))
            ''')
            
            print("Parameters estimated.")
        except:
            print("Failed to estimate parameters, saved data anyway.")
            # save all created R objects to the file calibration_tubes.RData
            R('save(list=ls(), file="calibdata/calibration/calibration_tubes' + 
                    time.strftime("%Y%m%d_%H%M") + '.RData")')
            return

        # extract estimated parameters in R to make them easier available
        # in python
        R('''
        p_r <- coef(nls_r)
        p_g <- coef(nls_g)
        p_b <- coef(nls_b)
        ''')
        
        # save all created R objects to the file calibration_tubes.RData
        R('save(list=ls(), file="calibdata/calibration/calibration_tubes' + 
                time.strftime("%Y%m%d_%H%M") + '.RData")')

        # save the estimated parameters to the tube object
        self.red_p1 = R['p_r'][0]
        self.red_p2 = R['p_r'][1]
        self.red_p3 = R['p_r'][2]
        self.green_p1 = R['p_g'][0]
        self.green_p2 = R['p_g'][1]
        self.green_p3 = R['p_g'][2]
        self.blue_p1 = R['p_b'][0]
        self.blue_p2 = R['p_b'][1]
        self.blue_p3 = R['p_b'][2]

        print("red_p1" + str(self.red_p1)) 
        print("red_p2" + str(self.red_p2)) 
        print("red_p3" + str(self.red_p3))
        print("green_p1" + str(self.green_p1))
        print("green_p2" + str(self.green_p2))
        print("green_p3" + str(self.green_p3))
        print("blue_p1" + str(self.blue_p1))
        print("blue_p2" + str(self.blue_p2))
        print("blue_p3" + str(self.blue_p3))
        
        # finished calibration :)
        self.IsCalibrated = True
        print("Calibration of tubes finished.")

    #def _sRGBtoU_r(self, red_sRGB):
    #    x = float(red_sRGB)
    #    return ((x - self.red_p1)/self.red_p2)

    #def _sRGBtoU_g(self, green_sRGB):
    #    x = float(green_sRGB)
    #    return ((x - self.green_p1)/self.green_p2)

    #def _sRGBtoU_b(self, blue_sRGB):
    #    x = float(blue_sRGB)
    #    return ((x - self.blue_p1)/self.blue_p2)

    # returns tuple

    def xyYtoU(self, xyY):
        """
        Calculates a smart guess for the corresponding voltages for a
        given xyY color (as tuple).
        ATTENTION at the moment this function maybe gives wrong values!!!
        """
        # TODO remove xyYColor from code, by calibrating tubes with a
        # coordinate transformation voltages <-> xyY
        # ATTENTION at the moment this function maybe gives wrong values!!!
        xyY = xyYColor(xyY[0], xyY[1], xyY[2])
        rgb = xyY.convert_to("rgb", target_rgb="sRGB", clip=False)
        return( (self._sRGBtoU_r(rgb.rgb_r), 
                 self._sRGBtoU_g(rgb.rgb_g),
                 self._sRGBtoU_b(rgb.rgb_b)) )

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

    def setVoltage(self, U_rgb):
        """DEPRECATED version. Please use setVoltages (with s in the
        end)."""
        print("DEPRECATED -- use devtubes.Tubes.setVoltages instead")
        return self.setVoltages(U_rgb)

    def setVoltages(self, U_rgb):
        """setVoltage set the voltage in the list or tuple of U_rgb to the 
        wasco card.
        U_rgb should contain three integers between self.low_threshold and 
        self.high_threshold."""
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

    def saveParameter(self, filename="./lastParameterTubes.pkl"):
        """Saves the for the interpolation function used parameter."""
        # TODO what to do, if file don't exists? Throw exception?
        f = open(filename, 'wb')
        pickle.dump(self.red_p1, f)
        pickle.dump(self.red_p2, f)
        pickle.dump(self.red_p3, f)
        pickle.dump(self.green_p1, f)
        pickle.dump(self.green_p2, f)
        pickle.dump(self.green_p3, f)
        pickle.dump(self.blue_p1, f)
        pickle.dump(self.blue_p2, f)
        pickle.dump(self.blue_p3, f)
        f.close()

    def loadParameter(self, filename="./lastParamterTubes.pkl"):
        """Loads the for the interpolation function used parameter."""
        # TODO warn if a file get replaced?
        f = open(filename, 'rb')
        self.red_p1   = pickle.load(f)
        self.red_p2   = pickle.load(f)
        self.red_p3   = pickle.load(f)
        self.green_p1 = pickle.load(f)
        self.green_p2 = pickle.load(f)
        self.green_p3 = pickle.load(f)
        self.blue_p1  = pickle.load(f)
        self.blue_p2  = pickle.load(f)
        self.blue_p3  = pickle.load(f)
        f.close()


    def plotCalibration(self):
        """plotCalibration plots the in the calibration"""
        if(not self.IsCalibrated):
            return
        # the in this R code used variables are created in calibrate()
        # idr, idg, idb, voltage_r, voltage_g,
        # voltage_b, rgb_r, rgb_g, rgb_b, p_r, p_g, p_b

        # plot calibration curves and data points for each channel
        R('pdf("calibdata/calibration/calibration_curves_rgb_tubes'+time.strftime("%Y%m%d_%H%M")
            +'.pdf", width=9, height=8)')

        R('''
        par(mfrow=c(3,3))
        len3 <- floor(length(voltage_r)/3)
        # only red voltage
        plot(voltage_r[1:len3], rgb_r[1:len3], col="red", ylim=c(0,256),
            pch=19,
            main="red channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="red rgb-value")
        points(voltage_r[1:len3], rgb_g[1:len3], pch=21, col="green")
        points(voltage_r[1:len3], rgb_b[1:len3], pch=21, col="blue")
        #curve(p_r[1] + p_r[2]*x, col="red", add=T, xlab="", ylab="")
        curve(p_r[1] + (p_r[2] - p_r[1])*exp(-exp(p_r[3])*x), col="red",
            add=T, xlab="", ylab="")
        
        # only green voltage
        plot(voltage_g[(len3+1):(2*len3)], rgb_g[(len3+1):(2*len3)], 
            col="green", ylim=c(0,256), pch=19,
            main="green channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="green rgb-value")
        points(voltage_g[(len3+1):(2*len3)], rgb_r[(len3+1):(2*len3)], pch=21,
              col="red")
        points(voltage_g[(len3+1):(2*len3)], rgb_b[(len3+1):(2*len3)], pch=21,
              col="blue")
        #curve(p_g[1] + p_g[2]*x, col="green", add=T, xlab="", ylab="")
        curve(p_g[1] + (p_g[2] - p_g[1])*exp(-exp(p_g[3])*x), col="green",
            add=T, xlab="", ylab="")
        
        # only blue voltage
        plot(voltage_b[(2*len3+1):(3*len3)], rgb_b[(2*len3+1):(3*len3)],
            col="blue", ylim=c(0,256), pch=19,
            main="blue channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="blue rgb-value")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_g[(2*len3+1):(3*len3)], 
            pch=21, col="green")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_r[(2*len3+1):(3*len3)], 
            pch=21, col="red")
        #curve(p_b[1] + p_b[2]*x, col="blue", add=T, xlab="", ylab="")
        curve(p_b[1] + (p_b[2] - p_b[1])*exp(-exp(p_b[3])*x), col="blue",
            add=T, xlab="", ylab="")
        
        # residual plots free y-scale
        #pred_r <- p_r[1] + p_r[2]*voltage_r
        #pred_g <- p_g[1] + p_g[2]*voltage_g
        #pred_b <- p_b[1] + p_b[2]*voltage_b

        pred_r <- p_r[1] + (p_r[2] - p_r[1])*exp(-exp(p_r[3])*voltage_r)
        pred_g <- p_g[1] + (p_g[2] - p_g[1])*exp(-exp(p_g[3])*voltage_g)
        pred_b <- p_b[1] + (p_b[2] - p_b[1])*exp(-exp(p_b[3])*voltage_b)

        resid_r <- rgb_r - pred_r
        resid_g <- rgb_g - pred_g
        resid_b <- rgb_b - pred_b

        plot(voltage_r[1:len3], resid_r[1:len3], pch=19, col="red",
            type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", type="h",
            main="residuals (free y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        
        # residual plots fixed y-scale
        plot(voltage_r[1:len3], resid_r[1:len3], pch=19, col="red",
            ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", ylim=c(-10,10), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)

        dev.off()
        ''')


if(__name__=="__main__"):
    eyeone = EyeOne()
    tubes = Tubes(eyeone)
    tubes.calibrate(imi=1.0)

    tubes.saveParameter()
    filename="./calibdata/calibration/parameterTubes"+time.strftime("%Y%m%d_%H%M")+".pkl"
    tubes.saveParameter(filename)
    
    tubes.plotCalibration()


    #farbe = (0.5, 0.5, 1.0)
    #tubes.setColor(farbe)
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.8) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.5) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.3) )
    #time.sleep(1)
    #tubes.setColor( (0.5, 0.5, 0.1) )

>>>>>>> 656542cf1eecf3a5e8d56f1647530f5791a73c8b
