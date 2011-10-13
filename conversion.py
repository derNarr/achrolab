#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./conversion.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and Dominik Wabersich <dominik.wabersich [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)

import numpy as np

class Conversion(object):
    """
    Conversion Object.
    """
    
    def __init__(self, xyY):
        """
        Conversion Object init function.
        """

    def convert_xyY_to_rgb(self, xyY):
        """
        Convert from xyY to RGB.
        """
        self.xyY_x = xyY[0]
        self.xyY_y = xyY[1]
        self.xyY_Y = xyY[2]
        xyY = (self.xyY_x, self.xyY.y, self.xyY.Y)
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
        # RGB Working Space: CIE RGB, Reference White: E
        print("Conversion: Using CIE RGB Working Space with Reference White E.")
        m = np.array([[2.3706743, -0.9000405, -0.4706338],
                        [-0.5138850, 1.4253036, 0.0885814],
                        [0.0052982, -0.0146949, 1.0093968]])
        xyz = np.array([[self.xyz_x], [self.xyz_y], [self.xyz_z]])
        rgb = m.dot(xyz)
        self.rgb_r = rgb[0][0]
        self.rgb_g = rgb[1][0]
        self.rgb_b = rgb[2][0]
        return (self.rgb_r, self.rgb_g, self.rgb_b)

def xyY2rgb(xyY):
    convert = Conversion()
    return convert.convert_xyY_to_rgb(xyY)

