#!/usr/bin/env python
"""Module collecting different functions to create visual stimuli."""

import numpy as np

from utils import degrees_to_pixels

def cornsweet(size, ppd, contrast, ramp_width=3, exponent=2.75,
                      mean_lum=.5):
    """
    Create a matrix containing a rectangular Cornsweet edge stimulus.
    The 2D luminance profile of the stimulus is defined as
    L = L_mean +/- (1 - X / w) ** a * L_mean * C/2 for the ramp and
    L = L_mean for the area beyond the ramp.
    X is the distance to the edge, w is the width of the ramp, a is a variable
    determining the steepness of the ramp, and C is the contrast at the edge,
    defined as C = (L_max-L_min) / L_mean.

    Parameters
    ----------
    size : tuple of 2 numbers
           the size of the matrix in degrees of visual angle
    ppd : number
          the number of pixels in one degree of visual angle
    contrast : number in [0,1]
               the contrast at the Cornsweet edge, defined as 
               (max_luminance - min_luminance) / mean_luminance
    ramp_width : number (optional)
                 the width of the luminance ramp in degrees of visual angle.
                 Default is 3.
    exponent : number (optional)
               Determines the steepness of the ramp. Default is 2.75. An
               exponent value of 0 leads to a stimulus with uniform flanks.
    mean_lum : number
               The mean luminance of the stimulus, i.e. the value outside of
               the ramp area.

    Returns
    -------
    stim : 2D ndarray
           
    References
    ----------
    The formula and default values are taken from Boyaci, H., Fang, F., Murray,
    S.O., Kersten, D. (2007). Responses to Lightness Variations in Early Human
    Visual Cortex. Current Biology 17, 989-993.
    """
    # compute size as the closest even number of pixel corresponding to the
    # size given in degrees of visual angle.
    size = np.round(np.tan(np.radians(np.array(size) / 2.)) / 
                 np.tan(np.radians(.5)) * ppd / 2) * 2
    stim = np.ones(size) * mean_lum
    dist = np.arange(size[1] / 2 )
    dist = np.degrees(np.arctan(dist / 2. / ppd * 2 * np.tan(np.radians(.5))))\
            * 2
    dist /= ramp_width
    dist[dist > 1] = 1
    profile = (1 - dist)  ** exponent * mean_lum *  contrast / 2
    stim[:, 0:size[1]/2] += profile[::-1]
    stim[:, size[1]/2:] -= profile
    return stim

def todorovic(coc, vert_rep, horz_rep):
    """
    Create a checkerboard illusion by appropriately aligning COC stimuli, in
    the way demonstrated by Todorovic (1987).

    Parameters
    ----------
    coc : ndarray
          The base Craig-O'Brien-Cornsweet stimulus, created with cornsweet().
          It should have a small ramp-width compared to its size, moderate
          contrast, and be square.
    horz_rep : int
               number of horizontal repetitions of the cornsweet stimulus.
    vert_rep : int
               number of vertical repetitions.

    Returns
    -------
    stim: 2D ndarray

    References
    ----------
    Todorovic, D. (1987). The Craik-O'Brien-Cornsweet effect: new
    varieties and their theoretical implications. Perception & psychophysics,
    42(6), 545-60, Plate 4.
    """

    stim = np.tile(np.hstack((coc, np.fliplr(coc))), (1, horz_rep / 2))
    if horz_rep % 2 != 0:
        stim = np.hstack((stim, stim[:, 0:coc.shape[1]]))
    stim = np.tile(np.vstack((stim, np.roll(stim, coc.shape[1], 1))),
                    (vert_rep / 2, 1))
    if vert_rep % 2 != 0:
        stim = np.vstack((stim, stim[0:coc.shape[0], :]))
    return stim

def square_wave(shape, ppd, contrast, frequency, mean_lum=.5, period='ignore',
        start='high'):
    """
    Create a horizontal square wave of given spatial frequency.

    Parameters
    ----------
    shape : tuple of 2 numbers
            The shape of the stimulus in degrees of visual angle. (y,x)
    ppd : number
          the number of pixels in one degree of visual angle
    contrast : number in [0,1]
               the contrast of the grating, defined as 
               (max_luminance - min_luminance) / mean_luminance
    frequency : number
                the spatial frequency of the wave in cycles per degree 
    mean_lum : number
               the mean luminance of the grating, i.e. (max_lum + min_lum) / 2.
               The average luminance of the actual stimulus can differ slightly
               from this value if the stimulus is not an integer of cycles big.
    period : string in ['ignore', 'full', 'half'] (optional)
             specifies if the period of the wave is taken into account when
             determining exact stimulus dimensions.
             'ignore' simply converts degrees to pixesl
             'full' rounds down to garuantee a full period
             'half' adds a half period to the size 'full' would yield.
             Default is 'ignore'.
    start : string in ['high', 'low'] (optional)
            specifies if the wave starts with a high or low value. Default is
            'high'.

    Returns
    -------
    stim : 2D ndarray
           the square wave stimulus
    """
    
    if not period in ['ignore', 'full', 'half']:
        raise TypeError('size not understood: %s' % period)
    if not start in ['high', 'low']:
        raise TypeError('start value not understood: %s' % start)
    if frequency > ppd / 2:
        raise ValueError('The frequency is limited to 1/2 cycle per pixel.')

    shape = degrees_to_pixels(np.array(shape), ppd).astype(int)
    pixels_per_cycle = int(degrees_to_pixels(1. / frequency / 2, ppd) + .5) * 2

    if period is 'full':
        shape[1] = shape[1] / pixels_per_cycle * pixels_per_cycle
    elif period is 'half':
        shape[1] = shape[1] / pixels_per_cycle * pixels_per_cycle + \
                                pixels_per_cycle / 2
    diff = type(mean_lum)(contrast * mean_lum)
    high = mean_lum + diff
    low = mean_lum - diff
    stim = np.ones(shape) * (low if start is 'high' else high)
    index = [i + j for i in range(pixels_per_cycle / 2) 
                      for j in range(0, shape[1], pixels_per_cycle)
                      if i + j < shape[1]]
    stim[:, index] = low if start is 'low' else high
    return stim

