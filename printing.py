#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# printing.py
# (c) 2012 James McMurray, Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content:
#
# input: --
# output: --
#
# created 2012-05-29 JM
# last mod 2013-01-22 14:12 KS


"""
This modules provides the class CalibDataFile, which provides a convenient
method of writing the calibration data to a comma separated file.

"""

#import json #JSON format is used so comments can be saved
import time

#Fix inheriting from file later, need way of working with open()
class CalibDataFile(object):
    """
    Provides a new method to write the calibration data of the
    monitor/photometer to a comma separated file.

    Example:

    >>> import printing
    >>> with printing.CalibDataFile(prefix="YourPrefixHere",
    ...             delimiter="\t") as filename:
    >>>     #code here
    >>>     filename.write_data_txt(rgb=rgb, xyY=None, voltage=None,
    ...             spec_list=spec_list)
    >>>     #more code

    If there is an error inside the with context, it will immediately close
    and write to the file, so data are not lost.

    """
    def __init__(self, prefix="calibdata_", file_type="txt", delimiter="\t"):
        """
        Parameters:
            prefix: str
                file name prefix

            file_type: str
                one of "txt"...
                not used at the moment

            delimiter: str
                delimiter which separates the values

        """
        self.file_type = file_type
        self.delimiter = delimiter
        #For now only works with justmeasure, can generalise this later
        self.file_object = open(str(prefix) + time.strftime("%Y%m%d_%H%M")
                + ".txt", "w")

    def __enter__(self):
        """
        Print header to file_object.

        When entering a context, print the header to the file_object.

        """
        delimiter = self.delimiter
        if self.file_type == "txt":
            writestr = ("gray_1" + str(delimiter) + "gray_2" +
                    str(delimiter) + "rgb_r" + str(delimiter) + "rgb_g" +
                    str(delimiter) + "rgb_b" + str(delimiter) + "x" +
                    str(delimiter)+"y" + str(delimiter) + "Y" +
                    str(delimiter) + "voltage_r" + str(delimiter) +
                    "voltage_g" + str(delimiter) + "voltage_b")
            for i in range(36):
                writestr += str(delimiter) + "l" + str(i+1)
            writestr += "\n"
            self.file_object.write(writestr)
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    # def writeDataJSON(self, grayvals=None, rgb=None, xyY=None,
    # voltage=None, spec_list=None, measurement=None, imi=None, times=None,
    # recalibrate=None):
    #     #Make list of dictionaries to do nested JSON
    #     #Needs to be modified to include all variables
    #     #Can this be modified to save data whilst running?
    #     # TODO code looks broken
    #     data = []
    #     i = 0
    #     color_list = grayvals
    #     for i in range(len(color_list)):
    #         data.append({"colorlist" : color_list[i], "speclist" :
    #         spec_list[i]})
    #         i += 1
    #     python_data = {
    #         "measurement" : measurement,
    #         "imi" : imi,
    #         "times" : times,
    #         "recalibrate" : recalibrate,
    #         "data": data
    #         }
    #     print(json.dumps(python_data, indent=4))
    #     #Write me to file


    def write_data_txt(self, grayvals=None, rgb=None, xyY=None, voltage=None,
            spec_list=None, delimiter="\t"):
        # Fundamentally different to JSON, as can write to buffer on the fly
        #  - i.e. does not need complete structure to write
        writestr = ""
        delimiter = self.delimiter
        # Write grayvals from 2 element list
        if grayvals != None:
            for i in range(2):
                writestr += str(grayvals[i])+str(delimiter)
        else:
            for i in range(2):
                writestr += "NA"+str(delimiter)

        # Write RGB values from 3 element list (should really be tuple as
        # different data)
        if rgb != None:
            for i in range(3):
                writestr += str(rgb[i])+str(delimiter)
        else:
            for i in range(3):
                writestr += "NA"+str(delimiter)

        # Write xyY values from 3 element list (should really be tuple as
        # different data)
        if xyY != None:
            for i in range(3):
                writestr += str(xyY[i])+str(delimiter)
        else:
            for i in range(3):
                writestr += "NA"+str(delimiter)

        # Write voltage_{r,g,b} values from 3 element list (should really
        # be tuple as different data)
        if voltage != None:
            for i in range(3):
                writestr += str(voltage[i])+str(delimiter)
        else:
            for i in range(3):
                writestr += "NA"+str(delimiter)

        # Write spectral values from 36 element list
        if spec_list != None:
            for i in range(36):
                writestr += str(spec_list[i])+str(delimiter)
        else:
            for i in range(36):
                writestr += "NA"+str(delimiter)
            writestr = writestr[:-1] #remove trailing delimiter
        #Terminate record with newline
        writestr += "\n"
        self.file_object.write(writestr)

        #rgb_r rgb_g rgb_b x y Y  voltage_r voltage_g voltage_b l1 l2 l3 ...
        #NA    NA    NA    0.2 ...

        #"{rgb_r}  {}".format(rgb_r="NA", ...
        #                 " ".join(list of strings)

    def write(self, text):
        self.file_object(text)

    def close(self):
        self.file_object.close()


class TubesDataFile(object):
    """
    Provides a new method to write the calibration of the tubes data to a
    comma separated file.

    Example:

    >>> import printing
    >>> with printing.CalibDataFile(prefix="YourPrefixHere",
    ...             delimiter="\t") as filename:
    >>>     #code here
    >>>     filename.write_data_txt(rgb=rgb, xyY=None, voltage=None,
    ...             spec_list=spec_list)
    >>>     #more code

    If there is an error inside the with context, it will immediately close
    and write to the file, so data are not lost.

    """
    def __init__(self, prefix="measure_tubes_", delimiter="\t"):
        """
        Parameters:
            prefix: str
                file name prefix

            delimiter: str
                delimiter which separates the values

        """
        self.delimiter = delimiter
        self.file_object = open(str(prefix) + time.strftime("%Y%m%d_%H%M")
                + ".txt", "w")

    def __enter__(self):
        """
        Print header to file_object.

        When entering a context, print the header to the file_object.

        """
        delimiter = self.delimiter
        writestr = ("x" + str(delimiter) + "y" + str(delimiter) + "Y" +
                str(delimiter) + "voltage_r" + str(delimiter) + "voltage_g"
                + str(delimiter) + "voltage_b")
        for i in range(36):
            writestr += str(delimiter) + "l" + str(i+1)
        writestr += "\n"
        self.file_object.write(writestr)
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def write_data_txt_loop(self, xyY=None, voltage=None, spec_list=None):
        delimiter = self.delimiter
        # Fundamentally different to JSON, as can write to buffer on the fly
        # - i.e. does not need complete structure to write
        # If at 0, write headers:
        for p in range(len(xyY)):
            if self.file_object.tell() == 0:
                writestr = ("x" + str(delimiter) + "y" + str(delimiter) +
                        "Y" + str(delimiter) + "voltage_r" + str(delimiter)
                        + "voltage_g" + str(delimiter) + "voltage_b")
                for i in range(36):
                    writestr += str(delimiter) + "l" + str(i+1)
                writestr += "\n"
                self.file_object.write(writestr)

            writestr = ""

            # Write xyY values from 3 element list (should really be tuple
            # as different data)
            if xyY != None:
                for i in range(3):
                    writestr += str(xyY[p][i]) + str(delimiter)
            else:
                for i in range(3):
                    writestr += "NA" + str(delimiter)

            # Write voltage_{r,g,b} values from 3 element list (should
            # really be tuple as different data)
            if voltage != None:
                for i in range(3):
                    writestr += str(voltage[p][i]) + str(delimiter)
            else:
                for i in range(3):
                    writestr += "NA" + str(delimiter)

            # Write spectral values from 36 element list
            if spec_list != None:
                for i in range(36):
                    writestr += str(spec_list[p][i])+str(delimiter)
            else:
                for i in range(36):
                    writestr += "NA"+str(delimiter)
                writestr=writestr[:-1] #remove trailing delimiter
            # Terminate record with newline
            writestr += "\n"
            self.file_object.write(writestr)

            #rgb_r rgb_g rgb_b x y Y  voltage_r voltage_g voltage_b l1 l2 l3 ...
            #NA    NA    NA    0.2 ...

            #"{rgb_r}  {}".format(rgb_r="NA", ...
            #                 " ".join(list of strings)

    def write_data_txt(self, xyY=None, voltage=None, spec_list=None):
        delimiter = self.delimiter
        # Fundamentally different to JSON, as can write to buffer on the
        # fly - i.e. does not need complete structure to write
        writestr = ""

        # Write xyY values from 3 element list (should really be tuple as
        # different data)
        if xyY != None:
            for i in range(3):
                writestr += str(xyY[i])+str(delimiter)
        else:
            for i in range(3):
                writestr += "NA"+str(delimiter)

        # Write voltage_{r,g,b} values from 3 element list (should really
        # be tuple as different data)
        if voltage != None:
            for i in range(3):
                writestr += str(voltage[i])+str(delimiter)
        else:
            for i in range(3):
                writestr += "NA"+str(delimiter)

        # Write spectral values from 36 element list
        if spec_list != None:
            for i in range(36):
                writestr += str(spec_list[i])+str(delimiter)
        else:
            for i in range(36):
                writestr += "NA"+str(delimiter)
            writestr=writestr[:-1] # remove trailing delimiter
        # Terminate record with newline
        writestr += "\n"
        self.file_object.write(writestr)

        #rgb_r rgb_g rgb_b x y Y  voltage_r voltage_g voltage_b l1 l2 l3 ...
        #NA    NA    NA    0.2 ...

        #"{rgb_r}  {}".format(rgb_r="NA", ...
        #                 " ".join(list of strings)

    def write(self, text):
        self.file_object(text)

    def close(self):
        self.file_object.close()

