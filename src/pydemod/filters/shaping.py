# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod
#
# Contains code from CommPy, used under the terms of the GPL 
# https://github.com/veeresht/CommPy/blob/master/commpy/filters.py
# (c) 2012 Veeresh Taranalli

import numpy

# The following function is from:
# https://github.com/veeresht/CommPy/blob/master/commpy/filters.py
# See also: https://en.wikipedia.org/wiki/Root-raised-cosine_filter
def rrcosfilter(N, alpha, Ts, Fs):
    """
    Generates a root raised cosine (RRC) filter (FIR) impulse response.
    
    Parameters
    ----------
    N : int 
        Length of the filter in samples.
    
    alpha: float
        Roll off factor (Valid values are [0, 1]).
    
    Ts : float
        Symbol period in seconds.
    
    Fs : float 
        Sampling Rate in Hz.
    
    Returns
    ---------

    h_rrc : 1-D ndarray of floats
        Impulse response of the root raised cosine filter.
    
    time_idx : 1-D ndarray of floats 
        Array containing the time indices, in seconds, for 
        the impulse response.
    """

    T_delta = 1/float(Fs)
    time_idx = ((numpy.arange(N)-N/2))*T_delta
    sample_num = numpy.arange(N)
    h_rrc = numpy.zeros(N, dtype=float)
        
    for x in sample_num:
        t = (x-N/2)*T_delta
        if t == 0.0:
            h_rrc[x] = 1.0 - alpha + (4*alpha/numpy.pi)
        elif alpha != 0 and t == Ts/(4*alpha):
            h_rrc[x] = (alpha/numpy.sqrt(2))*(((1+2/numpy.pi)* \
                    (numpy.sin(numpy.pi/(4*alpha)))) + ((1-2/numpy.pi)*(numpy.cos(numpy.pi/(4*alpha)))))
        elif alpha != 0 and t == -Ts/(4*alpha):
            h_rrc[x] = (alpha/numpy.sqrt(2))*(((1+2/numpy.pi)* \
                    (numpy.sin(numpy.pi/(4*alpha)))) + ((1-2/numpy.pi)*(numpy.cos(numpy.pi/(4*alpha)))))
        else:
            h_rrc[x] = (numpy.sin(numpy.pi*t*(1-alpha)/Ts) +  \
                    4*alpha*(t/Ts)*numpy.cos(numpy.pi*t*(1+alpha)/Ts))/ \
                    (numpy.pi*t*(1-(4*alpha*t/Ts)*(4*alpha*t/Ts))/Ts)
        
    return time_idx, h_rrc