def whites_illusion_bmcc(shape, ppd, contrast, frequency, mean_lum=.5,
        start='high'):
    """
    Create a version of White's illusion on a square wave, in the style used by
    Blakeslee and McCourt (1999).

    Parameters
    ----------
    shape : tuple of 2 numbers
            The shape of the stimulus in degrees of visual angle. (y,x)
    ppd : number
          the number of pixels in one degree of visual angle
    contrast : number in [0,1]
               the contrast of the grating, defined as 
               (max_luminance - min_luminance) / mean_luminance
    frequency : number
                the spatial frequency of the wave in cycles per degree 
    mean_lum : number
               the mean luminance of the grating, i.e. (max_lum + min_lum) / 2.
               The average luminance of the actual stimulus can differ slightly
               from this value if the stimulus is not an integer of cycles big.
    start : string in ['high', 'low'] (optional)
            specifies if the wave starts with a high or low value. Default is
            'high'.

    Returns
    -------
    stim : 2D ndarray
           the stimulus

    References
    ----------
    Blakeslee B, McCourt ME (1999). A multiscale spatial filtering account of
    the White effect, simultaneous brightness contrast and grating induction.
    Vision research 39(26):4361-77.
    """
    stim = square_wave(shape, ppd, contrast, frequency, mean_lum, 'full',
                        start)
    half_cycle = int(degrees_to_pixels(1. / frequency / 2, ppd) + .5)
    stim[stim.shape[0] / 3: stim.shape[0] / 3 * 2,
         stim.shape[1] / 2 - 2 * half_cycle: 
            stim.shape[1] / 2 - half_cycle] = mean_lum
    stim[stim.shape[0] / 3: stim.shape[0] / 3 * 2,
         stim.shape[1] / 2 + half_cycle: 
            stim.shape[1] / 2 + 2 * half_cycle] = mean_lum
    return stim

def whites_illusion_gil(shape, ppd, contrast, frequency, mean_lum=.5,
        start='low'):
    """
    Create a version of White's illusion on a square wave, in the style used by
    Gilchrist (2006, p. 281)

    Parameters
    ----------
    shape : tuple of 2 numbers
            The shape of the stimulus in degrees of visual angle. (y,x)
    ppd : number
          the number of pixels in one degree of visual angle
    contrast : number in [0,1]
               the contrast of the grating, defined as 
               (max_luminance - min_luminance) / mean_luminance
    frequency : number
                the spatial frequency of the wave in cycles per degree 
    mean_lum : number
               the mean luminance of the grating, i.e. (max_lum + min_lum) / 2.
               The average luminance of the actual stimulus can differ slightly
               from this value if the stimulus is not an integer of cycles big.
    start : string in ['high', 'low'] (optional)
            specifies if the wave starts with a high or low value. Default is
            'high'.

    Returns
    -------
    stim : 2D ndarray
           the stimulus

    References
    ----------
    Gilchrist A (2006). Seeing Black and White. New York, New York, USA: Oxford
    University Press.
    """
    stim = square_wave(shape, ppd, contrast, frequency, mean_lum, 'half',
                        start)
    half_cycle = int(degrees_to_pixels(1. / frequency / 2, ppd) + .5)
    on_dark_idx = [i for i in range(int(half_cycle * 2.5), 
                                        int(stim.shape[1] - half_cycle * .5)) 
                        if stim[0, i] < mean_lum]
    on_light_idx = [i for i in range(int(half_cycle * 1.5), 
                                        int(stim.shape[1] - half_cycle * 1.5)) 
                        if stim[0, i] > mean_lum]
    stim[stim.shape[0] / 5: stim.shape[0] / 5 * 2, on_light_idx] = mean_lum
    stim[stim.shape[0] / 5 * 3: stim.shape[0] / 5 * 4, on_dark_idx] = mean_lum

    # randomize border cutoff
    max_cut = stim.shape[0] / 10
    bg = stim[0, half_cycle]
    for start_idx in range(0 if start is 'low' else half_cycle,
                            stim.shape[1] - half_cycle, 2 * half_cycle):
        
        stim[0 : np.random.randint(max_cut), 
                start_idx : start_idx + half_cycle] = bg
        stim[stim.shape[0] - np.random.randint(max_cut):, 
                start_idx : start_idx + half_cycle] = bg
    return stim
