from achrolab.printing import CalibDataFile
try:
    from achrolab.eyeone import eyeone, EyeOneConstants
except:
    from achrolab.eyeone import EyeOne, EyeOneConstants
from ctypes import c_float
from contextlib import closing
from psychopy import visual
from psychopy import event
import eizoGS320
import math
import time
import mondrian
import Image
import numpy as np
from stimuli import *


class BaseMonitorTesting():
    """
    BaseMonitorTesting provides the basic methods for monitor testing - i.e. collecting data from the EyeOne, and presenting stimuli from images.
    All the other stimuli classes inherit from this.

   **Arguments for initialisation**:

   ========== ========== =========== =======================================================================================================
    Name        Kind       Default    Description
   ========== ========== =========== =======================================================================================================
   usingeizo    Boolean     False      Set to True if using or producing stimuli for the black and white monitor.
   measuring    Boolean     False      Set to True if you wish to measure data.
   calibrate    Boolean     True       If True then will ask to calibrate the EyeOne.
   prefix       String      "data"     This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime     Float       0.01       This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   ========== ========== =========== =======================================================================================================

   The assumed monitor sizes are 1024x1536 for the black and white monitor (due to the halving of the size with the graphics card) and 1024x768 if not using this monitor (i.e. for testing).

   """

    def __init__(self, usingeizo=False, measuring=False, calibrate=True, prefix="data", waittime=0.01):

        self.measuring=measuring
        self.usingeizo=usingeizo
        self.calibrate=calibrate
        self.prefix=prefix
        self.waittime=waittime

        if usingeizo==False:
            self.monitorsize=[1024,768]
            self.monitornum=0
            self.EyeOne = EyeOne.EyeOne(dummy=True) # EyeOne Object dummy

        else:
            self.monitorsize=[1024, 1536] #size of Eizo screen (half actualy monitor width)
            self.monitornum=1
            self.EyeOne = eyeone.EyeOne(dummy=False) # Actual EyeOne Object


        if measuring==True:
            if(self.EyeOne.I1_SetOption(EyeOneConstants.I1_MEASUREMENT_MODE,
            EyeOneConstants.I1_SINGLE_EMISSION) == EyeOneConstants.eNoError):
                print("Measurement mode set to single emission.")
            else:
                print("Failed to set measurement mode.")
            if(self.EyeOne.I1_SetOption(EyeOneConstants.COLOR_SPACE_KEY,
                EyeOneConstants.COLOR_SPACE_CIExyY) == EyeOneConstants.eNoError):
                print("Color space set to CIExyY.")
            else:
                print("Failed to set color space.")

            # Initialization of spectrum and colorspace
            self.colorspace = (c_float * EyeOneConstants.TRISTIMULUS_SIZE)()
            self.spectrum = (c_float * EyeOneConstants.SPECTRUM_SIZE)()

            self.checkCalibrate()


    def checkCalibrate(self):
        """
         This method is called to calibrate the EyeOne. Takes no arguments.
        """
        if (self.calibrate or (self.EyeOne.I1_TriggerMeasurement() ==  EyeOneConstants.eDeviceNotCalibrated)):
        # Calibration of EyeOne
            print("\nPlease put EyeOne Pro on calibration plate and press \n key to start calibration.")
            while(self.EyeOne.I1_KeyPressed() != EyeOneConstants.eNoError):
                time.sleep(0.1)
            if (self.EyeOne.I1_Calibrate() == EyeOneConstants.eNoError):
                print("Calibration done.")
            else:
                print("Calibration failed.")

    def showStimuliFromPNG(self, inputfilename, bgcolor=0):
        """
    This method displays the provided PNG image in a window, which has a black background by default.

    This function rewrites self.drawFunction to work with the generic runningLoop.

    **Arguments**:

   ============== ========== =========== =======================================================================================================
    Name            Kind       Default    Description
   ============== ========== =========== =======================================================================================================
   inputfilename    String      N/A        The path to the PNG file which is to be displayed.
   bgcolor          Integer     0          The background color of the window, defaultly 0 (black). Must be between 0 and 1023.
   ============== ========== =========== =======================================================================================================

        """
        self.window = visual.Window(self.monitorsize, monitor="mymon", color=eizoGS320.encode_color(bgcolor,bgcolor), screen=self.monitornum, colorSpace="rgb255", allowGUI=False, units="pix")
        self.imagestim=visual.SimpleImageStim(self.window, image=inputfilename, units='norm', pos=(0.0, 0.0), contrast=1.0, opacity=1.0, flipHoriz=False, flipVert=False, name='imagestim', autoLog=True)
        #Return function which handles drawing of stimuli, so we can write a general loop for all stimuli drawing/measurement
        #self.grayvals=None # specify in subclasses
        def drawFunction():
            self.imagestim.draw()
            self.window.flip()

        self.drawFunction=drawFunction

    def collectData(self, datafile):
        """
        This method collects the tristimulus data from the EyeOne photometer and writes it to the provided datafile (which should be a CalibDataFile object from the achrolab.printing class.

    **Arguments**:

   ============== =============== =========== =======================================================================================================
    Name            Kind            Default    Description
   ============== =============== =========== =======================================================================================================
   datafile        CalibDataFile      N/A      A CalibDataFile object to which the measurement data will be written.
   ============== =============== =========== =======================================================================================================

        """
        if(self.EyeOne.I1_TriggerMeasurement() != EyeOneConstants.eNoError):
            print("Measurement failed.")
            # retrieve Color Space
        if(self.EyeOne.I1_GetTriStimulus(self.colorspace, 0) != EyeOneConstants.eNoError):
            print("Failed to get color space.")
        else:
            print("Color Space " + str(self.colorspace[:]) + "\n")
            datafile.writeDataTXT(grayvals=self.grayvals, rgb=None, xyY=self.colorspace, voltage=None, spec_list=None, delimiter="\t")

    def runningLoop(self):
        """
        This method provides the runningLoop in its abstract form which is used by all the stimuli classes. The different stimuli classes simply provide different functions over self.drawFunction(). Takes no arguments, but depending on the stimuli, the correct object variables must be set.
        """
        running=True
        with closing(CalibDataFile(prefix=self.prefix)) as datafile:
            while running==True:
                self.keys=event.getKeys()
                for thiskey in self.keys:
                    if thiskey in ['q', 'escape']:
                        running=False
                        break

                self.drawFunction()
                if self.measuring==True:
                    self.collectData(datafile)
                time.sleep(self.waittime)


class CRTTest(BaseMonitorTesting):
    """
    CRTTest produces a patch of a certain luminance in the centre of the screen, and modulates the surround according to a sin function.

    TUB notes:
        Small region test at the centre of CRT, check min, middle, max, luminance.  Then,sin wave modulation of the rest of the screen while measuring centre. This is a powersupply issue. Modulate sin wave frequency to measure responsiveness. Square waves are even harsher on the CRT. Allowing naked eye testing is also good, since the frequency of modulation may be intense for crappy photometers.

    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ========== =========== =======================================================================================================
    Name              Kind       Default    Description
   ================ ========== =========== =======================================================================================================
   usingeizo          Boolean     False      Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean     False      Set to True if you wish to measure data.
   calibrate          Boolean     True       If True then will ask to calibrate the EyeOne.
   prefix             String      "data"     This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float       0.01       This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.

   patchsize          Float       0.5        This is the size of the patch in the centre in normalised units.
   centralstimgray    Integer     400        This is the fixed gray value of the central patch.
   sinamplitude       Integer     1023       This is the amplitude of the sin wave, so effectively the maximum gray value of the background.
   freq               Float       0.01       This sets the size of the steps of sampling of the sin function.
   sinoffset          Integer     0          This is an offset which is added to the sin wave, default 0.
   ================ ========== =========== =======================================================================================================

    Note that unlike most other stimuli, this does not rely on or produce any PNG files.
   """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, patchsize=0.5, centralstimgray=400, sinamplitude=1023, freq=0.01, sinoffset=0):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.patchsize=patchsize
        self.centralstimgray=centralstimgray
        self.sinamplitude=sinamplitude
        self.freq=freq
        self.sinoffset=sinoffset
        self.graystim=0
        self.n=0

    def initdraw(self):
        """
        This method creates the window and stimuli, ready for drawing. Takes no arguments. Is called prior to starting the runningLoop.

        Of particular importance is the setting of the self.grayvals list, which is a two item list containing the relevant gray color variables to be saved in measurements.
        """
        self.window = visual.Window(self.monitorsize, monitor="mymon", color=eizoGS320.encode_color(0,0), winType="pygame", screen=self.monitornum, colorSpace="rgb255", allowGUI=False, units="pix")

        self.bgstim=visual.PatchStim(self.window, tex=None, units='norm', pos=(0, 0), size=2, colorSpace=self.window.colorSpace, color=eizoGS320.encode_color(0, 0))

        self.centralstim=visual.PatchStim(self.window, tex=None, units='norm', pos=(0, 0), size=self.patchsize, colorSpace=self.window.colorSpace, color=eizoGS320.encode_color(self.centralstimgray, self.centralstimgray))
        self.n=0
        self.grayvals=[self.graystim, self.centralstimgray]

    def drawFunction(self):
        """
        This is the drawFunction method as specified by CRTTest. It takes no arguments but depends upon the properties being set correctly from the arguments passed in initialisation of the CRTTest object.
        """
        #sinamplitude, freq, sinoffset
        self.graystim=(self.sinamplitude*abs(math.sin(2*math.pi*self.freq*self.n)))+self.sinoffset
        color=eizoGS320.encode_color(self.graystim, self.graystim)
        #color = [x/128.-1 for x in color]
        #mywin.setColor(color, 'rgb255')
        self.bgstim.setColor(color)
        self.n+=1
        self.n = self.n % (1./self.freq)
        self.bgstim.draw()
        self.centralstim.draw()
        self.window.flip()

    def run(self):
        self.initdraw()
        self.runningLoop()

