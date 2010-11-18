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
import pickle,time

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

    def saveToCsv(self, filename):
        """
        saves object to comma sperated textfile.
        """
        f = open(filename, "w")
        f.write("name, patch_stim_value, "
                +"monitor_xyY_x, monitor_xyY_y, monitor_xyY_Y, "
                +"monitor_xyY_sd_x, monitor_xyY_sd_y, monitor_xyY_sd_Y, " 
                +"voltages_r, voltages_g, voltages_b, "
                +"tubes_xyY_x, tubes_xyY_y, tubes_xyY_Y, "
                +"tubes_xyY_sd_x, tubes_xyY_sd_y, tubes_xyY_sd_Y\n") 
        for ce in self.color_list: 
            f.write(ce.name+", "+str(ce.patch_stim_value))
            if not ce.monitor_xyY:
                f.write(", NA, NA, NA")
            else: 
                for x in ce.monitor_xyY:
                    f.write(", "+str(x))
            if not ce.monitor_xyY_sd:
                f.write(", NA, NA, NA")
            else:
                for x in ce.monitor_xyY_sd:
                    f.write(", "+str(x))
            if not ce.voltages:
                f.write(", NA, NA, NA")
            else:
                for x in ce.voltages:
                    f.write(", "+str(x))
            if not ce.tubes_xyY:
                f.write(", NA, NA, NA")
            else:
                for x in ce.tubes_xyY:
                    f.write(", "+str(x))
            if not ce.tubes_xyY_sd:
                f.write(", NA, NA, NA")
            else:
                for x in ce.tubes_xyY_sd:
                    f.write(", "+str(x))
            f.write("\n")


    def saveToPickle(self, filename):
        """
        saves object to pickle-file.
        """
        f = open(filename, "wb")
        pickle.dump(self.color_list, f)
        f.close()

    def loadFromR(self, filename):
        """
        loads object to R.
        """
        pass

    def loadFromCsv(self, filename):
        """
        loads object to comma sperated textfile.
        """
        pass

    def loadFromPickle(self, filename):
        """
        loads object to pickle-file.
        """
        f = open(filename, "rb")
        self.color_list = pickle.load(f)
        f.close()


if __name__ == "__main__":
    from EyeOne import EyeOne
    from psychopy import visual
    from monitor2 import Monitor
    from tubes2 import Tubes
    eye_one = EyeOne.EyeOne()#dummy=True)
    mywin = visual.Window(size=(2048,1536), monitor='mymon',
                    color=(0,0,0), screen=1)
    mon = Monitor(eye_one, mywin)
    tub = Tubes(eye_one)
 
    color_table = ColorTable(mon, tub)
    #color_table.loadFromPickle("./test_tino.pkl")
    #color_table.createColorList(patch_stim_value_list=[0.3,0.2])
    color_table.createColorList(
            patch_stim_value_list=[x/128.0 for x in range(-128,129)])
    color_table.saveToPickle("./color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".pkl")
    color_table.saveToCsv("./color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".csv")
    



