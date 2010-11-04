#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colortable.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-11-02, KS

class ColorTable(object):
    """
    ColorTable store colors in xyY and the data needed for
    psychopy.visual.PatchStim, the monitor and the tubes.

    The colors in ColorTable are indexed. So there is a first and a last
    color. 

    ColorTable is a list of ColorEntries with some useful functions defined
    on this list.
    """

    def __init__(self, monitor, tubes):
        self.monitor = monitor
        self.tubes = tubes
        self.color_list = []
   

    def checkColors(self, index_list=None, name_list=None):
        """
        checkColors checks if the color entries are still consistent. It
        measures the color of the monitor and the tubes and compares the
        measurements with the saved values.
        """
        pass

    
    def createColorList(self, patch_stim_value_list=None,
            voltages_list=None):
        """
        createColorList creates a list of ColorEntry objects.
        """
        if patch_stim_value_list and voltages_list:
            if not len(patch_stim_value_list) == len(voltages_list):
                print("patch_stim_value_list and voltages_list must have same length")
                return
        pass

    def showColorList(self, index_list=None, name_list=None):
        """
        draws every color on the screen and changes the illumination of the
        tubes to the corresponding voltage. Left mouse click changes to the
        next color in color list.
        """
        pass

    def saveToR(self, filename):
        """
        saves object to R.
        """
        pass

    def saveToCvs(self, filename):
        """
        saves object to comma sperated textfile.
        """
        pass

    def saveToPickle(self, filename):
        """
        saves object to pickle-file.
        """
        pass

    def loadFromR(self, filename):
        """
        loads object to R.
        """
        pass

    def loadFromCvs(self, filename):
        """
        loads object to comma sperated textfile.
        """
        pass

    def loadFromPickle(self, filename):
        """
        loads object to pickle-file.
        """
        pass


