#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./visionlab-utils/iterativColorTubes.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
#     and Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-12-16, KS

from colormath.color_objects import xyYColor,RGBColor,SpectralColor
from tubes import Tubes
from EyeOne.EyeOne import EyeOne
from EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time
from exceptions import ValueError
from psychopy import visual
import rpy2.robjects as robjects
# want to run R-commands with R("command")
R = robjects.r


def write_data(voltage_color_list, filename):
    f = open(filename, "w")
    f.write("voltage_r, voltage_g, voltage_b, rgb_r, rgb_g, rgb_b\n") 
    for vc in voltage_color_list:
        for voltage in vc[0]:
            f.write(str(voltage) + ", ")
        rgb = vc[1]
        f.write(str(rgb.rgb_r) + ", " + str(rgb.rgb_g) + ", " +
                str(rgb.rgb-g) + "\n")
 


##########################################################################
###  Use xyY colors  #####################################################
##########################################################################

# returns tuble
def xyYdiff(color1, color2):
    if isinstance(color1, xyYColor):
        (x1, y1, z1) = (color1.xyy_x, color1.xyy_y, color1.xyy_Y)
    else:
        (x1, y1, z1) = (color1[0], color1[1], color1[2])
    if isinstance(color2, xyYColor):
        (x2, y2, z2) = (color2.xyy_x, color2.xyy_y, color2.xyy_Y)
    else:
        (x2, y2, z2) = (color2[0], color2[1], color2[2])
    return (x2 - x1, y2 - y1, z2 - z1)

# returns tuble
def xyYnorm(color):
    if isinstance(color, tuple):
        xyY = xyYColor(color[0], color[1], color[2])
    else:
        xyY = color
    rgb = xyY.convert_to('rgb', target_rgb='sRGB', clip=False)
    return (rgb.rgb_r**2 + rgb.rgb_g**2 + rgb.rgb_b**2)**0.5

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
    
    while ((norm(diffColor) > epsilon)):
        if i == max_iterations:
            inputColor = None
            print("not converged")
            return (None, None)
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
    rgb = inputColor.convert_to('rgb', target_rgb='sRGB', clip=False)
    voltages = (tubes._sRGBtoU_r(rgb.rgb_r), 
                tubes._sRGBtoU_g(rgb.rgb_g),
                tubes._sRGBtoU_b(rgb.rgb_b))
    return (voltages, measuredColor)

# returns xyYColor
def newVoltages(old_voltages, vec):
    return (old_voltages[0] + vec[0],
            old_voltages[1] + vec[1],
            old_voltages[2] + vec[2])



