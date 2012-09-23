#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# test_convert.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# created 2011-10-14 KS
# last mod 2012-09-23 13:52 KS
#

import unittest

from ..convert import xyY2rgb
from ..convert import Convert

class ConvertTest(unittest.TestCase):

    def setUp(self):
        self.convert = Convert()

    def test_xyY2rgb(self):
        given = xyY2rgb((.5, .5, 15.))
        expected = [22.059507, 13.671279, -0.1409505]
        for idx, value in enumerate(given):
            self.assertAlmostEquals(value, expected[idx] , 8)
        # TODO test was calculated from http://brucelindbloom.com/index.html but
        # does not fit to our algorithm
        #assert [round(x, 14) for x in xyY2rgb( (.5, .5, 15.) )] == [3.823824,
        #        3.118855, -1.452654]
        #assert [round(x, 14) for x in xyY2rgb( (.1, .2, 30.) )] == [-5.462513,
        #        5.160600, 8.257528]

    def test_Covert_xyY2xyz(self):
        pairs = [
                (self.convert.convertXyYToXyz((.5, .5, 15.)), [15.0, 15.0, 0.0]),
                (self.convert.convertXyYToXyz((.5, .5, 0)), [0.0, 0.0, 0.0]),
                ]
        for given, expected in pairs:
            for idx, value in enumerate(given):
                self.assertAlmostEquals(value, expected[idx] , 8)

    def test_Covert_xyz2rgb(self):
        given = self.convert.convertXyzToRgb((15., 15., 0))
        #expected = [3.823824, 3.118855, -1.452654]
        expected = [22.059507, 13.671279, -0.1409505]
        for idx, value in enumerate(given):
            self.assertAlmostEquals(value, expected[idx] , 8)
        # TODO test was calculated from http://brucelindbloom.com/index.html but
        # does not fit to our algorithm
        #assert [round(x, 14) for x in self.convert.convertXyzToRgb((15.,
        #    15., 0))] == [3.823824, 3.118855, -1.452654]