class Mondrian(BaseMonitorTesting):
    '''
    This class is a wrapper for the Mondrian generation code from TU Berlin. It produces a Mondrian to a  PNG if no PNG file is provided in the pngfile argument, otherwise it will display the Mondrian with run().

    TU Berlin notes:
        Create a mondrian on which the difference between desired color distribution and actual color distribution is smaller than some accuracy value. If no randomly created mondrian fulfills this criterion before some cycle count is reached, the best mondrian generated so far is returned.

    .. warning::
        Note one must manually set the image size to (2048, 1536) if producing stimuli for the black and white monitor.

    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ========================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ========================================================================================================================
   usingeizo          Boolean          False      Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean          False      Set to True if you wish to measure data.
   calibrate          Boolean          True       If True then will ask to calibrate the EyeOne.
   prefix             String           "data"     This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float            0.01       This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.

   highgray           Integer         1023        This is the maximum gray value in the Mondrian (should be between 0 and 1023).
   lowgray            Integer         0           This is the minimum gray value in the Mondrian (should be between 0 and 1023).
   step               Integer         1           This is the step between the maximum and minimum gray values which creates the range for the color list.
   meanlength         Float           5           The mean length of the edges of the Mondrian rectangles.
   weights            List(Floats)    None        List of floats which define the probabilities of the colors in the Mondrian. Default None gives equal probabilities.
   accuracy           Float           0.05        The maximally allowed deviation between the relative frequency of a color and its specified weight.
   max_cycles         Integer         1000        The maximal number of mondrians created before the function aborts and returns the best mondrian so far.
   write              Boolean         False       Whether the Mondrian array should be saved, usually is False.
   seed               Hashable Object 1           This allows the seed to be set, so multiple Mondrians can be generated with the same background.
   pngfile            String          None        The path to the pre-made PNG file if one wishes to display a pre-made Mondrian.
   imagesize          List(2*Integer) None        The size of the Mondrian to be generated, as a 2 element list [X,Y]. If None uses defined monitor size.
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   saveimage          Boolean         True        Whether to save an image of the generated Mondrian. Set to false if generating to inset in another image.
   ================ ================= =========== ========================================================================================================================

    '''

    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, highgray=1023, lowgray=0, step=1, meanlength=5, weights=None, accuracy=0.05, max_cycles=1000, write=False, seed=1, pngfile=None, imagesize=None, encode=True, saveimage=True):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[highgray, lowgray]
        if imagesize==None:
            mondriansize=self.monitorsize
        else:
            #mondriansize=imagesize
            mondriansize = []
            mondriansize.extend(imagesize)
        mondriansize.reverse()
        #Create mondrian if no PNG file provided
        if (pngfile==None) or (pngfile==""):
            colorlist=range(lowgray, highgray, step)
            nparray=mondrian.create_mondrian(mondriansize, meanlength, colorlist, weights, accuracy, max_cycles, write, seed)
            self.mondrianarray=nparray
            if saveimage==True:
                if encode==True:
                    nparray=eizoGS320.encode_np_array(nparray)
                else:
                    (N, M) = np.shape(nparray)
                    newarray = np.zeros((N, M, 3), dtype=np.uint8)
                    newarray[:,:,0]=np.uint8(nparray[:,:]/4)
                    newarray[:,:,1]=np.uint8(nparray[:,:]/4)
                    newarray[:,:,2]=np.uint8(nparray[:,:]/4)
                    #nparray.dtype = np.uint8
                    nparray=newarray
                    pil_im = Image.fromarray(nparray)
                    self.pngfile="mondrian"+time.strftime("%Y%m%d_%H%M")+".png"
                    pil_im.save(self.pngfile)

        else:
            self.pngfile=pngfile

    def run(self):
        self.showStimuliFromPNG(self.pngfile)
        self.runningLoop()

class Cornsweet(BaseMonitorTesting):
    """
    This class is a wrapper for the Cornsweet generation code from TU Berlin. It produces a form of the Cornsweet illusion to PNG if no PNG file is provided in the pngfile argument, otherwise it will display the stimuli provided. Still need to fix the unencoded version.

    TU Berlin notes:
        Create a matrix containing a rectangular Cornsweet edge stimulus.
        The 2D luminance profile of the stimulus is defined as L = L_mean +/- (1 - X / w) ** a * L_mean * C/2 for the ramp and L = L_mean for the area beyond the ramp.
        X is the distance to the edge, w is the width of the ramp, a is a variable determining the steepness of the ramp, and C is the contrast at the edge, defined as C = (L_max-L_min) / L_mean.



    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ========================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ========================================================================================================================
   usingeizo          Boolean          False      Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean          False      Set to True if you wish to measure data.
   calibrate          Boolean          True       If True then will ask to calibrate the EyeOne.
   prefix             String           "data"     This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float            0.01       This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.

   visualdegrees      List(Floats)    None        List [X,Y] of size of stimuli in visual degrees. Default None instead calculates this from ppd and monitorsize.
   ppd                Integer         128         Number of pixels per visual degree.
   contrast           Float           1           Value between 0 and 1. The contrast of the grating, defined as (max_luminance - min_luminance) / mean_luminance.
   ramp_width         Float           3           The width of the luminance ramp in degrees of visual angle.
   exponent           Float           2.75        Determines the steepness of the ramp. An exponent value of 0 leads to a stimulus with uniform flanks.
   mean_lum           Integer         511         The mean luminance of the stimulus, i.e. the value outside of the ramp area.
   pngfile            String          None        The path to the pre-made PNG file if one wishes to display a pre-made stimuli
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   ================ ================= =========== ========================================================================================================================

    **References (from TU Berlin)**:

    The formula and default values are taken from Boyaci, H., Fang, F., Murray, S.O., Kersten, D. (2007). Responses to Lightness Variations in Early Human Visual Cortex. Current Biology 17, 989-993.

   """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, visualdegrees=None, ppd=128, contrast=1, ramp_width=3, exponent=2.75, mean_lum=511, pngfile=None, encode=True):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[mean_lum, exponent]
        if pngfile==None:
            if visualdegrees==None:
                visualdegrees=[]
                visualdegrees.append(int(self.monitorsize[1]/ppd))
                visualdegrees.append(int(self.monitorsize[0]/ppd))
            nparray=cornsweet(visualdegrees, ppd, contrast, ramp_width, exponent, mean_lum)
            if encode==True:
                nparray=eizoGS320.encode_np_array(nparray)
            else:
                (N, M) = np.shape(nparray)
                newarray = np.zeros((N, M, 3), dtype=np.uint8)
                newarray[:,:,0]=np.uint8(nparray[:,:]/4)
                newarray[:,:,1]=np.uint8(nparray[:,:]/4)
                newarray[:,:,2]=np.uint8(nparray[:,:]/4)
                #nparray.dtype = np.uint8
                nparray=newarray
            pil_im = Image.fromarray(nparray)
            self.pngfile="cornsweet"+time.strftime("%Y%m%d_%H%M")+".png"
            pil_im.save(self.pngfile)
        else:
            self.pngfile=pngfile

    def run(self):
        self.showStimuliFromPNG(self.pngfile)
        self.runningLoop()

class Todorovic(BaseMonitorTesting):
    """
    This class is a wrapper for the Todorovic checkerboard generation code from TU Berlin. It produces a form of the Torodovic checkerboard illusion to PNG if no PNG file is provided in the pngfile argument, otherwise it will display the stimuli provided. Still need to fix the unencoded version.

    Note that it works by first producing an appropriate Cornsweet stimulus and then repeating this.

    TU Berlin notes:
        Create a checkerboard illusion by appropriately aligning COC stimuli, in the way demonstrated by Todorovic (1987).



    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== =====================================================================================================================================
    Name              Kind             Default     Description
   ================ ================= =========== =====================================================================================================================================
   usingeizo          Boolean          False      Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean          False      Set to True if you wish to measure data.
   calibrate          Boolean          True       If True then will ask to calibrate the EyeOne.
   prefix             String           "data"     This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float            0.01       This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   visualdegrees      List(Floats)    None        List [X,Y] of size of stimuli in visual degrees. Default None instead calculates this from ppd and monitorsize.
   ppd                Integer         128         Number of pixels per visual degree.
   contrast           Float           1           Value between 0 and 1. The contrast of the grating, defined as (max_luminance - min_luminance) / mean_luminance.
   ramp_width         Float           3           The width of the luminance ramp in degrees of visual angle, used for generating the Cornsweet stimulus.
   exponent           Float           2.75        Determines the steepness of the ramp. An exponent value of 0 leads to a stimulus with uniform flanks. Used for Cornsweet Stimulus.
   mean_lum           Integer         511         The mean luminance of the stimulus, i.e. the value outside of the ramp area. Used for Cornsweet stimulus.
   vert_rep           Integer         3           The number of vertical repetitions (i.e. rows) in the Todorovic checkerboard.
   horz_rep           Integer         5           The number of horizontal repetitions (i.e. columns) in the Todorovic checkerboard.
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   ================ ================= =========== =====================================================================================================================================

    **References (from TU Berlin)**:
    Todorovic, D. (1987). The Craik-O'Brien-Cornsweet effect: new varieties and their theoretical implications. Perception & psychophysics, 42(6), 545-60, Plate 4.

    """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, visualdegrees=None, ppd=128, contrast=1, ramp_width=3, exponent=2.75, mean_lum=511, vert_rep=3, horz_rep=5, pngfile=None, encode=True):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[mean_lum, exponent]
        if pngfile==None:
            if visualdegrees==None:
                visualdegrees=[]
                visualdegrees.append(int((self.monitorsize[1]/ppd)/vert_rep))
                visualdegrees.append(int((self.monitorsize[0]/ppd)/horz_rep))
            nparray=cornsweet(visualdegrees, ppd, contrast, ramp_width, exponent, mean_lum)
            nparray=todorovic(nparray, vert_rep, horz_rep)
            if encode==True:
                nparray=eizoGS320.encode_np_array(nparray)
            else:
                (N, M) = np.shape(nparray)
                newarray = np.zeros((N, M, 3), dtype=np.uint8)
                newarray[:,:,0]=np.uint8(nparray[:,:]/4)
                newarray[:,:,1]=np.uint8(nparray[:,:]/4)
                newarray[:,:,2]=np.uint8(nparray[:,:]/4)
                #nparray.dtype = np.uint8
                nparray=newarray
            pil_im = Image.fromarray(nparray)
            self.pngfile="todorovic"+time.strftime("%Y%m%d_%H%M")+".png"
            pil_im.save(self.pngfile)
        else:
            self.pngfile=pngfile

    def run(self):
        self.showStimuliFromPNG(self.pngfile)
        self.runningLoop()

