#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# monitor.py
#
# (c) 2012 Konstantin Sering <konstantin.sering [aet] gmail.com>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: (1) class Monitor
#
# input: --
# output: --
#
# created 2012-05-29 KS
# last mod 2013-04-16 16:02 KS

"""
This module provides the class Monitor, which encapsulates the presentation
of a color stimuli on the monitor.

It is deprecated to use any other code than this in order to present one
color and collect key presses.

"""

from psychopy import visual, event, core

class Event(object):
    """
    Very small class to store a key stroke.

    """

    def __init__(self):
        """
        Add attribute key.

        """
        self.key = ""


class Monitor(object):
    """
    Provides a convenient interface to present a color on the monitor and
    get key strokes.

    Example:

    >>> mon = Monitor()
    >>> mon.setColor("#00FF00FF")

    """

    def __init__(self, psychopy_win=None):
        self.psychopy_win = psychopy_win
        if not psychopy_win:
            self.psychopy_win = visual.Window(size=(800, 600))
        self.patch_stim = visual.GratingStim(self.psychopy_win, tex=None,
                size=(2, 2), color=0, colorSpace="rgb255")
        self.e = Event() # small object storing one key

    def setColor(self, psychopy_color, colorSpace="rgb255"):
        """
        Presents one color at the monitor.

        """
        self.patch_stim.setColor(psychopy_color, colorSpace=colorSpace)
        self.patch_stim.draw()
        self.psychopy_win.flip()

    def waitForButtonPress(self):
        """
        Waits for a key press and stores button press in self.e.key.

        """
        event.clearEvents()
        self.e.key = ""
        while not self.e.key:
            core.wait(0.01)
            keys = event.getKeys()
            if keys:
                self.e.key = keys[0]

    def checkForButtonPress(self):
        """
        Checks for a key press and stores key press in self.e.key.

        """
        self.e.key = ""
        core.wait(0.01)
        keys = event.getKeys()
        if keys:
            self.e.key = keys[0]
        event.clearEvents()

