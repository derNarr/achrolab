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
# last mod 2013-01-29 11:19 KS

import pickle
import exceptions

from colorentry import ColorEntry

# TODO save measurements of each EyeOne Pro measurement in a folder
# ./measurements/ with date (as R-Datafile)

class ColorTable(object):
    """
    ColorTable stores colors in xyY coordinates and all data needed for
    psychopy.visual.GratingStim, the monitor, and the tubes.

    The colors in ColorTable are indexed. So there is a first and a last
    color.

    ColorTable is a list of ColorEntries with some useful functions defined
    on this list.

    Example:

    >>> from colorentry import ColorEntry
    >>> coltab = ColorTable()
    >>> coltab.addColorEntry(ColorEntry("grey1",
    ...    patch_stim_value="#505050FF"))
    >>> ce = coltab.getColorByName("grey1")
    >>> print(ce.patch_stim_value)
    #505050FF

    """

    def __init__(self, filename=""):
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
                raise exceptions.ValueError("Cannot load ColorTable. Wrong \
                        filetype.")

    def addColorEntry(self, ce):
        """
        Adds a color entry to the color table.

        Parameters:
            ce: colorentry.ColorEntry instance
                object that stores a color entry

        """
        if not isinstance(ce, ColorEntry):
            raise ValueError("ce must be colorentry.ColorEntry instance")
        self.color_list.append( ce )

    def getColorByName(self, name):
        """
        Returns the first object in color_list with the given name.

        Parameters:
            name: string
                name of colorentry.ColorEntry object

        Returns:
            out: ColorEntry
                first object in color_list with the given name.

        """
        for ce in self.color_list:
            if ce.name == name:
                return ce
        raise exceptions.ValueError("No color for this name")

    def getColorsByName(self, names):
        """
        Returns ColorEntry objects in a list, ordered after name_list.

        Parameters:
            names: sequence of strings
                list with names of colorentry.ColorEntry objects

        Returns:
            out: sequence of ColorEntry objects
                list with colorentry.ColorEntry objects corresponding to
                the names given in names

        """
        color_entries = []
        for name in names:
           color_entries.append(self.getColorByName(name))
        return color_entries

    def saveToCsv(self, filename):
        """
        Saves object to comma separated text file (.csv).

        Parameters:
            filename: string
                string that gives the filename and the location of the file.

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

        Parameters:
            filename: string
                string that gives the filename and the location of the file.

        """
        with open(filename, "wb") as f:
            pickle.dump(self.color_list, f)

    def loadFromCsv(self, filename):
        """
        Loads object from comma separated text file (.csv).

        Parameters:
            filename: string
                string that gives the filename and the location of the file.

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
        Loads object from pickle file (.pkl).

        Parameters:
            filename: string
                string that gives the filename and the location of the file.

        """
        with open(filename, "rb") as f:
            self.color_list = pickle.load(f)

    def loadFromR(self, filename):
        """
        Loads object from R data file.

        Parameters:
            filename: string
                string that gives the filename and the location of the file.

        """
        raise exceptions.NotImplementedError("not implemented to load from Rdata file")
        # TODO implement loadFromR