class WhiteIllusion(BaseMonitorTesting):
    """
    This class is a wrapper for the White's Illusion generation code from TU Berlin. It produces a form of the White's illusion on a square wave to PNG if no PNG file is provided in the pngfile argument, otherwise it will display the stimuli provided. Still need to fix the unencoded version.

    Produces both kind="bmcc": in the style used by Blakeslee and McCourt (1999), and kind="gil": in the style used by Gilchrist (2006, p. 281).



    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ========================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ========================================================================================================================
   usingeizo          Boolean         False       Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean         False       Set to True if you wish to measure data.
   calibrate          Boolean         True        If True then will ask to calibrate the EyeOne.
   prefix             String          "data"      This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float           0.01        This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   kind               String          "bmcc"      This sets the style of White's Illumination stimuli to be produced, valid values: "bmcc" or "gil".
   visualdegrees      List(Floats)    None        List [X,Y] of size of stimuli in visual degrees. Default None instead calculates this from ppd and monitorsize.
   ppd                Integer         128         Number of pixels per visual degree.
   contrast           Float           1           Value between 0 and 1. The contrast of the grating, defined as (max_luminance - min_luminance) / mean_luminance.
   frequency          Float           5           The spatial frequency of the wave in cycles per degree.
   mean_lum           Integer         511         The mean luminance of the stimulus, i.e. the value outside of the ramp area.
   start              String          "high"      Specifies if the wave starts with a high or low value, can be "high" or "low".
   pngfile            String          None        The path to the pre-made PNG file if one wishes to display a pre-made stimuli
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   ================ ================= =========== ========================================================================================================================

    **References (from TU Berlin)**:

    Blakeslee B, McCourt ME (1999). A multiscale spatial filtering account of the White effect, simultaneous brightness contrast and grating induction. Vision research 39(26):4361-77.

    Gilchrist A (2006). Seeing Black and White. New York, New York, USA: Oxford University Press.

   """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, kind="bmcc", visualdegrees=None, ppd=128, contrast=1, frequency=5, mean_lum=511, start='high', pngfile=None, encode=True):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[mean_lum, contrast]
        if pngfile==None:
            if visualdegrees==None:
                visualdegrees=[]
                visualdegrees.append(int(self.monitorsize[1]/ppd))
                visualdegrees.append(int(self.monitorsize[0]/ppd))
            if kind=="bmcc":
                nparray=whites_illusion_bmcc(visualdegrees, ppd, contrast, frequency, mean_lum=mean_lum, start=start)
            if kind=="gil":
                nparray=whites_illusion_gil(visualdegrees, ppd, contrast, frequency, mean_lum=mean_lum, start=start)

            if encode==True:
                nparray=eizoGS320.encode_np_array(nparray)
            else:
                (N, M) = np.shape(nparray)
                newarray = np.zeros((N, M, 3), dtype=np.uint8)
                newarray[:,:,0]=np.uint8(nparray[:,:]/4)
                newarray[:,:,1]=np.uint8(nparray[:,:]/4)
                newarray[:,:,2]=np.uint8(nparray[:,:]/4)
                #nparray.dtype = np.uint8
                nparray=newarray
            pil_im = Image.fromarray(nparray)
            self.pngfile="whiteillusion"+kind+time.strftime("%Y%m%d_%H%M")+".png"
            pil_im.save(self.pngfile)
        else:
            self.pngfile=pngfile
    def run(self):
        self.showStimuliFromPNG(self.pngfile)
        self.runningLoop()

