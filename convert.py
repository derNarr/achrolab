#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./convert.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and Dominik Wabersich <dominik.wabersich [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-10-14 KS

import numpy as np

class Convert(object):
    """
    Convert Object.
    """
    
    def __init__(self):
        """
        Convert Object init function.
        """

    def convert_xyY_to_rgb(self, xyY):
        """
        Convert from xyY to RGB.
        """
        self.xyY_x = xyY[0]
        self.xyY_y = xyY[1]
        self.xyY_Y = xyY[2]
        xyY = (self.xyY_x, self.xyY_y, self.xyY_Y)
        xyz = self.convert_xyY_to_xyz(xyY)
        rgb = self.convert_xyz_to_rgb(xyz)
        return (rgb)

    def convert_xyY_to_xyz(self, xyY):
        """
        Convert from xyY to XYZ.
        """
        self.xyY_x = xyY[0]
        self.xyY_y = xyY[1]
        self.xyY_Y = xyY[2]
        x = self.xyY_x              # these lines are not necessary
        y = self.xyY_y              # you could also just use the self.xyY variables
        Y = self.xyY_Y              # but it makes the transformation equations easier to understand
        if y != 0:
            self.xyz_x = (x * Y) / y
            self.xyz_y = Y
            self.xyz_z = ( (1-x-y) * Y ) / y
        else:
            self.xyz_x = 0
            self.xyz_y = 0
            self.xyz_z = 0
        return (self.xyz_x, self.xyz_y, self.xyz_z)

    def convert_xyz_to_rgb(self, xyz):
        """
        Convert from XYZ to RGB.
        """
        self.xyz_x = xyz[0]
        self.xyz_y = xyz[1]
        self.xyz_z = xyz[2]
        # Conversion Matrix. http://brucelindbloom.com/index.html?Eqn_XYZ_to_RGB.html
        # sRGB, Reference White: D50, Bradford-adapted
        print("Convert: Using sRGB, reference white D50 and Bradford-adapted.")
        m = np.array([[ 3.1338561, -1.6168667, -0.4906146],
                     [-0.9787684,  1.9161415,  0.0334540], 
                     [ 0.0719453, -0.2289914,  1.4052427]])
        ## RGB Working Space: CIE RGB, Reference White: E
        #print("Convert: Using CIE RGB Working Space with Reference White E.")
        #m = np.array([[2.3706743, -0.9000405, -0.4706338],
        #                [-0.5138850, 1.4253036, 0.0885814],
        #                [0.0052982, -0.0146949, 1.0093968]])
        xyz = np.array([self.xyz_x, self.xyz_y, self.xyz_z])
        rgb = m.dot(xyz)
        #RGB = rgb
        #for i in range(3):
        #    if rgb[i] <= 0.0031308:
        #        RGB[i] = 12.92 * rgb[i]
        #    else:
        #        RGB[i] = 1.055 * rgb[i]**1/2.4 - 0.055
        self.rgb_r = rgb[0] #RGB[0]
        self.rgb_g = rgb[1] #RGB[1]
        self.rgb_b = rgb[2] #RGB[2]
        return (self.rgb_r, self.rgb_g, self.rgb_b)

def xyY2rgb(xyY):
    convert = Convert()
    return convert.convert_xyY_to_rgb(xyY)

