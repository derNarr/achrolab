.. _achrolab_experiments:

How to Use in Experiments
=========================

We now want to use the colors we defined when calibrating our booth (See
:doc:`tutorial`).

We use `psychopy <http://www.psychopy.org/>`_ to present our stimuli. Of
course, there might be other choices. But all the monitor measurements of
achrolab are based on psychopy or more precisely on
`psychopy.visual.GratingStim
<http://www.psychopy.org/api/visual/gratingstim.html>`_.

First, you might want to tell python where it can find the package
*achrolab*.

>>> import sys
>>> sys.path.append("<YOURPATH>/achrolabutils/achrolab")

Second, import visual from psychopy.

>>> from psychopy import visual

Then, you want to import your calibrated and saved colors.

>>> from colortable import ColorTable

Next, we need a tubes object, so we can make adjustments to the tubes.

>>> from tubes import Tubes
>>> tub = Tubes()

Then, we actually load the color table with our stored configurations.

>>> color_table = ColorTable("./calibdata/color_table_20110204_1108.pkl")

We select a certain illumination for our experiment. These illuminations
are usually high since we always want the illumination of the booth to be a
lot higher than the stimuli we present. We want to present stimuli in an
illuminated room so they appear to be surface colors. If we wanted them to
appear self-luminant we would present them in a completely dark room.

We can load a certain color entry from our color table and then define the
background of our monitor and set the tubes accordingly. The background
variable can be given to `psychopy.visual.GratingStim
<http://www.psychopy.org/api/visual/gratingstim.html>`_.

>>> color_entry = color_table.color_list[165]
>>> bg = color_entry.grating_stim_value
>>> tubes.setVoltages(color_entry.voltages)

Then we choose the colors for our stimuli, for example 10 stimuli.

>>> col_exp = [x.grating_stim_value for x in color_table.color_list[99:109]]
