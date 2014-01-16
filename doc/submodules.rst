.. _achrolab_submodules:

Classes of Submodules
=====================

Submodule eyeone
~~~~~~~~~~~~~~~~

The submodule `eyeone <https://github.com/derNarr/eyeone>`_ is a standalone
python package. It controls our photometer `i1 Basic Pro
<http://www.xrite.com/product_overview.aspx?ID=1461>`_  that we use to do
all the luminance measurements in our :ref:`color laboratory
<colorlab_colorlab>`. Some notes on its performance can be found :ref:`here
<colorlab_photometer>`.

`EyeOne`
--------

.. automodule:: achrolab.eyeone.eyeone
    :members:
    :inherited-members:

Submodule wasco
~~~~~~~~~~~~~~~

We use the submodule `wasco <https://github.com/derNarr/wasco>`_ to control
the multifunction card IODA-PCI12K4EXTENDED PCI that drives our dimmable
tubes. We use four sets of tubes each with three Osram T8 fluorescent tubes
red (58W / color 60), green (58W / color 66), and blue (58W / color 67). 

`Wasco`
-------

.. automodule:: achrolab.wasco.wasco
    :members:
    :inherited-members:


