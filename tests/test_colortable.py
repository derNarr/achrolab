#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tests/test_colorentry.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)

from psychopy import visual

from ..colortable import ColorTable
from ..eyeone import EyeOne
from ..monitor import Monitor
from ..tubes import Tubes

eyeone = EyeOne.EyeOne(dummy=True)
mywin = visual.Window(size=(800,600), color=(0,0,0))
mon = Monitor(eyeone, mywin)
tub = Tubes(eyeone, dummy=True)

tub.calibrateEyeOne()


class TestColorTable(object):
    """
    All tests which end on DRY can be run and should pass in dummy
    mode.
    """

    def testInitColorTable(self):
        test_table = ColorTable(mon, tub)

    def testCheckColorTable(self):
        pass

    def testCheckColorTableTubes(self):
        pass

    def testCheckColorTableMonitor(self):
        pass

    def testGetColorByName(self):
        pass

    def testGetColorsByName(self):
        pass

    def testCreateColorList(self):
        pass

    def testMeasureColorListMonitor(self):
        pass

    def testFindVoltages(self):
        pass

    def testVoltagesTuning(self):
        pass

    def testMeasureColorListTubes(self):
        pass

    def testShowColorList(self):
        pass

    def testSaveToR(self):
        pass
    
    def testSaveToCsv(self):
        pass

    def testSaveToPickle(self):
        pass

    def testLoadFromR(self):
        pass

    def testLoadFromCsv(sefl):
        pass

    def testLoadFromPickle(self):
        pass




