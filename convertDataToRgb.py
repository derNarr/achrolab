#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./convertDataToRgb.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-01-17, KS

from colormath.color_objects import SpectralColor, xyYColor,RGBColor
from colortable import ColorTable

#filename = "./data/color_table_20110115_1306.pkl"
filename = "./data/color_table_20101209_1220.pkl"

color_table = ColorTable(monitor=None, tubes=None)
color_table.loadFromPickle(filename)

for i in range(len(color_table.color_list)):
    ce = color_table.color_list[i]
    if ce.tubes_xyY:
        xyY = xyYColor(ce.tubes_xyY[0], ce.tubes_xyY[1], ce.tubes_xyY[2])
        # save rgb values in tubes_xyY
        rgb = xyY.convert_to("rgb",
                targetRGB="sRGB", clip=False)
        color_table.color_list[i].tubes_xyY = (rgb.rgb_r, rgb.rgb_g,
                rgb.rgb_b)
    if ce.monitor_xyY:
        xyY = xyYColor(ce.monitor_xyY[0], ce.monitor_xyY[1], ce.monitor_xyY[2])
        # save rgb values in tubes_xyY
        rgb = xyY.convert_to("rgb",
                targetRGB="sRGB", clip=False)
        color_table.color_list[i].monitor_xyY = (rgb.rgb_r, rgb.rgb_g,
                rgb.rgb_b)

color_table.saveToCsv(filename + "RGB")

