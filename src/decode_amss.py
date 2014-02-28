#!/usr/bin/python

import scipy.io.wavfile as wavfile
import numpy
#from scipy import signal
#import matplotlib.pyplot as mplot

import pydemod.modulation.phase as phasemod
import pydemod.coding.manchester as manchester
import pydemod.coding.polynomial as poly
import pydemod.app.amss as amss

import sys


# symbolLength: expressed in samples
# (it is twice the bitrate of 46.875 since every bit is coded by
# 2 manchester symbols
def amss_deshape(signal, symbolLength):
    # logical version of the signal (0 - 1)
    logical = numpy.array(signal >= 0, int)
    changes = numpy.diff(logical)
    
    manchesterThreshold = 1.6*symbolLength
    
    changeInstants = numpy.nonzero(changes)[0]
    changeLengths = numpy.diff(changeInstants)
    
    print "changeLengths = " + str(changeLengths)
    
    # reconstruct pulse stream
    #pulseStream = changes[changeInstants]
    pulseStream = []
    for i in range(changeLengths.size):
        if changeLengths[i] > manchesterThreshold and len(pulseStream) > 0:
            pulseStream.append(pulseStream[-1])
        pulseStream.append(changes[changeInstants[i+1]])
        
    return pulseStream




##### MAIN PROGRAM #####

(sampleRate, samples) = wavfile.read(sys.argv[1])

(avgPeriod, deltaPhiF) = phasemod.naive_phase_demod(samples)

manchesterPeriod = sampleRate / 46.875 / avgPeriod / 2

bits = manchester.manchester_decode(amss_deshape(deltaPhiF, manchesterPeriod))


# find pair-impulse sync
# must find 2 pulses with the same value


#print bits

word_stream = poly.amss_code.bitstream_to_wordstream(bits)

print word_stream


s = amss.Station()

s.process_stream(word_stream)


#mplot.plot(deltaPhi)
#mplot.plot(deltaPhiF)
#mplot.show()
