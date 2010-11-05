#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./visionlab-utils/iterativColorTubes.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-11-05, KS

from colormath.color_objects import xyYColor,RGBColor,SpectralColor
from visionlab.tubes import Tubes
from visionlab.monitor import Monitor
from visionlab.EyeOne.EyeOne import EyeOne
from visionlab.EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    SPECTRUM_SIZE)
from ctypes import c_float
import time
from psychopy import visual
import rpy2.robjects as robjects
# want to run R-commands with R("command")
R = robjects.r


# returns tuble
def xyYdiff(color1, color2):
    return (color2.xyy_x - color1.xyy_x,
            color2.xyy_y - color1.xyy_y,
            color2.xyy_Y - color1.xyy_Y)

# returns tuble
def xyYnorm(color):
    return (color.xyy_x**2 + color.xyy_y**2 + color.xyy_Y**2)**0.5

# returns float
def norm(vec):
    return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

# returns xyYColor
def xyYnew_color(old_color, vec):
    return xyYColor(old_color.xyy_x + vec[0],
                    old_color.xyy_y + vec[1],
                    old_color.xyy_Y + vec[2])


# returns tuple (voltages, tri_stim)  (last inputColor)
def iterativeColormatch(targetColor, eyeone, tubes, epsilon=0.01,
    streckung=1.0, imi=0.5, max_iterations=50):
    """
    iterativeColormatch tries to match the measurement of the tubes to the
    targetColor.
    * targetColor -- colormath color object
    * eyeone -- calibrated EyeOne object
    * tubes -- visionlab.tubes.Tubes object
    * epsilon
    * streckung
    * imi -- intermeasurement intervall
    * max_iterations
    """
    # set colors
    if isinstance(targetColor, tuple):
        targetColor = xyYColor(targetColor[0], targetColor[1],
                targetColor[2])
    else:
        targetColor = targetColor.convert_to('xyY')
    inputColor = targetColor
    measuredColor = xyYColor(0,0,0)
    diffColor = (1.0, 1.0, 1.0)
    
    tubes.setColor(inputColor)
    
    print("Start measurement...")
    
    tri_stim = (c_float * TRISTIMULUS_SIZE)()
    i=0
    print("\n\nTarget: " + str(targetColor) + "\n")
    
    while ((norm(diffColor) > epsilon) & (i < max_iterations)):
        tubes.setColor(inputColor)
        i = i + 1 # new round
        time.sleep(imi)
        if(eyeone.I1_TriggerMeasurement() != eNoError):
            print("Measurement failed for color %s ." %str(inputColor))
        if(eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
            print("Failed to get tri stimulus for color %s ."
                    %str(inputColor))
        measuredColor = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
        print(str(measuredColor))
        # correct the new color to a probably reduced (streckung < 1)
        # negative difference to the measured color.
        diffColor = [x*streckung for x in xyYdiff(measuredColor, targetColor)]
        print("diff: " + str(diffColor))
        inputColor = xyYnew_color(inputColor, diffColor)
    
    print("\nFinal inputColor: " + str(inputColor) + "\n\n")
    rgb = color.convert_to('rgb', target_rgb='sRGB')
    voltages = (tubes._sRGBtoU_r(rgb.rgb_r), 
                tubes._sRGBtoU_g(rgb.rgb_g),
                tubes._sRGBtoU_b(rgb.rgb_b))
    return (voltages, tri_stim)


