#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tests/ut_colorentry.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-06-28, KS

import colorentry

import unittest

from eyeone import EyeOne
from psychopy import visual
from monitor import Monitor
from tubes import Tubes
from colortable import ColorTable

eyeone = EyeOne.EyeOne(dummy=True)
mywin = visual.Window(size=(800,600), color=(0,0,0))
mon = Monitor(eyeone, mywin)
tub = Tubes(eyeone, dummy=True)

tub.calibrateEyeOne()


class UTColorEntry(unittest.TestCase):
    """all tests which ends on DRY can be run and should pass in dummy
    mode."""

    def testCreateCE(self):
        test_color_entry1 = colorentry.ColorEntry("test1")
        test_color_entry2 = colorentry.ColorEntry("test2", 0.2,
                (1000,1200,1500))

    def testMeasureMonitorDRY(self):
        ce = colorentry.ColorEntry("test1", patch_stim_value=0.3)
        ce.measureMonitor(mon, n=3)

    def testMeasureTubesDRY(self):
        ce = colorentry.ColorEntry("test1", voltages=(1000,1200,1500))
        ce.findVoltagesTuning(tub)

    def testFindVoltagesDRY(self):
        ce = colorentry.ColorEntry("test1", voltages=(1000,1200,1500))
        ce.monitor_xyY = (0.1,0.2, 20)
        ce.findVoltages(tub)

    def testFindVoltagesTuningDRY(self):
        ce = colorentry.ColorEntry("test1", voltages=(1000,1200,1500))
        ce.monitor_xyY = (0.1,0.2, 20)
        ce.findVoltagesTuning(tub)


if __name__ == '__main__':
    unittest.main()