# return tuple of (voltages, color)
def measureColor(voltages, tubes, eyeone, imi=0.5):
    """
    measureColor measures inputColor and sleeps imi-time. Returns measured Color.
    * inputColor
    * imi-- intermeasurement intervall
    """
    tri_stim = (c_float * TRISTIMULUS_SIZE)()
    tubes.setVoltage(voltages)
    time.sleep(imi)
    if(eyeone.I1_TriggerMeasurement() != eNoError):
        print("Measurement failed for color %s ." %str(inputColor))
    if(eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
        print("Failed to get tri stimulus for color %s ."
                %str(inputColor))
    measuredColor = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
    return (voltages, measuredColor)


def createMeasurementSeries(starting_voltages, tubes, eyeone, step_R=0,
        step_G=0, step_B=0, series_quantity=10, imi=0.5):
    """
    createMeasurementSeries creates and returns a list of measured Points
    (voltages, xyYColor).
    * starting_voltages
    * step_R -- red value step between two points
    * step_G -- green value step between two points
    * step_B -- blue value step between two points
    * series_quantity -- number of measurements
    * imi -- sleep time between two measurements
    """
    diff_voltages = (-(1/2)*series_quantity*step_R,
                 -(1/2)*series_quantity*step_G,
                 -(1/2)*series_quantity*step_B)
    input_voltages = newVoltages(starting_voltages, diff_voltages)
    i = 0
    diff_voltages = (step_R,step_G,step_B)
    measured_series = []
    while (i < series_quantity):
        i = i + 1 # new round
        measured_voltage_color = measureColor(input_voltages, tubes, eyeone, imi=imi)
        measured_series.append( measured_voltage_color )
        print(str(measured_voltage_color[1]))
        print("diff: " + str(diff_voltages))
        input_voltages = newVoltages(input_voltages, diff_voltages)
    return measured_series

def findNearestColors(measured_color_list, target_color):
    """
    findNearestColors returns the nearest and the second nearest measured
    colorspoints (voltages, xyYColor) to targetColor.
    * measured_color_list -- contains the measured Colors
    * target_color
    """
# TODO take the two _seond_ nearest points and not the nearest point!
    nearest = measured_color_list[0]
    second_nearest = measured_color_list[1]
    for voltage_color in measured_color_list:
        if ( xyYnorm(xyYdiff(voltage_color[1], target_color)) <=
                xyYnorm(xyYdiff(nearest[1], target_color)) ):
            second_nearest = nearest
            nearest = voltage_color
        elif ( xyYnorm(xyYdiff(voltage_color[1], target_color)) <
                xyYnorm(xyYdiff(second_nearest[1], target_color)) ):
            second_nearest = voltage_color
    return (nearest, second_nearest) 

def measureBetweenColors(two_voltages_colors, tubes, eyeone, channel, stepsize=1):
    """
    measureBetweenColors returns a list of measured Colors between
    the first and second element of two_voltages_color.
    * two_voltages_colors contains a pair (tuple with two elements) of
          voltage_color
    * count -- number of measurements between colors
    """
# TODO implement stepsize
    if channel=="red":
        index = 0
    elif channel=="green":
        index = 1
    elif channel=="blue":
        index = 2
    else:
        raise ValueError("channel must be one of 'red', 'green' or 'blue'")
    
    voltages = list(two_voltages_colors[0][0]) # should be the same for the two
                                         # channels that are not varied
    voltage1 = int(two_voltages_colors[0][0][index])
    voltage2 = int(two_voltages_colors[1][0][index])

    measured_series = []

    if voltage1 > voltage2:
        (voltage1, voltage2) = (voltage2, voltage1)
    
    for voltage in range(voltage1, voltage2+1):
        voltages[index] = voltage
        measured_series.append( measureColor(voltages, tubes, eyeone) )

    return measured_series


def findBestColor(measured_color_red, measured_color_green,
        measured_color_blue, target_color):
    """
    findBestColor returns a color, which is nearest targetColor.
    * measured_color -- contains the measured colors for each channel
    * target_color
    """
    voltage_color_list = []
    voltage_color_list.extend( measured_color_red )
    voltage_color_list.extend( measured_color_green )
    voltage_color_list.extend( measured_color_blue )
    return min(voltage_color_list, key=(lambda a: xyYnorm(xyYdiff(a[1],
        target_color))))


# returns tuple (voltages, tri_stim)  (last inputColor)
def iterativeColormatch2(targetColor, eyeone, tubes, start_voltages=None,
        iterations=50, stepsize=10, imi=0.5):
    """
    iterativeColormatch2 tries to match the measurement of the tubes to the
    targetColor (with a different method than iterativeColormatch).
    * targetColor -- colormath color object or tuple of (x, y, Y)
    * eyeone -- calibrated EyeOne object
    * tubes -- visionlab.tubes.Tubes object
    * iterations
    """
    # TODO: extra iterations for the measurement points
    # set colors
    # TODO: imi
    if isinstance(targetColor, tuple):
        targetColor = xyYColor(targetColor[0], targetColor[1],
                targetColor[2])

    rgb = targetColor.convert_to('rgb', target_rgb='sRGB', clip=False)
    if start_voltages:
        input_voltages = start_voltages
    else:
        input_voltages = (tubes._sRGBtoU_r(rgb.rgb_r), 
                     tubes._sRGBtoU_g(rgb.rgb_g),
                     tubes._sRGBtoU_b(rgb.rgb_b))
    measuredColor = xyYColor(0,0,0)
    diffColor = (1.0, 1.0, 1.0)
    
    print("Start measurement...")
    
    i=0
    print("\n\nTarget: " + str(targetColor) + "\n")

    while (i < iterations):
        i = i + 1

        # create (voltages, color) list
        measuredColorList_R = createMeasurementSeries(input_voltages,
                tubes, eyeone, step_R=stepsize, series_quantity=20)
        measuredColorList_G = createMeasurementSeries(input_voltages,
                tubes, eyeone, step_G=stepsize, series_quantity=20)
        measuredColorList_B = createMeasurementSeries(input_voltages,
                tubes, eyeone, step_B=stepsize, series_quantity=20)

        filename = ("tuned_r" + str(rgb.rgb_r) + "g" + str(rgb.rgb_g) + "b" +
                str(rgb.rgb_b) + "_iteration" + str(i) + ".csv")
        write_data(measuredColorList_R, filename)
        write_data(measuredColorList_G, filename)
        write_data(measuredColorList_B, filename)

        # 2 nearest points of the list
        two_points_R = findNearestColors(measuredColorList_R, targetColor)
        two_points_G = findNearestColors(measuredColorList_G, targetColor)
        two_points_B = findNearestColors(measuredColorList_B, targetColor)

        # new measurement between 2 nearest points
        measuredColor_R = measureBetweenColors(two_points_R, tubes,
                eyeone, channel="red")
        measuredColor_G = measureBetweenColors(two_points_G, tubes,
                eyeone, channel="green")
        measuredColor_B = measureBetweenColors(two_points_B, tubes,
                eyeone, channel="blue")

        # now serch for point with the smallest distance to targetColor
        # should return inputColor or inputVoltages
        best_voltage_color = findBestColor(measuredColor_R, measuredColor_G, measuredColor_B, targetColor)
        input_voltages = best_voltage_color[0]
    
    print("\nFinal voltages:" + str(best_voltage_color[0]) + "\n\n")
    return best_voltage_color


##########################################################################
###  Use RGB colors  #####################################################
##########################################################################

# returns tuble
def RGBdiff(color1, color2):
    return (color2.rgb_r - color1.rgb_r,
            color2.rgb_g - color1.rgb_g,
            color2.rgb_b - color1.rgb_b)

# returns float 
def RGBnorm(color):
    return (color.rgb_r**2 + color.rgb_g**2 + color.rgb_b**2)**0.5

# returns float
def norm(vec):
    return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

# returns Color
def RGBnew_color(old_color, vec):
    return RGBColor(old_color.rgb_r + vec[0],
                    old_color.rgb_g + vec[1],
                    old_color.rgb_b + vec[2])


# returns tuple (voltages, tri_stim)  (last inputColor)
def iterativeColormatchRGB(targetColor, eyeone, tubes, epsilon=5.0,
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
        targetColor = RGBColor(targetColor[0], targetColor[1],
                targetColor[2])
    else:
        targetColor = targetColor.convert_to('rgb', target_rgb='sRGB',
                clip=False)
    inputColor = targetColor
    measuredColor = RGBColor(0,0,0)
    diffColor = (100.0, 100.0, 100.0)
    
    tubes.setColor(inputColor)
    
    print("Start measurement...")
    
    tri_stim = (c_float * TRISTIMULUS_SIZE)()
    i=0
    print("\n\nTarget: " + str(targetColor) + "\n")
    
    while ((norm(diffColor) > epsilon)):
        if i == max_iterations:
            inputColor = None
            print("not converged")
            return (None, None)
        i = i + 1 # new round
        tubes.setColor(inputColor)
        print("set tubes to: " + str( (tubes._sRGBtoU_r(inputColor.rgb_r), 
                tubes._sRGBtoU_g(inputColor.rgb_g),
                tubes._sRGBtoU_b(inputColor.rgb_b)) ) )
        time.sleep(imi)
        if(eyeone.I1_TriggerMeasurement() != eNoError):
            print("Measurement failed for color %s ." %str(inputColor))
        if(eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
            print("Failed to get tri stimulus for color %s ."
                    %str(inputColor))
        xyY = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
        measuredColor = xyY.convert_to('rgb', target_rgb='sRGB', clip=False)
        print("target color: " + str(targetColor))
        print("measured color: " + str(measuredColor))
        # correct the new color to a probably reduced (streckung < 1)
        # negative difference to the measured color.
        diffColor = [x*streckung for x in RGBdiff(measuredColor, targetColor)]
        print("diff: " + str(diffColor) + "\n")
        inputColor = RGBnew_color(inputColor, diffColor)
            
    
    print("\nFinal inputColor: " + str(inputColor) + "\n\n")
    #rgb = inputColor.convert_to('rgb', target_rgb='sRGB', clip=False)
    voltages = (tubes._sRGBtoU_r(inputColor.rgb_r), 
                tubes._sRGBtoU_g(inputColor.rgb_g),
                tubes._sRGBtoU_b(inputColor.rgb_b))
    return (voltages, measuredColor)