class SquareWave(BaseMonitorTesting):
    """
    This class is a wrapper for the Square Wave generation code from TU Berlin. It produces a form of a square wave to PNG if no PNG file is provided in the pngfile argument, otherwise it will display the stimuli provided. Still need to fix the unencoded version.

    TU Berlin notes:
        Create a horizontal square wave of given spatial frequency.



    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ===============================================================================================================================================================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ===============================================================================================================================================================================================================================================================
   usingeizo          Boolean         False       Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean         False       Set to True if you wish to measure data.
   calibrate          Boolean         True        If True then will ask to calibrate the EyeOne.
   prefix             String          "data"      This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float           0.01        This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   visualdegrees      List(Floats)    None        List [X,Y] of size of stimuli in visual degrees. Default None instead calculates this from ppd and monitorsize.
   ppd                Integer         128         Number of pixels per visual degree.
   contrast           Float           1           Value between 0 and 1. The contrast of the grating, defined as (max_luminance - min_luminance) / mean_luminance.
   frequency          Float           5           The spatial frequency of the wave in cycles per degree.
   period             String          "ignore"    Specifies if the period of the wave is taken into account when determining exact stimulus dimensions. 'ignore' simply converts degrees to pixels, 'full' rounds down to guarantee a full period, 'half' adds a half period to the size 'full' would yield.
   mean_lum           Integer         511         The mean luminance of the stimulus, i.e. the value outside of the ramp area.
   start              String          "high"      Specifies if the wave starts with a high or low value, can be "high" or "low".
   pngfile            String          None        The path to the pre-made PNG file if one wishes to display a pre-made stimuli
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   ================ ================= =========== ===============================================================================================================================================================================================================================================================

   """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, visualdegrees=None, ppd=512, contrast=1, frequency=5, mean_lum=511, period='ignore', start='high', pngfile=None, encode=True):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[mean_lum, contrast]
        if pngfile==None:
            if visualdegrees==None:
                visualdegrees=[]
                visualdegrees.append(int(self.monitorsize[1]/ppd))
                visualdegrees.append(int(self.monitorsize[0]/ppd))
            nparray=square_wave(visualdegrees, ppd, contrast, frequency, mean_lum, period=period, start=start)
            if encode==True:
                nparray=eizoGS320.encode_np_array(nparray)
            else:
                (N, M) = np.shape(nparray)
                newarray = np.zeros((N, M, 3), dtype=np.uint8)
                newarray[:,:,0]=np.uint8(nparray[:,:]/4)
                newarray[:,:,1]=np.uint8(nparray[:,:]/4)
                newarray[:,:,2]=np.uint8(nparray[:,:]/4)
                #nparray.dtype = np.uint8
                nparray=newarray
            pil_im = Image.fromarray(nparray)
            self.pngfile="squarewave"+time.strftime("%Y%m%d_%H%M")+".png"
            pil_im.save(self.pngfile)
        else:
            self.pngfile=pngfile
    def run(self):
        self.showStimuliFromPNG(self.pngfile)
        self.runningLoop()

class Lines(BaseMonitorTesting):
    """
    This class produces horizontally and vertically oriented lines of a specified width (to test whether there is the same luminance in both directions). It is similar to the SquareWave stimuli code from TU Berlin. It produces the line stimuli to PNG files if no PNG files are provided in the pngfiles list argument, otherwise it will display the stimuli provided. Still need to fix the unencoded version.

    .. warning::
        Note one must manually set the monitor size argument to (2048, 1536) if producing stimuli for the black and white monitor.


    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ===============================================================================================================================================================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ===============================================================================================================================================================================================================================================================
   usingeizo          Boolean         False       Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean         False       Set to True if you wish to measure data.
   calibrate          Boolean         True        If True then will ask to calibrate the EyeOne.
   prefix             String          "data"      This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float           0.01        This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   pngfiles           List(Strings)   None        The paths to the pre-made PNG files if one wishes to display pre-made stimuli. If None then generates new stimuli files.
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   monitorsize        List(Integers)  None        List of monitor size values [X,Y] to produce stimuli for. If None then determines values from defaults.
   lowgray            Integer         0           The gray value of the lines.
   highgray           Integer         1023        The gray value of the space between the lines.
   linewidth          Integer         8           The width of the lines in pixels. Note this must be a divisor of your monitor size for the stimuli to display correctly.
   ================ ================= =========== ===============================================================================================================================================================================================================================================================

   """
    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, pngfiles=None, encode=True, monitorsize=None, lowgray=0, highgray=1023, linewidth=8):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.linepngs=[]
        self.grayvals=[highgray, lowgray]
        if pngfiles==None:
            if monitorsize==None:
                #monitorsize=self.monitorsize
                monitorsize = []
                monitorsize.extend(self.monitorsize)
            monitorsize.reverse()
            nparrayx=np.ones(monitorsize, dtype=np.uint16)
            nparrayx*=512
            nparrayy=np.ones(monitorsize, dtype=np.uint16)
            nparrayy*=512
            i=0
            color=lowgray
            #x-loop
            while i<monitorsize[0]:
                if i%linewidth==0:
                    if color==lowgray:
                        color=highgray
                    else:
                        color=lowgray
                nparrayx[i, :]=color
                i+=1
            i=0
            #y-loop
            while i<monitorsize[1]:
                if i%linewidth==0:
                    if color==lowgray:
                        color=highgray
                    else:
                        color=lowgray
                nparrayy[:,i]=color
                i+=1
            if encode==True:
                nparrayx=eizoGS320.encode_np_array(nparrayx)
                nparrayy=eizoGS320.encode_np_array(nparrayy)
            else:
                (N, M) = np.shape(nparrayx)
                newarrayx = np.zeros((N, M, 3), dtype=np.uint8)
                newarrayx[:,:,0]=np.uint8(nparrayx[:,:]/4)
                newarrayx[:,:,1]=np.uint8(nparrayx[:,:]/4)
                newarrayx[:,:,2]=np.uint8(nparrayx[:,:]/4)
                #nparray.dtype = np.uint8
                nparrayx=newarrayx
                (N, M) = np.shape(nparrayy)
                newarrayy = np.zeros((N, M, 3), dtype=np.uint8)
                newarrayy[:,:,0]=np.uint8(nparrayy[:,:]/4)
                newarrayy[:,:,1]=np.uint8(nparrayy[:,:]/4)
                newarrayy[:,:,2]=np.uint8(nparrayy[:,:]/4)
                #nparray.dtype = np.uint8
                nparrayy=newarrayy

            pil_imx = Image.fromarray(nparrayx)
            pil_imy = Image.fromarray(nparrayy)
            timem=str(time.strftime("%Y%m%d_%H%M"))
            self.linepngs.append(str(linewidth)+"linesx"+timem+".png")
            self.linepngs.append(str(linewidth)+"linesy"+timem+".png")
            pil_imx.save(self.linepngs[0])
            pil_imy.save(self.linepngs[1])

        else:
            self.linepngs=pngfiles

    def drawFunction(self):
            if self.n%2 == 0:
                self.linesx.draw()
                print("Horizontal lines drawn")
            else:
                self.linesy.draw()
                print("Vertical lines drawn")
            self.n+=1
            self.n = self.n % 2
            self.window.flip()

    def run(self):
        self.window = visual.Window(self.monitorsize, monitor="mymon", color=eizoGS320.encode_color(0,0), screen=self.monitornum, colorSpace="rgb255", allowGUI=False, units="pix")
        self.linesx=visual.SimpleImageStim(self.window, image=self.linepngs[0], units='norm', pos=(0.0, 0.0), contrast=1.0, opacity=1.0, flipHoriz=False, flipVert=False, name='linesx', autoLog=True)
        self.linesy=visual.SimpleImageStim(self.window, image=self.linepngs[1], units='norm', pos=(0.0, 0.0), contrast=1.0, opacity=1.0, flipHoriz=False, flipVert=False, name='linesy', autoLog=True)
        self.n=0
        if self.measuring==True:
            print("\nPlease put EyeOne Pro in measurement position and press \n key to start measurement.")
            while(self.EyeOne.I1_KeyPressed() != EyeOneConstants.eNoError):
                time.sleep(0.1)
            print("Starting measurement...")
        self.runningLoop()

