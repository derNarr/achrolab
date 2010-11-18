#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tubes.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-05-25, KS

from wasco.wasco import wasco, boardId
from wasco.WascoConstants import DAOUT1_16, DAOUT2_16, DAOUT3_16

from EyeOne.EyeOne import EyeOne
from EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    COLOR_SPACE_RGB,
                                    TRISTIMULUS_SIZE)

from math import exp,log

from colormath.color_objects import SpectralColor, xyYColor,RGBColor

import rpy2.robjects as robjects

import time,pickle

from ctypes import c_float


# want to run R-commands with R("command")
R = robjects.r
EyeOne = EyeOne()


class Tubes(object):
    """The class Tubes encapsulates all functions controlling the light
    tubes in the box."""
    def __init__(self):
        """Setting some "global" variables."""
        self.wascocard = wasco
        self.wasco_boardId = boardId 

        self.red_out = DAOUT2_16
        self.green_out = DAOUT1_16
        self.blue_out = DAOUT3_16

        self.IsCalibrated = False

        # EyeOne Pro
        self.EyeOne = EyeOne

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


    def setColor(self, color):
        """setColor sets the color of the tubes to the given color.
        * color should be a colormath color object"""

        #transform to sRGB
        rgb = color.convert_to('rgb', target_rgb='sRGB')

        #set the wasco-card to the right voltage
        self.setVoltage( (self._sRGBtoU_r(rgb.rgb_r), 
                          self._sRGBtoU_g(rgb.rgb_g), 
                          self._sRGBtoU_b(rgb.rgb_b)) )

    def calibrate(self, imi=0.5):
        """calibrate calibrates the tubes with the EyeOne Pro. The EyeOne
        Pro should be connected to the computer. The calibration takes
        around 2 minutes.
        * imi -- is the inter mesurement intervall in seconds."""
        # TODO generate logfile for every calibration

        # set EyeOne Pro variables
        if(EyeOne.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("measurement mode set to single emission.")
        else:
            print("failed to set measurement mode.")
            return
        if(EyeOne.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_RGB) ==
                eNoError):
            print("color space set to RGB.")
        else:
            print("failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put the EyeOne-Pro on the calibration plate and "
        + "press the key to start calibration.")
        while(EyeOne.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (EyeOne.I1_Calibrate() == eNoError):
            print("Calibration of the EyeOne Pro done.")
        else:
            print("Calibration of the EyeOne Pro failed. Please RESTART"
            + "the calibration of the tubes.")
            return
        
        ## Measurement
        print("\nPlease put the EyeOne-Pro in measurement position and hit"
        + "the button to start the measurement.")
        while(EyeOne.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Start measurement...")

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
            self.setVoltage(voltage)
            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            # TODO still needs the EyeOne.Constants not encapsulated
            # tottaly
            if(self.EyeOne.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ." %str(voltage))
            if(self.EyeOne.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(voltage))
            rgb_list.append(list(tri_stim))
        
        print("finished measurement")
        self.setVoltage( (0x0, 0x0, 0x0) ) # to signal that the
                                           # measurement is over
        xyY_list = list()
        for rgb in rgb_list:
            tmp_rgb = RGBColor(rgb[0], rgb[1], rgb[2])
            tmp_xyY = tmp_rgb.convert_to('xyY')
            xyY_list.append( (tmp_xyY.xyy_y, tmp_xyY.xyy_y, tmp_xyY.xyy_Y))

        
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
        
        # put xyY into R for the plotCalibration method
        xyY_x = robjects.FloatVector([x[0] for x in xyY_list])
        xyY_y = robjects.FloatVector([x[1] for x in xyY_list])
        xyY_Y = robjects.FloatVector([x[2] for x in xyY_list])
        R("xyY_x <- " + xyY_x.r_repr())
        R("xyY_y <- " + xyY_y.r_repr())
        R("xyY_Y <- " + xyY_Y.r_repr())

        print("Data read into R")

        ## fit a nonlinear least squares function (using nls() in R)
        ## y(x) = p1 + (p2 - p1) * exp[-exp(p3)x] (cf. Pinheiro & Bates, p. 511)
        
        try:
            ## red channel
            R('''
            len3 <- floor(length(voltage_r)/3)
            idr <- rgb_r >= 10 & rgb_r != 255 #only use rgb values between 10 and 255
            idr[-(1:len3)] = FALSE # area measured the red values
            rgb_r_small <- rgb_r[idr]
            voltage_r_small <- voltage_r[idr]
            #nls_r <- nls(rgb_r_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_r_small),
            #             start=c(p1=255, p2=-100, p3=-7))
            nls_r <- nls(rgb_r_small ~ p1 + p2*voltage_r_small,
                         start=c(p1=0, p2=1))
            ''')
            ## green channel
            R('''
            idg <- rgb_g >= 10 & rgb_g != 255 #only use rgb values between 10 and 255
            idg[-((len3+1):(2*len3))] = FALSE # area measured the green values
            rgb_g_small <- rgb_g[idg]
            voltage_g_small <- voltage_g[idg]
            #nls_g <- nls(rgb_g_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_g_small),
            #             start=c(p1=255, p2=-100, p3=-7))
            nls_g <- nls(rgb_g_small ~ p1 + p2*voltage_g_small,
                         start=c(p1=0, p2=1))
            ''')
            ## blue channel
            R('''
            idb <- rgb_b >= 10 & rgb_b != 255 #only use rgb values between 10 and 255
            idb[-((2*len3+1):(3*len3))] = FALSE # area measured the blue values
            rgb_b_small <- rgb_b[idb]
            voltage_b_small <- voltage_b[idb]
            #nls_b <- nls(rgb_b_small ~ p1 + (p2 - p1)*exp(-exp(p3)*voltage_b_small),
            #             start=c(p1=255, p2=-100, p3=-7))
            nls_b <- nls(rgb_b_small ~ p1 + p2*voltage_b_small,
                         start=c(p1=0, p2=1))
            ''')
            
            print("Parameter estimated.")
        except:
            print("failed to estimate parameters, saved data anyway")
            # save all created R objects to the file calibration_tubes.RData
            R('save(list=ls(), file="calibration_tubes' + 
                    time.strftime("%Y%m%d_%H%M") + '.RData")')
            return

        # extract extimated parameters in R to make them easier available
        # in pyhton
        R('''
        p_r <- coef(nls_r)
        p_g <- coef(nls_g)
        p_b <- coef(nls_b)
        ''')
        
        # save all created R objects to the file calibration_tubes.RData
        R('save(list=ls(), file="calibration_tubes' + 
                time.strftime("%Y%m%d_%H%M") + '.RData")')

        # save the estimated parameters to the tube object
        self.red_p1 = R['p_r'][0]
        self.red_p2 = R['p_r'][1]
        #self.red_p3 = R['p_r'][2]
        self.green_p1 = R['p_g'][0]
        self.green_p2 = R['p_g'][1]
        #self.green_p3 = R['p_g'][2]
        self.blue_p1 = R['p_b'][0]
        self.blue_p2 = R['p_b'][1]
        #self.blue_p3 = R['p_b'][2]

        print("red_p1" + str(self.red_p1)) 
        print("red_p2" + str(self.red_p2)) 
        #print("red_p3" + str(self.red_p3))
        print("green_p1" + str(self.green_p1))
        print("green_p2" + str(self.green_p2))
        #print("green_p3" + str(self.green_p3))
        print("blue_p1" + str(self.blue_p1))
        print("blue_p2" + str(self.blue_p2))
        #print("blue_p3" + str(self.blue_p3))
        
        # finished calibration :)
        self.IsCalibrated = True
        print("Calibration of the tubes finished.")


    def _sRGBtoU_r(self, red_sRGB):
        x = float(red_sRGB)
        return ((x - self.red_p1)/self.red_p2)

    def _sRGBtoU_g(self, green_sRGB):
        x = float(green_sRGB)
        return ((x - self.green_p1)/self.green_p2)

    def _sRGBtoU_b(self, blue_sRGB):
        x = float(blue_sRGB)
        return ((x - self.blue_p1)/self.blue_p2)

    #def _sRGBtoU_r(self, red_sRGB):
    #    x = float(red_sRGB)
    #    return (-log((x - self.red_p1)/(self.red_p2 - self.red_p1)) / 
    #            exp(self.red_p3))

    #def _sRGBtoU_g(self, green_sRGB):
    #    x = float(green_sRGB)
    #    return (-log((x - self.green_p1)/(self.green_p2 - self.green_p1)) / 
    #            exp(self.green_p3))

    #def _sRGBtoU_b(self, blue_sRGB):
    #    x = float(blue_sRGB)
    #    return (-log((x - self.blue_p1)/(self.blue_p2 - self.blue_p1)) / 
    #            exp(self.blue_p3))

    def setVoltage(self, U_rgb):
        """setVoltage set the voltage in the list or tuple of U_rgb to the 
        wasco card.
        U_rgb should contain three integers between 0x000 and 0xFFF."""
        
        #set the wasco-card to the right voltage
        self.wascocard.wasco_outportW(self.wasco_boardId, self.red_out,
                                int(U_rgb[0]))
        self.wascocard.wasco_outportW(self.wasco_boardId, self.green_out,
                                int(U_rgb[1]))
        self.wascocard.wasco_outportW(self.wasco_boardId, self.blue_out,
                                int(U_rgb[2]))
        return

    def saveParameter(self, filename="./lastParameterTubes.pkl"):
        """Saves the for the interpolation fuction used parameter."""
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
        """Loads the for the interpolation fuction used parameter."""
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
        """plotCalibration plots the in the calibration measured colors in
        an xyY-Space"""
        if(not self.IsCalibrated):
            return
        # the in this R code used variables are created in calibrate()
        # xyY_x, xyY_y, xyY_Y, idr, idg, idb, voltage_r, voltage_g,
        # voltage_b, rgb_r, rgb_g, rgb_b, p_r, p_g, p_b

        # plot used datapoints for calibration
        R(' pdf("data_points_xyY_tubes'+time.strftime("%Y%m%d_%H%M")
            +'.pdf")')
        R('''
        layout(matrix(c(1,1,1,2,3,4), 3, 2), respect=matrix(c(0,0,0,1,1,1),3,2))
        
        par(mai=c(1.3, .5, 1, .1), mgp=c(2.2,1,0))
        plot(xyY_x[idr], xyY_y[idr], type="b", pch=16, col="red",
            ylim=c(0,.8), xlim=c(0,.8), xlab="x", ylab="y", main="xyY Space for
            Tubes", sub="Measured data points, which were used for
            calibration")
        points(xyY_x[idg], xyY_y[idg], type="b", pch=16, col="green")
        points(xyY_x[idb], xyY_y[idb], type="b", pch=16, col="blue")
        
        par(mai=c(.5, .5, 0.1, 0.1), mgp=c(2.2,1,0))
        plot(voltage_r[idr], xyY_Y[idr], type="l", pch=16, col="red",
            xlab="voltage red channel", ylab="Y", ylim=c(0,1))
        plot(voltage_g[idg], xyY_Y[idg], type="l", pch=16, col="green",
            xlab="voltage green channel", ylab="Y", ylim=c(0,1))
        plot(voltage_b[idb], xyY_Y[idb], type="l", pch=16, col="blue",
            xlab="voltage blue channel", ylab="Y", ylim=c(0,1))

        dev.off()
        ''')

        # plot calibration curves and data points for each channel
        R('pdf("calibration_curves_rgb_tubes'+time.strftime("%Y%m%d_%H%M")
            +'.pdf", width=9, height=8)')

        R('''
        par(mfrow=c(3,3))
        len3 <- floor(length(voltage_r)/3)
        # only red voltage
        plot(voltage_r[1:len3], rgb_r[1:len3], col="red", ylim=c(0,300),
            pch=19,
            main="red channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="red rgb-value")
        points(voltage_r[1:len3], rgb_g[1:len3], pch=21, col="green")
        points(voltage_r[1:len3], rgb_b[1:len3], pch=21, col="blue")
        curve(p_r[1] + p_r[2]*x, col="red", add=T, xlab="", ylab="")
        #curve(p_r[1] + (p_r[2] - p_r[1])*exp(-exp(p_r[3])*x), col="red",
        #    add=T, xlab="", ylab="")
        
        # only green voltage
        plot(voltage_g[(len3+1):(2*len3)], rgb_g[(len3+1):(2*len3)], 
            col="green", ylim=c(0,300), pch=19,
            main="green channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="green rgb-value")
        points(voltage_g[(len3+1):(2*len3)], rgb_r[(len3+1):(2*len3)], pch=21,
              col="red")
        points(voltage_g[(len3+1):(2*len3)], rgb_b[(len3+1):(2*len3)], pch=21,
              col="blue")
        curve(p_g[1] + p_g[2]*x, col="green", add=T, xlab="", ylab="")
        #curve(p_g[1] + (p_g[2] - p_g[1])*exp(-exp(p_g[3])*x), col="green",
        #    add=T, xlab="", ylab="")
        
        # only blue voltage
        plot(voltage_b[(2*len3+1):(3*len3)], rgb_b[(2*len3+1):(3*len3)],
            col="blue", ylim=c(0,300), pch=19,
            main="blue channel vs. voltage\ndata points and
            calibration curve",
            xlab="voltage", ylab="blue rgb-value")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_g[(2*len3+1):(3*len3)], 
            pch=21, col="green")
        points(voltage_b[(2*len3+1):(3*len3)], rgb_r[(2*len3+1):(3*len3)], 
            pch=21, col="red")
        curve(p_b[1] + p_b[2]*x, col="blue", add=T, xlab="", ylab="")
        #curve(p_b[1] + (p_b[2] - p_b[1])*exp(-exp(p_b[3])*x), col="blue",
        #    add=T, xlab="", ylab="")
        
        # residual plots free y-scale
        pred_r <- p_r[1] + p_r[2]*voltage_r
        pred_g <- p_g[1] + p_g[2]*voltage_g
        pred_b <- p_b[1] + p_b[2]*voltage_b

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
            ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)
        plot(voltage_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="voltage", ylab="resid")
        abline(h=0)

        dev.off()
        ''')


if(__name__=="__main__"):
    tubes = Tubes()
    tubes.calibrate(imi=1.0)

    tubes.saveParameter()
    filename="./parameterTubes"+time.strftime("%Y%m%d_%H%M")+".pkl"
    tubes.saveParameter(filename)
    
    tubes.plotCalibration()

    #from colormath.color_objects import xyYColor,RGBColor

    #farbe = xyYColor(0.5, 0.5, 1.0)
    #tubes.setColor(farbe)
    #time.sleep(1)
    #tubes.setColor(xyYColor(0.5, 0.5, 0.))
    #time.sleep(1)
    #tubes.setColor(xyYColor(0.5, 0.5, 0.8))
    #time.sleep(1)
    #tubes.setColor(xyYColor(0.5, 0.5, 0.5))
    #time.sleep(1)
    #tubes.setColor(xyYColor(0.5, 0.5, 0.3))
    #time.sleep(1)
    #tubes.setColor(xyYColor(0.5, 0.5, 0.1))
    #for i in range(50,255):
    #    tubes.setColor(RGBColor(i, i, i))
    #    time.sleep(0.1)

    #for i in range(50,255):
    #    tubes.setColor(RGBColor(i, 0, 0))
    #    time.sleep(0.1)

    #for i in range(50,255):
    #    tubes.setColor(RGBColor(0, i, 0))
    #    time.sleep(0.1)

    #monitor.Color2RGB(farbe)

