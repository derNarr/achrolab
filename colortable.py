#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./colortable.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-05-11, KS

from psychopy import event, core
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

    def checkColorTable(self, index_list=None, name_list=None):
        """
        checkColorTable checks if the color entries are still consistent. It
        measures the color of the monitor and the tubes and compares the
        measurements with the saved values.
	* index_list (List) -- List with the color indexes: [100,101,...]
        """
        print("""WARNING ColorTable.checkColorTable not implemented yet.
                Use ColorTable.checkColorTableTubes at the moment.""")
        if index_list:
            diff_list_tubes = checkColorTableTubes(index_list=index_list)
            diff_list_monitor = checkColorTableMonitor(index_list=index_list)
            diff_list = []
            for i in len(index_list):
	      diff_list.append((index_list[i], diff_list_tubes[i][1:4], diff_list_monitor[i][1:4]))
            return diff_list
        else:
            print("""WARNING ColorTable.checkColorTable not
                    implemented for this way of usage.""")
            pass

    def checkColorTableTubes(self, index_list=None, name_list=None):
        """
        checkColorTableTubes checks if the color entries for the tubes are
        still consistent. It measures the color of the tubes and compares the
        measurements with the saved values.

        returns a list of transformed differences ((d_x, d_y, d_Y), ...).
        The differences are defined as d_x = (x-x')/x_sd where x
        is the old, stored value and x' is the new, measured value.
        """
        if index_list:
            diff_list = []
            # write txt, which can be used for further analysis in R
            f = open("data/checkColorTableTubes_%Y%m%d_%H%M.txt", "w")
            f.write("name, d_x, d_y, d_Y\n")
            for idx in index_list:
                ce = self.color_list[idx] #ce = ColorEntry(-object)
                # extract xyY values
                xyY = ce.tubes_xyY
                xyY_sd = ce.tubes_xyY_sd
                new_xyY, new_xyY_sd = ce.measureTubes(return_only=True)
                # calculate (x - x') / sd(x) and store in diff_list
                diff_list.append( [(xyY[j] - new_xyY[j])/xyY_sd[j] for j in
                   range(3)] )
                # write results in file
                f.write(ce.name)
                for x in diff_list[-1]:
                    f.write(", " + str(x))
		f.write("\n")
            f.close()
            return diff_list
	else:
            print("""WARNING ColorTable.checkColorTableTubes not
                    implemented for this way of usage.""")
            pass
    
    def checkColorTableMonitor(self, index_list=None, name_list=None):
        """
        checkColorTableMonitor checks if the color entries for the monitor are
        still consistent. It measures the color of the monitor and compares the
        measurements with the saved values.

        returns a list of transformed differences ((d_x, d_y, d_Y), ...).
        The differences are defined as d_x = (x-x')/x_sd where x
        is the old, stored value and x' is the new, measured value.
        """
        if index_list:
            diff_list = []
            # write txt, which can be used for further analysis in R
            f = open("data/checkColorTableMonitor_%Y%m%d_%H%M.txt", "w")
            f.write("name, d_x, d_y, d_Y\n")
            for idx in index_list:
                ce = self.color_list[idx] #ce = ColorEntry(-object)
                # extract xyY values
                xyY = ce.monitor_xyY
                xyY_sd = ce.monitor_xyY_sd
                new_xyY, new_xyY_sd = ce.measureTubes(return_only=True) # measureTubes with return_only=True can be used to measure the monitor and immediatly return the values
                # calculate (x - x') / sd(x) and store in diff_list
                diff_list.append( [(xyY[j] - new_xyY[j])/xyY_sd[j] for j in
                   range(3)] )
                # write results in file
                f.write(ce.name)
                for x in diff_list[-1]:
                    f.write(", " + str(x))
                f.write("\n")
            f.close()
            return diff_list
        else:
            print("""WARNING ColorTable.checkColorTableMonitor not
                    implemented for this way of usage.""")
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


    def measureColorListMonitor(self):
        """
        measures the monitor for every colorentry in colorlist and
        overwrites the monitor entries in the colorentry
        """
        self.monitor.calibrateEyeOne()
        self.monitor.startMeasurement()
        for colorentry in self.color_list:
            colorentry.measureMonitor(self.monitor, n=10)

    def findVoltages(self, name_list=None):
        #self.tubes.calibrateEyeOne()
        self.tubes.startMeasurement()
        if name_list:
            color_dict = {}
            for ce in self.color_list:
                color_dict[ce.name] = ce
            for name in name_list:
                color_dict[name].findVoltages(self.tubes)
        else:
            for ce in self.color_list:
                ce.findVoltages(self.tubes)

    def findVoltagesTuning(self, name_list=None):
        #self.tubes.calibrateEyeOne()
        self.tubes.startMeasurement()
        if name_list:
            color_dict = {}
            for ce in self.color_list:
                color_dict[ce.name] = ce
            for name in name_list:
                color_dict[name].findVoltagesTuning(self.tubes)
        else:
            for ce in self.color_list:
                ce.findVoltagesTuning(self.tubes)


    def measureColorListTubes(self):
        """
        measures the tubes for every colorentry in colorlist and
        overwrites the tubes' entries in the colorentry
        """
        #self.tubes.calibrateEyeOne()
        self.tubes.startMeasurement()
        for colorentry in self.color_list:
            colorentry.tubes_xyY = None
            colorentry.tubes_xyY_sd = None
            colorentry.measureTubes(self.tubes, n=10)


    def showColorList(self, index_list=None, name_list=None):
        """
        draws every color on the screen and changes the illumination of the
        tubes to the corresponding voltage. Left mouse click changes to the
        next color in color list.
        """
        # TODO implement index_list 
        print('''Click the left mouse button to move to the next
        corresponding colors of the tubes and monitor.''')
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
            self.monitor.setPatchStimColor(colorentry.patch_stim_value)
            self.tubes.setVoltages(colorentry.voltages)
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
	f.close()


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
    from monitor import Monitor
    from tubes import Tubes
    eye_one = EyeOne.EyeOne()#dummy=True)
    mywin = visual.Window(size=(2048,1536), monitor='mymon',
                    color=(0,0,0), screen=1)
    mon = Monitor(eye_one, mywin)
    tub = Tubes(eye_one)
    tub.calibrateEyeOne()

    #interessting colors
    color_list = []
    for i in range(20):
        color_list.append( "color" + str(160 + i) )
 
    color_table = ColorTable(mon, tub)
    color_table.loadFromPickle("./data/color_table_20101209_1220.pkl")
    #color_table.loadFromPickle("./data/color_table_20101209_2042.pkl")
    #color_table.loadFromPickle("./data/color_table_20101123_2024.pkl")
    #color_table.createColorList(patch_stim_value_list=[0.3,0.2])
    #color_table.createColorList(
    #        patch_stim_value_list=[x/127.5 - 1 for x in range(0,256)])

    #color_table.measureColorListMonitor()
    color_table.findVoltages(name_list=color_list)
    color_table.saveToPickle("./data/color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".pkl")
    color_table.saveToCsv("./data/color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".csv")

    color_table.findVoltagesTuning(name_list=color_list)
    #color_table.measureColorListTubes()
    color_table.saveToPickle("./data/color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".pkl")
    color_table.saveToCsv("./data/color_table_" + 
            time.strftime("%Y%m%d_%H%M") +".csv")
    #color_table.showColorList(name_list=color_list)

    #color_table.showColorList()
    