class SinGrating(BaseMonitorTesting):
    """
    Produces a sin-wave based stimuli across the screen, which is then shifted to anti-phase and re-presented rapidly.

    TUB notes:
    Two stimuli, superimposed mean luminance is equal to background. At high enough frequencies, the stimuli should be invisible. The photometer will probably be fine with this, but if one's eyes are moving too much, it will look terrible. Look through a tube and the effect will probably go away. Anyway, the point is, is that this is a great test for frame dropping.

    .. warning::
        Note one must manually set the monitor size argument to (2048, 1536) if producing stimuli for the black and white monitor.


    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ===============================================================================================================================================================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ===============================================================================================================================================================================================================================================================
   usingeizo          Boolean         False       Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean         False       Set to True if you wish to measure data.
   calibrate          Boolean         True        If True then will ask to calibrate the EyeOne.
   prefix             String          "data"      This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float           0.01        This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   pngfiles           List(Strings)   None        The paths to the pre-made PNG files if one wishes to display pre-made stimuli. If None then generates new stimuli files.
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   monitorsize        List(Integers)  None        List of monitor size values [X,Y] to produce stimuli for. If None then determines values from defaults.
   gratingheight      Integer         20          Height of the grating from the centre, in pixels.
   sinamplitude       Integer         512         The middle gray value of the sin grating.
   sinoffset          Integer         512         The offset for the sin grating, with default values this is set to 512 such that the maximal value is 1024.
   ================ ================= =========== ===============================================================================================================================================================================================================================================================

    Note this stimuli does not yet appear to work as intended, in that the sin wave never appears invisible even at very high refresh rates.
     """

    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, pngfiles=None, encode=True, monitorsize=None, gratingheight=20, sinamplitude=512, sinoffset=512):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[sinamplitude, sinoffset]
        self.sinpngs=[]
        if pngfiles==None:
            if monitorsize==None:
                #monitorsize=self.monitorsize
                monitorsize = []
                monitorsize.extend(self.monitorsize)
            monitorsize.reverse()
            nparray0=np.ones(monitorsize, dtype=np.uint16)
            nparray0*=512
            nparray180=np.ones(monitorsize, dtype=np.uint16)
            nparray180*=512
            i=0
            #x-loop
            while i<monitorsize[1]:
                nparray0[int(monitorsize[0]/2)-gratingheight:int(monitorsize[0]/2)+gratingheight, i]=(sinamplitude*math.sin((((2.0*math.pi)/(monitorsize[1]))*i) +0.00001)) + sinoffset
                nparray180[int(monitorsize[0]/2)-gratingheight:int(monitorsize[0]/2)+gratingheight, i]=(sinamplitude*math.sin((((2.0*math.pi)/(monitorsize[1]))*i) +0.00001 + math.pi)) + sinoffset
                i+=1


            if encode==True:
                nparray0=eizoGS320.encode_np_array(nparray0)
                nparray180=eizoGS320.encode_np_array(nparray180)

            else:
                (N, M) = np.shape(nparray0)
                newarray0 = np.zeros((N, M, 3), dtype=np.uint8)
                newarray0[:,:,0]=np.uint8(nparray0[:,:]/4)
                newarray0[:,:,1]=np.uint8(nparray0[:,:]/4)
                newarray0[:,:,2]=np.uint8(nparray0[:,:]/4)
                #nparray.dtype = np.uint8
                nparray0=newarray0
                (N, M) = np.shape(nparray180)
                newarray180 = np.zeros((N, M, 3), dtype=np.uint8)
                newarray180[:,:,0]=np.uint8(nparray180[:,:]/4)
                newarray180[:,:,1]=np.uint8(nparray180[:,:]/4)
                newarray180[:,:,2]=np.uint8(nparray180[:,:]/4)
                #nparray.dtype = np.uint8
                nparray180=newarray180


            pil_im0 = Image.fromarray(nparray0)
            pil_im180 = Image.fromarray(nparray180)
            timem=str(time.strftime("%Y%m%d_%H%M"))
            self.sinpngs.append("singrating0p"+timem+".png")
            self.sinpngs.append("singrating180p"+timem+".png")
            pil_im0.save(self.sinpngs[0])
            pil_im180.save(self.sinpngs[1])

        else:
            self.sinpngs=pngfiles

    def drawFunction(self):
        if self.n%2 == 0:
            self.sin0.draw()
            print("0 phase sin grating drawn")
        else:
            self.sin180.draw()
            print("180 phase sin grating drawn")
        self.n+=1
        self.n = self.n % 2
        self.window.flip()

    def run(self):
        self.window = visual.Window(self.monitorsize, monitor="mymon", color=eizoGS320.encode_color(0,0), screen=self.monitornum, colorSpace="rgb255", allowGUI=False, units="pix")
        self.sin0=visual.SimpleImageStim(self.window, image=self.sinpngs[0], units='norm', pos=(0.0, 0.0), contrast=1.0, opacity=1.0, flipHoriz=False, flipVert=False, name='phase0', autoLog=True)
        self.sin180=visual.SimpleImageStim(self.window, image=self.sinpngs[1], units='norm', pos=(0.0, 0.0), contrast=1.0, opacity=1.0, flipHoriz=False, flipVert=False, name='phase180', autoLog=True)
        self.n=0
        self.runningLoop()

