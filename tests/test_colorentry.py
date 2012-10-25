#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tests/test_colorentry.py
#
# (c) 2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
# last mod 2012-09-23 13:54 KS

import unittest

from ..colorentry import ColorEntry

class TestColorEntry(unittest.TestCase):
    """
    All tests which end on DRY can be run and should pass in dummy
    mode.
    """

    def test_create_color_entry(self):
        """
        tests the interface of ColorEntry.
        """
        # minimal call
        ce1 = ColorEntry("color1")
        self.assertEqual(ce1.name, "color1")
        self.assertIsNone(ce1.patch_stim_value)
        self.assertIsNone(ce1.voltages)
        self.assertIsNone(ce1.tubes_xyY)
        self.assertIsNone(ce1.tubes_xyY_sd)
        self.assertIsNone(ce1.monitor_xyY)
        self.assertIsNone(ce1.monitor_xyY_sd)
        # call with positional arguments
        ce2 = ColorEntry("color2", 0.2, (1000, 1200, 1500))
        self.assertEqual(ce2.name, "color2")
        self.assertEqual(ce2.patch_stim_value, 0.2)
        self.assertEqual(ce2.voltages, (1000, 1200, 1500))
        self.assertIsNone(ce2.tubes_xyY)
        self.assertIsNone(ce2.tubes_xyY_sd)
        self.assertIsNone(ce2.monitor_xyY)
        self.assertIsNone(ce2.monitor_xyY_sd)
        # call with named arguments
        ce3 = ColorEntry(name="color3", patch_stim_value="#FFFF00FF", voltages=(1000,
            1200, 1500))
        self.assertEqual(ce3.name, "color3")
        self.assertEqual(ce3.patch_stim_value, "#FFFF00FF")
        self.assertEqual(ce3.voltages, (1000, 1200, 1500))
        self.assertIsNone(ce3.tubes_xyY)
        self.assertIsNone(ce3.tubes_xyY_sd)
        self.assertIsNone(ce3.monitor_xyY)
        self.assertIsNone(ce3.monitor_xyY_sd)

if __name__ == "__main__":
    unittest.main()

