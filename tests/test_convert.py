#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# test_convert.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# created 2011-10-14 KS
# last mod 2011-10-14 KS
#

from ..convert import xyY2rgb
from ..convert import Convert

def test_xyY2rgb():
    assert [round(x, 14) for x in xyY2rgb( (.5, .5, 15.) )] == [22.754841,
    14.0605965, -2.3556915]
    # TODO test was calculated from http://brucelindbloom.com/index.html but
    # does not fit to our algorithm
    #assert [round(x, 14) for x in xyY2rgb( (.5, .5, 15.) )] == [3.823824,
    #        3.118855, -1.452654]
    #assert [round(x, 14) for x in xyY2rgb( (.1, .2, 30.) )] == [-5.462513,
    #        5.160600, 8.257528]

def test_Covert_xyY2xyz():
    convert = Convert()
    assert [round(x, 14) for x in convert.convert_xyY_to_xyz((.5, .5,
        15.))] == [15.0, 15.0, 0.0]
    assert [round(x, 14) for x in convert.convert_xyY_to_xyz((.5, .5,
        0.0))] == [0.0, 0.0, 0.0]

# TODO test was calculated from http://brucelindbloom.com/index.html but
# does not fit to our algorithm
#def test_Covert_xyz2rgb():
#    convert = Convert()
#    assert [round(x, 14) for x in convert.convert_xyz_to_rgb((15., 15.,
#        0))] == [3.823824, 3.118855, -1.452654]

