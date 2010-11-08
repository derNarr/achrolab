#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colortable.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-11-08, KS

from psychopy import event
from colorentry import ColorEntry
import pickle

# TODO save measurements of each EyeOne Pro measurement in a folder
# ./measurements/ with date (as R-Datafile)
# TODO rewrite tubes.py to a slim version based on TriStim and voltages
# TODO write class to generate and measure all possible greys of the
# monitor with nice plotting, which generates a list of patch_stim_colors

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

    
    def createColorList(self, name_list=None, patch_stim_value_list=None,
            voltages_list=None):
        """
        createColorList creates a list of ColorEntry objects.
        """
        if patch_stim_value_list and voltages_list:
            if not len(patch_stim_value_list) == len(voltages_list):
                print("patch_stim_value_list and voltages_list must have same length")
                return
        if name_list:
            if not len(name_list) == len(patch_stim_value_list):
                print("name_list and patch_stim_value_list must have same length")
                return
        else:
            name_list = ["color" + str(x) for x in
                    range(len(patch_stim_value_list))]

        for i in range(len(name_list)):
            self.color_list.append( ColorEntry(name_list[i],
                patch_stim_value_list[i]) )

        self.monitor.calibrateEyeOne()
        self.monitor.startMeasurement()
        for colorentry in self.color_list:
            colorentry.measureMonitor(self.monitor, n=10)

        self.tubes.calibrateEyeOne()
        self.tubes.startMeasurement()
        for colorentry in self.color_list:
            colorentry.findVoltages(self.tubes)
            colorentry.measureTubes(self.tubes, n=10)


    def showColorList(self, index_list=None, name_list=None):
        """
        draws every color on the screen and changes the illumination of the
        tubes to the corresponding voltage. Left mouse click changes to the
        next color in color list.
        """
        print('''Click the left mouse button to move to the next
        corresponding colors of the tubes and monitor.''')
        for colorentry in self.color_list:
            self.monitor.setPatchStimColor(colorentry.patch_stim_color)
            self.tubes.setVoltages(colorentry.voltages)
            mouse = event.Mouse()
            event.clearEvents()
            show = True 
            while show:
                left, middle, right = mouse.getPressed()
                if left: 
                    core.wait(0.2)
                    show=False
        print("finished showing all colors")


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
        f = open(filename, "b")
        pickle.dump(self.color_list, f)
        f.close()
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
        f = open(filename, "b")
        self.color_list = pickle.load(self.color_list, f)
        f.close()
        pass


if __name__ == "__main__":
    from EyeOne import EyeOne
    from monitor2 import Monitor
    from tubes2 import Tubes
    eye_one = EyeOne.EyeOne(dummy=True)
    mon = Monitor(eye_one)
    tub = Tubes(eye_one)
 
    color_table = ColorTable(mon, tub)
    color_table.createColorList(patch_stim_value_list=[-0.3,-0.2,-0.1,0.0])

