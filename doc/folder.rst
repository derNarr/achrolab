.. _achrolab_folder:

Folder structure
================

.. highlight:: text

Schematic folder overview of the python package *achrolab*::

     achrolabutils (useful scripts)
     |
     +--achrolab (main classes and interfaces to use in the lab)
         |
         +--eyeone (wrapper for i1 Pro photometer)
         |
         +--wasco (wrapper for wasco multifunction card)

achrolabutils
~~~~~~~~~~~~~

This folder contains all scripts that we use to run our :ref:`color
laboratory <colorlab_colorlab>`. In this folder you will find all scripts
that actually do things like :doc:`calibrating the booth <tutorial>`,
adjusting tubes, showing certain colors and so on. One might want to use
these scripts as examples on how to use the functions of *achrolab*.
(Except for the people working in our lab. They will want to actually use
these scripts.)

achrolab
~~~~~~~~

This folder contains the actual python package. It depends on two
submodules: `eyeone` and `wasco` (see below). Apart from that there are two
folders that are used by the package:

1. **calibdata** stores all files obtained during measurements; scripts in
   achrolabutils will put all measurements they conduct to the folder
   *calibdata/measurements* and figures that are created into
   *calibdata/figures*. You might want to clean out this folder on a regular
   basis (e.g., before the next calibration).
2. **tests** contains all files for unit testing the :doc:`classes of
   achrolab <classes>`.

eyeone
~~~~~~

In this folder you will find all files of the submodule `eyeone`. This
package is responsible for controlling the :ref:`i1 Pro photometer
<colorlab_photometer>` that we use. This module is independent. It can be
used as a python interface for the i1 Pro without any of the other
packages we use here.

wasco
~~~~~

This is the submodule that gives us an interface to the ADIODA-PCIF12 MDA
PCI multifunction card that we use to control the tubes. Again, this module
is independent. One should keep in mind that this card can be applied to
different purposes and our implementation might be special for our setting.

