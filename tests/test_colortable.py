#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tests/test_colorentry.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2012-09-23 13:19 KS

import unittest

from ..colortable import ColorTable
from ..colorentry import ColorEntry

class TestColorTable(unittest.TestCase):
    """
    All tests which end on DRY can be run and should pass in dummy
    mode.
    """

    def setUp(self):
        self.col_table = ColorTable("./tests/testdata/color_table.csv")

    def testInitColorTable(self):
        col_table1 = ColorTable()
        self.assertEqual(col_table1.color_list, [])

    def testGetColorByName(self):
        assert isinstance( self.col_table.getColorByName("color121"),
                ColorEntry)

    def testGetColorsByName(self):
        ce_list = self.col_table.getColorsByName( ["color1",
            "color2", "color3"] )
        assert isinstance( ce_list , list)
        assert isinstance( ce_list[0], ColorEntry)

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

if __name__ == "__main__":
    unittest.main()

