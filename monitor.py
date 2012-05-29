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
# last mod 2012-05-29 KS

"""
This module provides the class Monitor, which capsulates the presentation
of a color stimuli on the monitor.

It is deprecated to use any other code than this 
"""

from psychopy import visual

class Monitor(object):
    """
    Monitor provides a convenient interface to present a color on the
    monitor.
    """

    def __init__(self, psychopy_win=None):
        self.psychopy_win = psychopy_win
        if not psychopy_win:
            self.psychopy_win = visual.Window(size=(800,600))

        self.patch_stim = visual.PatchStim(self.psychopy_win, tex=None,
                size=(2, 2), color=0, colorSpace="rgb255")

    def setColor(self, psychopy_color, colorSpace="rgb255"):
        """
        presents one color at the monitor.
        """
        self.patch_stim.setColor(psychopy_color, colorSpace=colorSpace)
        self.patch_stim.draw()
        self.psychopy_win.flip()

