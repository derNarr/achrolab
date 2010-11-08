#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./monitor.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-05-25, KS
#          2010-06-11, NU

from psychopy import visual

from EyeOne.EyeOne import EyeOne
from EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    SPECTRUM_SIZE)

from math import exp,log

from colormath.color_objects import SpectralColor

import rpy2.robjects as robjects

import time,pickle

from ctypes import c_float

# want to run R-commands with R("command")
R = robjects.r


class Monitor(object):
    """The class Monitor encapsulates the color transformation /
    corrections for the crt-color-monitor."""
    def __init__(self):
        """Setting some "global" variables."""
        self.IsCalibrated = False

        # EyeOne Pro
        self.EyeOne = EyeOne

        # set default values for the sRGBtoU transformation function
        self.red_p1 =   0.0 
        self.red_p2 =   1.0
        self.green_p1 = 0.0
        self.green_p2 = 1.0
        self.blue_p1 =  0.0
        self.blue_p2 =  1.0


    def ColorToRGB(self, color, format="255"):
        """ColorToRGB accepts a colormath color and returns a tuple of
        three RGB values. 
        When the format argument ist set to "psychopy" ColorToRGB returns
        floats between -1 and 1. In all other cases it will return integers
        between 0 and 255."""

        # transform to sRGB
        srgb = color.convert_to('rgb', target_rgb='sRGB')

        rgb = ( self._sRGBtoRGB_r(srgb.rgb_r),
                self._sRGBtoRGB_g(srgb.rgb_g),
                self._sRGBtoRGB_b(srgb.rgb_b) )

        # test if psychopy format is set:
        if format == "psychopy":
            return self._toPsychopy(rgb)
        else:
            return rgb

    # screen = 0 or 1, depending on which screen to calibrate
    def calibrate(self, imi=0.5, screen=1):
        """calibrates the monitor with the EyeOne Pro. The EyeOne
        Pro should be connected to the computer. The calibration takes
        around 2 minutes, depending on the imi.
        * imi -- is the inter mesurement intervall in seconds.
        * screen -- gives the used screen for the calibration (see
                    psychopy.visual.Window for details)."""
        # TODO generate logfile for every calibration

        # set EyeOne Pro variables
        if(EyeOne.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("measurement mode set to single emission.")
        else:
            print("failed to set measurement mode.")
            return
            
        
        if(EyeOne.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_CIExyY) ==
                eNoError):
            print("color space set to CIExyY.")
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
            print("Calibration of the EyeOne Pro failed. Please RESTART "
            + "the calibration of the monitor.")
            return
        
        ## Measurement
        
        # new psychopy version from 1.6+
        #win = visual.Window(size=(800,600), color=(0,0,0),
        #                    colorSpace="rgb", screen=screen)

        # old psychopy version 1.5 and earlier
        win = visual.Window(size=(1600,1200), rgb=(0,0,0), screen=screen)
        patch_stim = visual.PatchStim(win, tex=None, size=(2,2), rgb=(0,0,0))
        
        # prompt for the click on the button of the EyeOne Pro
        print("\nPlease put the EyeOne-Pro in measurement position and hit"
        + " the button to start the measurement.")
        while(EyeOne.I1_KeyPressed() != eNoError):
            time.sleep(0.01)

        print("Start measurement...")
        
        spectra = list() # saves the measured spectra

        # define some variables
        # generating the tested voltages (r, g, b)
        colors = list()
        for i in range(25): 
            colors.append( ((55 + 8 * i), 0, 0) ) 
        for i in range(25):
            colors.append( (0, (55 + 8 * i), 0) )
        for i in range(25):
            colors.append( (0, 0, (55 + 8 * i)) )

        spect = (c_float * SPECTRUM_SIZE)() # memory to where EyeOne
                                            # Pro saves spectrum.

        for color in colors:
            # new psychopy version from 1.6+
            #win.setColor( self._toPsychopy(color), colorSpace="rgb")
            #win.flip()
            #win.flip() # do it twice because of some issues of win.setColor
            
            # old psychopy version 1.5 and earlier
            patch_stim.setRGB( self._toPsychopy(color) )
            patch_stim.draw()
            win.flip()

            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects

            if(self.EyeOne.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for color %s ." %str(color))
            if(self.EyeOne.I1_GetSpectrum(spect, 0) != eNoError):
                print("Failed to get spectrum for color %s ."
                        %str(color))
            spectra.append(list(spect))
        
        win.close()

        print("finished measurement")
        
        xyY = list()
        xyz = list()
        rgb = list()

#        # set negative values to zero
#        # negative intensity is not reasonable
#        for i in range(len(spectra)):
#            for j in range(len(spectra[i])):
#                if spectra[i][j] < 0:
#                    spectra[i][j] = 0.0


        # convert spectra to colormath object SpectralColor
        for spectrum in spectra:
            spectral = SpectralColor(observer=2, illuminant='d65',
                spec_380nm=spectrum[0],
                spec_390nm=spectrum[1],
                spec_400nm=spectrum[2],
                spec_410nm=spectrum[3],
                spec_420nm=spectrum[4],
                spec_430nm=spectrum[5],
                spec_440nm=spectrum[6],
                spec_450nm=spectrum[7],
                spec_460nm=spectrum[8],
                spec_470nm=spectrum[9],
                spec_480nm=spectrum[10],
                spec_490nm=spectrum[11],
                spec_500nm=spectrum[12],
                spec_510nm=spectrum[13],
                spec_520nm=spectrum[14],
                spec_530nm=spectrum[15],
                spec_540nm=spectrum[16],
                spec_550nm=spectrum[17],
                spec_560nm=spectrum[18],
                spec_570nm=spectrum[19],
                spec_580nm=spectrum[20],
                spec_590nm=spectrum[21],
                spec_600nm=spectrum[22],
                spec_610nm=spectrum[23],
                spec_620nm=spectrum[24],
                spec_630nm=spectrum[25],
                spec_640nm=spectrum[26],
                spec_650nm=spectrum[27],
                spec_660nm=spectrum[28],
                spec_670nm=spectrum[29],
                spec_680nm=spectrum[30],
                spec_690nm=spectrum[31],
                spec_700nm=spectrum[32],
                spec_710nm=spectrum[33],
                spec_720nm=spectrum[34],
                spec_730nm=spectrum[35])
            
            tmp_xyY = spectral.convert_to('xyY')
            tmp_xyz = spectral.convert_to('xyz')
            tmp_rgb = spectral.convert_to('rgb')
            
            xyY.append( (tmp_xyY.xyy_x, tmp_xyY.xyy_y, tmp_xyY.xyy_Y) )
            xyz.append( (tmp_xyz.xyz_x, tmp_xyz.xyz_y, tmp_xyz.xyz_z) )
            rgb.append( (tmp_rgb.rgb_r, tmp_rgb.rgb_g, tmp_rgb.rgb_b) )
        
        # get python objects into R -- maybe there is a better way TODO
        r_spectra = [robjects.FloatVector(x) for x in spectra]
        input_rgb_r = robjects.IntVector([x[0] for x in colors])
        input_rgb_g = robjects.IntVector([x[1] for x in colors])
        input_rgb_b = robjects.IntVector([x[2] for x in colors])
        rgb_r = robjects.FloatVector([x[0] for x in rgb])
        rgb_g = robjects.FloatVector([x[1] for x in rgb])
        rgb_b = robjects.FloatVector([x[2] for x in rgb])
        
        R("spectra <- data.frame()")
        for r_spectrum in r_spectra:
            R("spectra <- rbind(spectra," + r_spectrum.r_repr() + ")")
        R("input_rgb_r <- " + input_rgb_r.r_repr())
        R("input_rgb_g <- " + input_rgb_g.r_repr())
        R("input_rgb_b <- " + input_rgb_b.r_repr())
        R("rgb_r <- " + rgb_r.r_repr())
        R("rgb_g <- " + rgb_g.r_repr())
        R("rgb_b <- " + rgb_b.r_repr())
        
        # put xyY into R for the plotCalibration method
        xyY_x = robjects.FloatVector([x[0] for x in xyY])
        xyY_y = robjects.FloatVector([x[1] for x in xyY])
        xyY_Y = robjects.FloatVector([x[2] for x in xyY])
        R("xyY_x <- " + xyY_x.r_repr())
        R("xyY_y <- " + xyY_y.r_repr())
        R("xyY_Y <- " + xyY_Y.r_repr())

        print("Data read into R")

        ## fit a nonlinear least squares function (using nls() in R)
        ## y(x) = p1 + (p2 - p1) * exp[-exp(p3)x] (cf. Pinheiro & Bates, p. 511)
        
        print("\nEstimating the gamma correction is not implemented yet!")
        
        try:
            ## red channel
            R('''
            len3 <- floor(length(input_rgb_r)/3)
            idr <- rgb_r != 0 & rgb_r != 255 #don't use rgb values of 0 and 255
            idr[-(1:len3)] = FALSE # area measured the red values
            rgb_r_small <- rgb_r[idr]
            input_rgb_r_small <- input_rgb_r[idr]
            nls_r <- nls(rgb_r_small ~ p1 + p2*input_rgb_r_small,
                         start=c(p1=0, p2=1))
            ''')
            ## green channel
            R('''
            idg <- rgb_g != 0 & rgb_g != 255 #don't use rgb values of 0 and 255
            idg[-((len3+1):(2*len3))] = FALSE # area measured the green values
            rgb_g_small <- rgb_g[idg]
            input_rgb_g_small <- input_rgb_g[idg]
            nls_g <- nls(rgb_g_small ~ p1 + p2*input_rgb_g_small,
                         start=c(p1=0, p2=1))
            ''')
            ## blue channel
            R('''
            idb <- rgb_b != 0 & rgb_b != 255 #don't use rgb values of 0 and 255
            idb[-((2*len3+1):(3*len3))] = FALSE # area measured the blue values
            rgb_b_small <- rgb_b[idb]
            input_rgb_b_small <- input_rgb_b[idb]
            nls_b <- nls(rgb_b_small ~ p1 + p2*input_rgb_b_small,
                         start=c(p1=0, p2=1))
            ''')
            
            print("Parameter estimated.")
        except:
            print("failed to estimate parameters, saved data anyway")
            # save all created R objects to the file calibration_tubes.RData
            R('save(list=ls(), file="calibration_monitor' + 
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
        R('save(list=ls(), file="calibration_monitor' + 
                time.strftime("%Y%m%d_%H%M") + '.RData")')

        # save the estimated parameters to the tube object
        self.red_p1 = R['p_r'][0]
        self.red_p2 = R['p_r'][1]
        self.green_p1 = R['p_g'][0]
        self.green_p2 = R['p_g'][1]
        self.blue_p1 = R['p_b'][0]
        self.blue_p2 = R['p_b'][1]

        print("red_p1" + str(self.red_p1)) 
        print("red_p2" + str(self.red_p2)) 
        print("green_p1" + str(self.green_p1))
        print("green_p2" + str(self.green_p2))
        print("blue_p1" + str(self.blue_p1))
        print("blue_p2" + str(self.blue_p2))
        
        # finished calibration :)
        self.IsCalibrated = True
        print("Calibration of the monitor finished.")


    def _sRGBtoRGB_r(self, red_sRGB):
        x = float(red_sRGB)
        return ((x - self.red_p1)/self.red_p2)

    def _sRGBtoRGB_g(self, green_sRGB):
        x = float(green_sRGB)
        return ((x - self.green_p1)/self.green_p2)

    def _sRGBtoRGB_b(self, blue_sRGB):
        x = float(blue_sRGB)
        return ((x - self.blue_p1)/self.blue_p2)
    
    def _toPsychopy(self, rgb):
        """Converts a rgb tuple of 0:255 values to a -1:1 format in a
        strict linear form."""
        return [x/128.0-1.0 for x in rgb]
        # TODO 255 entspricht nicht 1 sondern 0.9... !

    def saveParameter(self, filename="./lastParameterMonitor.pkl"):
        """Saves the for the interpolation fuction used parameter."""
        # TODO what to do, if file don't exists? Throw exception?
        f = open(filename, 'wb')
        pickle.dump(self.red_p1, f)
        pickle.dump(self.red_p2, f)
        pickle.dump(self.green_p1, f)
        pickle.dump(self.green_p2, f)
        pickle.dump(self.blue_p1, f)
        pickle.dump(self.blue_p2, f)
        f.close()

    def loadParameter(self, filename="./lastParamterMonitor.pkl"):
        """Loads the for the interpolation fuction used parameter."""
        # TODO warn if a file gets replaced?
        f = open(filename, 'rb')
        self.red_p1   = pickle.load(f)
        self.red_p2   = pickle.load(f)
        self.green_p1 = pickle.load(f)
        self.green_p2 = pickle.load(f)
        self.blue_p1  = pickle.load(f)
        self.blue_p2  = pickle.load(f)
        f.close()


    def plotCalibration(self):
        """plotCalibration plots the in the calibration measured colors in
        an xyY-Space"""
        if(not self.IsCalibrated):
            return
        # the in this R code used variables are created in calibrate()
        # xyY_x, xyY_y, xyY_Y, idr, idg, idb, input_rgb_r, input_rgb_g,
        # input_rgb_b, rgb_r, rgb_g, rgb_b, p_r, p_g, p_b

        # plot used datapoints for calibration
        R(' pdf("data_points_xyY_monitor'+time.strftime("%Y%m%d_%H%M")
            +'.pdf")')
        R('''
        layout(matrix(c(1,1,1,2,3,4), 3, 2), respect=matrix(c(0,0,0,1,1,1),3,2))
        
        par(mai=c(1.3, .5, 1, .1), mgp=c(2.2,1,0))
        plot(xyY_x[idr], xyY_y[idr], type="b", pch=16, col="red",
            ylim=c(0,1), xlim=c(0,1), xlab="x", ylab="y", main="xyY Space for
            Tubes", sub="Measured data points, which were used for
            calibration")
        points(xyY_x[idg], xyY_y[idg], type="b", pch=16, col="green")
        points(xyY_x[idb], xyY_y[idb], type="b", pch=16, col="blue")
        
        par(mai=c(.5, .5, 0.1, 0.1), mgp=c(2.2,1,0))
        plot(input_rgb_r[idr], xyY_Y[idr], type="l", pch=16, col="red",
            xlab="input_rgb red channel", ylab="Y", ylim=c(0,1))
        plot(input_rgb_g[idg], xyY_Y[idg], type="l", pch=16, col="green",
            xlab="input_rgb green channel", ylab="Y", ylim=c(0,1))
        plot(input_rgb_b[idb], xyY_Y[idb], type="l", pch=16, col="blue",
            xlab="input_rgb blue channel", ylab="Y", ylim=c(0,1))

        dev.off()
        ''')

        # plot calibration curves and data points for each channel
        R('pdf("calibration_curves_rgb_monitor'+time.strftime("%Y%m%d_%H%M")
            +'.pdf", width=9, height=8)')

        R('''
        par(mfrow=c(3,3))
        len3 <- floor(length(input_rgb_r)/3)
        # only red input_rgb
        plot(input_rgb_r[1:len3], rgb_r[1:len3], col="red", ylim=c(0,300),
            pch=19,
            main="red channel vs. input_rgb\ndata points and
            calibration curve",
            xlab="input_rgb", ylab="red rgb-value")
        points(input_rgb_r[1:len3], rgb_g[1:len3], pch=21, col="green")
        points(input_rgb_r[1:len3], rgb_b[1:len3], pch=21, col="blue")
        curve(p_r[1] + p_r[2]*x, col="red", add=T, xlab="", ylab="")
        
        # only green input_rgb
        plot(input_rgb_g[(len3+1):(2*len3)], rgb_g[(len3+1):(2*len3)], 
            col="green", ylim=c(0,300), pch=19,
            main="green channel vs. input_rgb\ndata points and
            calibration curve",
            xlab="input_rgb", ylab="green rgb-value")
        points(input_rgb_g[(len3+1):(2*len3)], rgb_r[(len3+1):(2*len3)], pch=21,
              col="red")
        points(input_rgb_g[(len3+1):(2*len3)], rgb_b[(len3+1):(2*len3)], pch=21,
              col="blue")
        curve(p_g[1] + p_g[2]*x, col="green", add=T, xlab="", ylab="")
        
        # only blue input_rgb
        plot(input_rgb_b[(2*len3+1):(3*len3)], rgb_b[(2*len3+1):(3*len3)],
            col="blue", ylim=c(0,300), pch=19,
            main="blue channel vs. input_rgb\ndata points and
            calibration curve",
            xlab="input_rgb", ylab="blue rgb-value")
        points(input_rgb_b[(2*len3+1):(3*len3)], rgb_g[(2*len3+1):(3*len3)], 
            pch=21, col="green")
        points(input_rgb_b[(2*len3+1):(3*len3)], rgb_r[(2*len3+1):(3*len3)], 
            pch=21, col="red")
        curve(p_b[1] + p_b[2]*x, col="blue", add=T, xlab="", ylab="")
        
        # residual plots free y-scale
        pred_r <- p_r[1] + p_r[2]*input_rgb_r
        pred_g <- p_g[1] + p_g[2]*input_rgb_g
        pred_b <- p_b[1] + p_b[2]*input_rgb_b

        resid_r <- rgb_r - pred_r
        resid_g <- rgb_g - pred_g
        resid_b <- rgb_b - pred_b

        plot(input_rgb_r[1:len3], resid_r[1:len3], pch=19, col="red",
            type="h",
            main="residuals (free y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)
        plot(input_rgb_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", type="h",
            main="residuals (free y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)
        plot(input_rgb_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", type="h",
            main="residuals (free y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)
        
        # residual plots fixed y-scale
        plot(input_rgb_r[1:len3], resid_r[1:len3], pch=19, col="red",
            ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)
        plot(input_rgb_g[(len3+1):(2*len3)], resid_g[(len3+1):(2*len3)], 
            pch=19, col="green", ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)
        plot(input_rgb_b[(2*len3+1):(3*len3)], resid_b[(2*len3+1):(3*len3)], 
            pch=19, col="blue", ylim=c(-20,20), type="h",
            main="residuals (fixed y-axis)", xlab="input_rgb", ylab="resid")
        abline(h=0)

        dev.off()
        ''')



if(__name__=="__main__"):
    monitor = Monitor()
    monitor.calibrate(imi=0.2, screen=1)
    
    monitor.saveParameter()
    filename="./parameterMonitor"+time.strftime("%Y%m%d_%H%M")+".pkl"
    monitor.saveParameter(filename)

    monitor.plotCalibration()
    
    from colormath.color_objects import xyYColor,RGBColor

    #farbe = xyYColor(0.5, 0.5, 1.0)
    #monitor.ColorToRGB(farbe)
    #monitor.ColorToRGB(xyYColor(0.5, 0.5, 0.9))
    #monitor.ColorToRGB(xyYColor(0.5, 0.5, 0.8))
    #monitor.ColorToRGB(xyYColor(0.5, 0.5, 0.5))
    #monitor.ColorToRGB(xyYColor(0.5, 0.5, 0.3))
    #monitor.ColorToRGB(xyYColor(0.5, 0.5, 0.1))
    #for i in range(50,255):
    #    monitor.ColorToRGB(RGBColor(i, i, i))
    #    time.sleep(0.1)

    #for i in range(50,255):
    #    monitor.ColorToRGB(RGBColor(i, 0, 0))
    #    time.sleep(0.1)

    #for i in range(50,255):
    #    monitor.ColorToRGB(RGBColor(0, i, 0))
    #    time.sleep(0.1)

    #monitor.Color2RGB(farbe)

