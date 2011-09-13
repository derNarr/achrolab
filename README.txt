This file contains some random information you should be aware of when
using the Python module achrolab.

Run "git submodule update" to fetch submodules.

achrolab and colormath:
This module uses a patched colormath module, which is not included in the
packages. The dependencies of this module will be removed in one of the
following commits. If you want to use this package before this dependency
is removed, send me a short email. --KS

achrolab and R:
We use R to analyze our data. This includes calibration data. Therefore,
all measurements are saved as .Rdata files. If you want to use the module,
R has to be installed on your machine.
We use the module rpy2 (see http://rpy.sourceforge.net/rpy2.html) to import
our measurements directly into R.
All plots are produced in R.
See achrolab/devtubes.py and the Tubes.calibrate function therein for
an example.

Used conventions:
Variables:
	* Always small letters
	* _ (Underline) as separator between words
	* e.g. example_variable
Functions: 
	* Start with small letter
	* New word starts with capital letter (no other separator)
	* e.g. exampleFunction
Classes:
	* Start with capital letter
	* New word starts with capital letter (no other separator)
	* e.g. ExampleClass
See also github.com/noum/documentation-achrolab/python_conventions.txt

