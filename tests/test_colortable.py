#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tests/test_colorentry.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-10-24 KS

from psychopy import visual

from ..colortable import ColorTable, CalibColorTable
from ..colorentry import ColorEntry
from ..eyeone import EyeOne
from ..monitor import Monitor
from ..tubes import Tubes

eyeone = EyeOne.EyeOne(dummy=True)
mywin = visual.Window(size=(800,600), color=(0,0,0))
mon = Monitor(eyeone, mywin)
tub = Tubes()


class TestColorTable(object):
    """
    All tests which end on DRY can be run and should pass in dummy
    mode.
    """

    def testInitColorTable(self):
        self.test_table = ColorTable("./tests/testdata/color_table.pkl")

    def testGetColorByName(self):
        assert isinstance( self.test_table.getColorByName("color121"),
                ColorEntry)

    def testGetColorsByName(self):
        ce_list = self.test_table.getColorsByName( ["color1",
            "color2", "color3"] )
        assert isinstance( ce_list , list)
        assert isinstance( ce_list[0], ColorEntry)

    def testShowColorList(self):
        self.test_table.showColorList(tub, mon,index_list=[3,4,5])

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



class TestCalibColorTable(object):
    """
    All tests which end on DRY can be run and should pass in dummy
    mode.
    """

    def testInitColorTable(self):
        test_table = CalibColorTable(mon, tub)

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


