#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./visionlab-utils/iterativColorTubes.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
#     and Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-13-01, DW

import pyglet
from EyeOne import EyeOne
from psychopy import visual
from monitor2 import Monitor
from tubes2 import Tubes
from colortable import ColorTable
eye_one = EyeOne.EyeOne(dummy=True)
mywin = visual.Window(size=(2048,1536), monitor='mymon',
                    color=(0,0,0), screen=1)
mon = Monitor(eye_one, mywin)
tub = Tubes(eye_one)

win = pyglet.window.Window()
color_table = ColorTable(mon, tub)
color_table.loadFromPickle("./data/color_table_20101209_1220.pkl")

color_entry = color_table.color_list[170] #TODO welchen Farbwert noch manuell einstellen
# TODO erledigt - über startvoltages kann der Farbwert manuell eingestellt werden (siehe Funktion setTubesManual)

voltages = list(color_entry.voltages)

# Variables are pre-defined to avoid Errors, can be changed in the program l8ter
colortube = ('red', 0)
step = 10

def getKey(symbol):
    """
    returns the key for certain symbol-codes
    """
    if symbol == 114:
        key = 'r'
    elif symbol == 103:
        key = 'g'
    elif symbol == 98:
        key = 'b'
    elif symbol == 49:
        key = '1'
    elif symbol == 50:
        key = '2'
    elif symbol == 51:
        key = '3'
    elif symbol == 52:
        key = '4'
    elif symbol == 53:
        key = '5'
    elif symbol == 65362:
        key = 'arrowup'
    elif symbol == 65364:
        key = 'arrowdown'
    else:
        key = 'ERROR'
    return key

def setColorTube(key):
    """
    Defines which colortube should be changed.
    """
    if key == 'r':
        return ('red', 0)
    elif key == 'g':
        return ('green', 1)
    elif key == 'b':
        return ('blue', 2)
    else:
        pass

def setStepSize(key):
    """
    Defines the stepsize of the change.
    """
    if key == '1':
        return 1
    elif key == '2':
        return 10
    elif key == '3':
        return 50
    elif key == '4':
        return 200
    elif key == '5':
        return 500
    else:
        pass
    
def adjustTube(key, tubes, voltages, colortube, step):
    """
    Enables up and down arrow to adjust the colortubes by step (lower if down and higher if up).
    """
    if key == 'arrowup':
        voltages[colortube[1]] = voltages[colortube[1]] + step
        tubes.setVoltages(voltages)
        print('Adjusted ' + colortube[0] + ' colortube voltage higher by ' + str(step))
    elif key == 'arrowdown':
        voltages[colortube[1]] = voltages[colortube[1]] - step
        tubes.setVoltages(voltages)
        print('Adjusted ' + colortube[0] + ' colortube voltage lower by ' + str(step))
    else:
        pass

def setTubesManual(startvoltages):
    """
    Start the Program to set Tubes by hand.
    """
    print('Manual adjustment of the colortubes\n\n' +
          'Press [arrowup] for higher intensity ' +
          'or press [arrowdown] for lower intensity.\n' +
          'To set the colortube and the stepsize press following buttons:\n' +
          'Stepsize:\n [1] - 1\n [2] - 10\n [3] - 50\n [4] - 200\n [5] - 500' +
          'Colortube:\n [R] - Red\n [G] - Green\n [B] - Blue')
    tub.setVoltages(startvoltages)
    pyglet.app.run()

@win.event
def on_key_press(symbol, modifiers):
    
    #print(symbol)
    global step
    global colortube
    key = getKey(symbol)
    print(key)
    if key == 'r' or key == 'g' or key == 'b':
        colortube = setColorTube(key)
        print('Colortube ' + colortube[0] + ' ready for adjustment.')
    elif key == '1' or key == '2' or key == '3' or key == '4' or key == '5':
        step = setStepSize(key)
        print('Stepsize set to ' + str(step))
    else:
        adjustTube(key, tub, voltages, colortube, step)
            
if __name__ == "__main__":

    setTubesManual(voltages)
    
