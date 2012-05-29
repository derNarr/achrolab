#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colortable.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: a list of ColorEntry objects with functions
#
# input: --
# output: --
#
# created 2010
# last mod 2012-05-29 KS

from psychopy import event, core
from colorentry import ColorEntry
import pickle,time
from exceptions import ValueError

# TODO save measurements of each EyeOne Pro measurement in a folder
# ./measurements/ with date (as R-Datafile)

class ColorTable(object):
    """
    ColorTable stores colors in xyY coordinates and all data needed for
    psychopy.visual.PatchStim, the monitor, and the tubes.

    The colors in ColorTable are indexed. So there is a first and a last
    color. 

    ColorTable is a list of ColorEntries with some useful functions defined
    on this list.
    """

    def __init__(self, filename=False):
        self.color_list = []
        if filename:
            filetype = filename.split(".")[-1]
            if filetype == "pkl":
                self.loadFromPickle(filename)
            elif filetype == "csv":
                self.loadFromCsv(filename)
            elif filetype in ("RData", "rdata", "Rdata", "R", "RDat", "rdat",
                    "Rdat"):
                self.loadFromR(filename)
            else:
                print("Warning: Cannot load ColorTable. Wrong filetype.")


    def getColorByName(self,name):
        """
        returns the first object in color_list with the given name

            * name -- name of colorentry object
        """
        for ce in self.color_list:
            if ce.name == name:
                return ce
        raise ValueError("No color for this name")

    def getColorsByName(self,name_list):
        """
        returns colorentry objects in a list, ordered after name_list

            * name_list -- list with names of colorentry objects
        """
        color_list = []
        for name in name_list:
           color_list.append(self.getColorByName(name))
        return color_list

    def showColorList(self, tubes, monitor, index_list=None, name_list=None):
        """
        draws every color on the screen and changes the illumination of the
        tubes to the corresponding voltage. Left mouse click changes to
        next color in color list.
        """
        # TODO implement index_list 
        print('''Click left mouse button to move to the next
        corresponding colors of tubes and monitor.''')
        color_list = []
        if name_list:
            color_dict = {}
            for ce in self.color_list:
                color_dict[ce.name] = ce
            for name in name_list:
                color_list.append(color_dict[name])
        else:
            color_list = self.color_list

        for colorentry in color_list:
            monitor.setPatchStimColor(colorentry.patch_stim_value)
            tubes.setVoltages(colorentry.voltages)
            mouse = event.Mouse(win=self.monitor.psychopy_win) 
            event.clearEvents()
            show = True 
            print("Show color " + colorentry.name + ".")
            while show:
                core.wait(0.01)
                left, middle, right = mouse.getPressed()
                if left: 
                    core.wait(0.2)
                    show=False
        print("Finished showing all colors.")

    def saveToCsv(self, filename):
        """
        Saves object to comma separated text file (.csv).
        """
        with open(filename, "w") as f:
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
        Saves object to pickle file (.pkl).
        """
        with open(filename, "wb") as f:
            pickle.dump(self.color_list, f)

    def loadFromCsv(self, filename):
        """
        Loads object to comma separated text file (.csv).
        """
        def float_None(x):
            if x=="NA":
                return None
            else:
                return float(x)
        with open(filename, "r") as f:
            f.readline() 
            currentline = f.readline()
            while currentline:
                currentline = currentline.split(',')
                currentline = [x.strip() for x in currentline]
                ce = ColorEntry(currentline[0])
                ce.patch_stim_value = float_None(currentline[1])
                ce.monitor_xyY = (float_None(currentline[2]),
                                  float_None(currentline[3]),
                                  float_None(currentline[4]))
                ce.monitor_xyY_sd = (float_None(currentline[5]),
                                     float_None(currentline[6]),
                                     float_None(currentline[7]))
                ce.voltages = (float_None(currentline[8]),
                               float_None(currentline[9]),
                               float_None(currentline[10]))
                ce.tubes_xyY = (float_None(currentline[11]),
                                float_None(currentline[12]),
                                float_None(currentline[13]))
                ce.tubes_xyY_sd = (float_None(currentline[14]),
                                   float_None(currentline[15]),
                                   float_None(currentline[16]))
                self.color_list.append(ce)
                currentline = f.readline()

    def loadFromPickle(self, filename):
        """
        Loads object to pickle file (.pkl).
        """
        with open(filename, "rb") as f:
            self.color_list = pickle.load(f)


