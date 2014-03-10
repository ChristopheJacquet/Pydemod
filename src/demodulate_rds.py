#!/usr/bin/python

# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod


# Sources of documentation:
# http://www.db-thueringen.de/servlets/DerivateServlet/Derivate-18898/54_IWK_2009_1_0_08.pdf
# http://dsp.stackexchange.com/questions/8456/how-to-perform-carrier-phase-recovery-in-software#8462

from scipy import signal
import numpy
import matplotlib.pyplot as plt
import math
import cmath

import scipy.io.wavfile as wavfile

import sys

import io

import argparse

import pydemod.filters.shaping as shaping_filter


parser = argparse.ArgumentParser(description='Demodulates RDS bitstreams from FM multiplex basedband', epilog='The demodulated bitstream may be decoded using, for instance, RDS Surveyor: java -jar rdssurveyor.jar -inbinstrfile bitstream_file')

parser.add_argument("--input", type=str, default=None, help='Input WAV file at 228 kHz')
parser.add_argument("--output", type=str, default=None, help="Output bitstream (text file composed of 0's and 1's)")

args = parser.parse_args()

if args.input == None or args.output == None:
    print("Must provide --input and --output")


# captured using: rtl_fm -f 87.8M -s 228000 -l 0 fi878.raw

sampleRate, samples = wavfile.read(args.input)

if sampleRate != 228000:
    print("Only supports WAV files at 228 kHz currently.")

samples = samples.astype(float) / max(abs( samples ))


print( "Sample rate: {} Hz, duration: {} s".format(sampleRate, len(samples) / float(sampleRate)) )


filt57k = signal.remez(512, numpy.array([0, 53000, 54000, 60000, 61000, sampleRate/2]), numpy.array([0, 1, 0]), Hz = sampleRate)

rdsBand = signal.convolve(samples, filt57k)


# quadrature sampling

# ensure array is of length 4*N
rdsBand = rdsBand[:(len(rdsBand)/4)*4]

c57 = numpy.tile( [1., -1.], len(rdsBand)/4 )

xi = rdsBand[::2] * c57
xq = rdsBand[1::2] * (-c57)


# low-pass filter

filtLP = signal.remez(400, [0, 2400, 3000, sampleRate/4], [1, 0], Hz=sampleRate/2)

xfi = signal.convolve(xi, filtLP)
xfq = signal.convolve(xq, filtLP)


# shape filter

shapeFilt = shaping_filter.rrcosfilter(300, 1, 1/(2*1187.5), sampleRate/2) [1]

xsfi = signal.convolve(xfi, shapeFilt)
xsfq = signal.convolve(xfq, shapeFilt)


if len(xsfi) % 2 == 1:
    xsfi = xsfi[:-1]
    xsfq = xsfq[:-1]

# downsample

xdi = (xsfi[::2] + xsfi[1::2]) / 2
xdq = xsfq[::2]



# remove phase drift using a moving average

smooth = 1/200. * numpy.ones(200)

angles = numpy.where(xdi >= 0, numpy.arctan2(xdq, xdi), numpy.arctan2(-xdq, -xdi))

theta = (signal.convolve(angles, smooth)) [-len(xdi):]

xr = (xdi + 1j * xdq) * numpy.exp(-1j * theta)


# binarize the phase modulation

bi = (numpy.real(xr) >= 0) + 0


# sample symbols using a discrete PLL

#sampleInstants = numpy.zeros(len(bi))

period = 24
halfPeriod = period/2
corr = period / 24.
phase = 0

res = ""
pin = 0

stats = {0: 0, 1: 1}
oddity = 0

latestXrSquared = [0]*8
lxsIndex = 0
theta = [0]
#thetaShift = [0]
shift = 0

#xpi = []
#xpq = []
#xppi = []
#xppq = []


for i in range(1, len(bi)):
    if bi[i-1] != bi[i]:  # transition
        if phase < halfPeriod-2:
            phase += corr
            #sampleInstants[i] = .5
        elif phase > halfPeriod+2:
            phase -= corr
            #sampleInstants[i] = -.5
        else:
            pass
            #sampleInstants[i] = .1
    if phase >= period:
        #sampleInstants[i] = 2*bi[i]-1
        phase -= period
            
        latestXrSquared[lxsIndex] = (xdi[i] + 1j * xdq[i])**2
        lxsIndex += 1
        if lxsIndex >= len(latestXrSquared):
            lxsIndex = 0
        
        th = shift + cmath.phase(sum(latestXrSquared)) / 2
        if abs(th - theta[-1]) > 2:
            if th < theta[-1]:
                shift += math.pi
                th += math.pi
                #thetaShift.append(10)
            else:
                shift -= math.pi
                th -= math.pi
                #thetaShift.append(-10)
            #bitphase ^= 1
        else:
            pass
            #thetaShift.append(0)
        theta.append(th)

        oddity += 1

        if oddity == 2:
            oddity = 0
            
            yp = (xdi[i] + 1j * xdq[i])
            #xpi.append(yp.real)
            #xpq.append(yp.imag)
            
            ypp = cmath.exp(-1j * th) * yp
            #xppi.append(ypp.real)
            #xppq.append(ypp.imag)

            # bit decode
            nin = 1 * (ypp.real > 0)
            stats[nin] += 1
            res += "{}".format(pin ^ nin)
            pin = nin


    phase += 1

# write output

f = io.open(args.output, "w")
f.write(unicode(res))
f.close()