class PatchBrightnessTest(BaseMonitorTesting):
    '''
    Compare luminance of big patch and small patch, on CRT big patch should always be less bright. Can use up and down arrow keys to modify the size of the patch whilst running.

    This class inherits from BaseMonitorTesting.

   **Arguments for initialisation**:

   ================ ================= =========== ===============================================================================================================================================================================================================================================================
    Name              Kind             Default    Description
   ================ ================= =========== ===============================================================================================================================================================================================================================================================
   usingeizo          Boolean         False       Set to True if using or producing stimuli for the black and white monitor.
   measuring          Boolean         False       Set to True if you wish to measure data.
   calibrate          Boolean         True        If True then will ask to calibrate the EyeOne.
   prefix             String          "data"      This is the prefix for the filename that the data will be written to. Writes like prefix+date_time.
   waittime           Float           0.01        This is the waiting time between iterations of the runningLoop. So effectively sets the framerate.
   encode             Boolean         True        Sets whether to encode the black and white monitor or not.
   monitorsize        List(Integers)  None        List of monitor size values [X,Y] to present the stimuli on. If None then determines values from defaults.
   patchsize          Float           0.5         The initial size of the central patch in normalised units.
   bggray             Integer         512         The fixed value of the background gray.
   patchgray          Integer         800         The fixed value of the patch gray.
   patchstep          Float           0.1         The amount by which one button press Up or Down changes the central patch size.
   ================ ================= =========== ===============================================================================================================================================================================================================================================================


     '''

    def __init__(self, usingeizo=False, measuring=False, calibrate=True,prefix="data", waittime=0.1, encode=True, monitorsize=None, patchsize=0.5, bggray=511, patchgray=800, patchstep=0.1):
        BaseMonitorTesting.__init__(self, usingeizo=usingeizo, measuring=measuring, calibrate=calibrate, prefix=prefix, waittime=waittime)
        self.grayvals=[patchgray, bggray]
        self.patchsize=patchsize
        self.bggray=bggray
        self.patchgray=patchgray
        self.patchstep=patchstep
    def drawFunction(self):
        for thiskey in self.keys:
            if thiskey in ['up']:
                self.patchsize+=self.patchstep
                self.patch.setSize(self.patchsize, units='norm')
            if thiskey in ['down']:
               self.patchsize-=self.patchstep
               self.patch.setSize(self.patchsize, units='norm')
        self.patch.draw()
        self.window.flip()

    def run(self):
        self.window = visual.Window(self.monitorsize, monitor="mymon", color=eizoGS320.encode_color(0,0), screen=self.monitornum, colorSpace="rgb255", allowGUI=False, units="pix")
        self.patch=visual.PatchStim(self.window, tex=None, units='norm', pos=(0, 0), size=self.patchsize, colorSpace=self.window.colorSpace, color=eizoGS320.encode_color(self.patchgray, self.patchgray))
        self.runningLoop()

