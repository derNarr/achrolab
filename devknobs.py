#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# devknobs.py
#
# (c) 2013 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content:
#
# input: --
# output: --
#
# created 2013-04-16 KS
# last mod 2013-04-16 16:26 KS

"""
Defines a class that encapsulates the triggering and reading out for the knobs
from the user.

"""

from __future__ import print_function

import time

from achrolab.wasco import wasco
from achrolab.wasco.constants import (AD_ADCONT, AD_ADDAT, AD_ADRANGE,
        AD_ADSTAT, AD_STARTCH, AD_SWTRIG, DAOUT1, RESETERRORFLAG,
        RESETFIFO)

class DevKnobs(object):
    """
    DevKnobs encapsulates all functions getting input from the knobs.

    Example
    -------

        >>> devknobs = DevKnobs(dummy=True)
        >>> states = devknobs.getStates()

    """
    def __init__(self, dummy=False):
        """
        Setting attributes.

        If dummy=True no wasco runtimelibraries will be loaded.

        """

        self.wasco_card = wasco.Wasco(dummy=dummy)    # create wasco object
        self.boardId = self.wasco_card.boardId

        self.channels = (("red", 62), ("green", 61), ("blue", 60), ("all", 63))
        self.reference_voltage = 0x800

        # initialize wasco card
        self.wasco_card.wasco_outportW(self.boardId, AD_ADCONT, 0x91) # A/D-Modus:
                                                            # Softwareauslösung
        self.wasco_card.wasco_outportW(self.boardId, AD_ADCONT, 0xB1) # PGA-Ansteuerung über
                                                            # Register AD_ADRANGE
        # MUX-Ansteuerung über Register AD_ADSTARTCH
        self.wasco_card.wasco_outportW(self.boardId, AD_ADRANGE, 0x1) # VPGA = 2, single ended
                                                            # vgl Seite 34 im
                                                            # Manual
        self.wasco_card.wasco_outportW(self.boardId, RESETERRORFLAG, 0x0)
        self.wasco_card.wasco_outportW(self.boardId, RESETFIFO, 0x0)
        self.wasco_card.wasco_outportW(self.boardId, DAOUT1, self.reference_voltage)

    def getStates(self):
        """
        returns (red, green, blue, all) as integer values between 0 and 0xFFF.

        Internally it triggers the measurement and reads out the values from
        the wasco card.

        """
        # trigger measurement
        for name, channel in self.channels:
            self.wasco_card.wasco_outportW(self.boardId, AD_STARTCH, channel)
            time.sleep(0.001)
            self.wasco_card.wasco_outportW(self.boardId, AD_SWTRIG, 0x0)
            time.sleep(0.001)
        values = list()
        # read out values
        for name, channel in self.channels:
            status = self.wasco_card.wasco_inportW(self.boardId, AD_ADSTAT) # check A/D-Status-Register
            if status:
                value = self.wasco_card.wasco_inportW(self.boardId, AD_ADDAT) # read A/D-Wert
                #print("Kanal: %02d  %4x Hex  %4.4f Volt\t" % (channel, value,
                #                                              -10 + value *
                #                                              0.004882812),
                #      end="")
                values.append(value)
                time.sleep(0.001)
            else:
                print(("\nA/D-Statusregister: %x") % status)
                values.append(None)
        # transform from (0x800, 0xFFF) -> (0x000, 0xFFF)
        return [(value - 0x800)*2 for value in values if value]


    @property
    def states(self):
        return self.getStates()

