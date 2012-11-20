.. _achrolab_install:

How to install *achrolab* on your computer
==========================================

The easiest way to get all the code is to clone it directly from
https://github.com.

.. highlight:: bash

Just type::

    git clone git@github.com:derNarr/achrolabutils.git
    
    cd achrolabutils
    git submodule update --recursive --init

into your terminal or git bash. (Find a short introduction on how to setup
git and github :ref:`here <colorlab_tipsandtricks>`.)

.. highlight:: python

You can then add the folder to your path or include the following lines
into your python code whenever you want to use *achrolab*::
    
    import sys
    sys.path.append("<YOURPATH>/achrolabutils/")

Then import like you always do::

    from achrolab import *

