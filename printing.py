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
# last mod 2012-07-11 19:08 KS


"""
This modules provides the class CalibDataFile, which provides a convenient
method of writing the calibration data to a comma separated file.

"""

import json #JSON format is used so comments can be saved
import time

#Fix inheriting from file later, need way of working with open()
class CalibDataFile():
    """
    CalibDataFile provides a new method to
    write the calibration data to a comma separated file.
    TODO add arguments, etc. here

    Use with closing() from the contextlib module as follows: ::

        from contextlib import closing
        import printing
        with closing(printing.CalibDataFile(prefix="YourPrefixHere")) as file_name:
            #code here
            filename.writeTXT(rgb=rgb, xyY=None, voltage=None, spec_list=spec_list, delimiter="\t")
            #more code

    This way if there is an error, inside the with context, it will immediately
    close and write to the file, so data is not lost.

    """

    def __init__(self, prefix=""):
        #For now only works with justmeasure, can generalise this later
        self.file_object=open(str(prefix) + time.strftime("%Y%m%d_%H%M") + ".txt", "w")
        #print "init"
        #Open file object here

    def writeDataJSON(self, grayvals=None, rgb=None, xyY=None, voltage=None, spec_list=None, measurement=None, imi=None, times=None, recalibrate=None):
        #Make list of dictionaries to do nested JSON
        #Needs to be modified to include all variables
        #Can this be modified to save data whilst running?
        # TODO code looks broken
        data = []
        i = 0
        color_list = grayvals
        for i in range(len(color_list)):
            data.append({"colorlist" : color_list[i], "speclist" : spec_list[i]})
            i+=1
        python_data = {
            "measurement" : measurement,
            "imi" : imi,
            "times" : times,
            "recalibrate" : recalibrate,
            "data": data
            }
        print(json.dumps(python_data, indent=4))
        #Write me to file

    #def writeDataCSV(self, listcolorlist, listspeclist, measurement, imi, times, recalibrate):

    def writeDataTXT(self, grayvals=None, rgb=None, xyY=None, voltage=None, spec_list=None, delimiter="\t"):
        #Fundamentally different to JSON, as can write to buffer on the fly - i.e. does not need complete structure to write
        #If at 0, write headers:
        if self.file_object.tell()==0:
            writestr="gray_1" + str(delimiter) + "gray_2" + str(delimiter) + "rgb_r"+str(delimiter)+"rgb_g"+str(delimiter)+"rgb_b"+str(delimiter)+"x"+str(delimiter)+"y"+str(delimiter)+"Y"+str(delimiter)+"voltage_r"+str(delimiter)+"voltage_g"+str(delimiter)+"voltage_b"
            for i in range(36):
                 writestr+=str(delimiter) +"l"+str(i+1)
            writestr+="\n"
            self.file_object.write(writestr)

        writestr = ""
        # Write grayvals from 2 element list
        if grayvals != None:
            for i in range(2):
                writestr+=str(grayvals[i])+str(delimiter)
        else:
            for i in range(2):
                writestr+="NA"+str(delimiter)

        #Write RGB values from 3 element list (should really be tuple as different data)
        if rgb != None:
            for i in range(3):
                writestr+=str(rgb[i])+str(delimiter)
        else:
            for i in range(3):
                writestr+="NA"+str(delimiter)

        #Write xyY values from 3 element list (should really be tuple as different data)
        if xyY != None:
            for i in range(3):
                writestr+=str(xyY[i])+str(delimiter)
        else:
            for i in range(3):
                writestr+="NA"+str(delimiter)

        #Write voltage_{r,g,b} values from 3 element list (should really be tuple as different data)
        if voltage != None:
            for i in range(3):
                writestr+=str(voltage[i])+str(delimiter)
        else:
            for i in range(3):
                writestr+="NA"+str(delimiter)

          #Write spectral values from 36 element list
        if spec_list != None:
            for i in range(36):
                writestr+=str(spec_list[i])+str(delimiter)
        else:
            for i in range(36):
                writestr+="NA"+str(delimiter)
            writestr=writestr[:-1] #remove trailing delimiter
        #Terminate record with newline
        writestr+="\n"
        self.file_object.write(writestr)

        #rgb_r rgb_g rgb_b x y Y  voltage_r voltage_g voltage_b l1 l2 l3 ...
        #NA    NA    NA    0.2 ...

        #"{rgb_r}  {}".format(rgb_r="NA", ...
        #                 " ".join(list of strings)

    def close(self):
        self.file_object.close()

class ExperimentDataFile():
    def __init__(self, expInfo):
        #For now only works with justmeasure, can generalise this later
        self.fileName = expInfo['Versuchsleiter'] + expInfo['Versuchsperson'] + expInfo['Session'] + '_' + expInfo['Datum']
        self.file_object=open(self.filename + ".txt", "w")
        #print "init"
        #Open file object here

    def writeDataTXT(self, stimuliName=None, leftmean=None, leftvar=None, leftgrayplus=None, rightmean=None, rightvar=None, rightgrayplus=None, bg=None, voltages=None, rtTime=None, key=None, thisResp=None, delimiter="\t"):
        #Fundamentally different to JSON, as can write to buffer on the fly - i.e. does not need complete structure to write
        #If at 0, write headers:

        #thisResp, rtTime, key, stimuliname, leftmean, leftvar, rightmean, rightvar, leftgreyplus, rightgreyplus, bg
        if self.file_object.tell()==0:
            writestr="stimuliName" + str(delimiter) + "leftmean" + str(delimiter) + "leftvar"+str(delimiter)+"leftgrayplus"+str(delimiter)+"rightmean"+str(delimiter)+"rightvar"+str(delimiter)+"rightgrayplus"+str(delimiter)+"bgR"+str(delimiter)+"bgG"+str(delimiter)+"bgB"+str(delimiter)+"voltageR"+str(delimiter)+"voltageG"+str(delimiter)+"voltageB"+str(delimiter)+"rtTime"+str(delimiter)+"key"+str(delimiter)+"thisResp"
            writestr+="\n"
            self.file_object.write(writestr)

        writestr = ""
        # Write grayvals from 2 element list
        if stimuliName != None:
            writestr+=str(stimuliName)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if leftmean != None:
            writestr+=str(leftmean)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if leftvar != None:
            writestr+=str(leftvar)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if leftgrayplus != None:
            writestr+=str(leftgrayplus)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if rightmean != None:
            writestr+=str(rightmean)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if rightvar != None:
            writestr+=str(rightvar)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if rightgrayplus != None:
            writestr+=str(rightgrayplus)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if bg != None:
            for i in range(3):
                writestr+=str(bg[i])+str(delimiter)
        else:
            for i in range(3):
                writestr+="NA"+str(delimiter)

        if voltages != None:
            for i in range(3):
                writestr+=str(voltages[i])+str(delimiter)
        else:
            for i in range(3):            
                writestr+="NA"+str(delimiter)                

        if rtTime != None:
            writestr+=str(rtTime)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if key != None:
            writestr+=str(key)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

        if thisResp != None:
            writestr+=str(thisResp)+str(delimiter)
        else:
            writestr+="NA"+str(delimiter)

            writestr=writestr[:-1] #remove trailing delimiter
        #Terminate record with newline
        writestr+="\n"
        self.file_object.write(writestr)

    def close(self):
        self.file_object.close()
