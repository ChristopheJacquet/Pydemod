#!/usr/bin/python

# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod

import argparse
import numpy
import numpy.random as random
import scipy.io.wavfile as wavfile
from scipy import signal

import pydemod.app.rds as rds
import pydemod.modulation.am as am


parser = argparse.ArgumentParser(description='Generates RDS bitstreams, or RDS baseband samples')

parser.add_argument("--ps", type=str, default="PyDemod", help='Program Service Name')
parser.add_argument("--pi", type=str, default="FFFF", help='PI code')
parser.add_argument("--len", type=int, default=2, help='Duration in seconds')
parser.add_argument("--bitstream", help='Generates a bitstream', action="store_true")
parser.add_argument("--unmodulated", help='Generates the unmodulated signal at 228 kHz', action="store_true")
parser.add_argument("--baseband", help='Generates basedband samples at 228 kHz', action="store_true")
parser.add_argument("--phase", type=float, default=0, help='Phase of the 57 kHz carrier in radians (use in cunjunction with --baseband)')
parser.add_argument("--frequency", type=float, default=57000, help='Frequency of the "57 kHz" carrier in hertz (use in cunjunction with --baseband)')
parser.add_argument("--noise", type=float, default=0, help='Relative noise. RDS signal is 1. (use in cunjunction with --baseband)')
parser.add_argument("--tune", type=float, default=None, help='At a tune at the given frequency')
parser.add_argument("--ootune", type=float, default=None, help='At an on/off tune at the given frequency, with a half-period of 1 second')
parser.add_argument("--wavout", type=str, default=None, help='Output WAV file')

args = parser.parse_args()

bitstream = rds.bitstream(rds.generate_basic_wordstream(int(args.pi, 16), args.ps), args.len)

if args.bitstream:
    print("".join(map(str, bitstream)))
elif args.unmodulated or args.baseband:
    if args.wavout == None:
        print("--wavout required")
        exit()
    sample_rate = 228000

    shapedSamples = rds.unmodulated_signal(bitstream, sample_rate)
    
    if args.unmodulated:
        out = shapedSamples
    elif args.baseband:
        out = am.modulate(shapedSamples, sample_rate, args.frequency, args.phase)
        if args.tune:
            out += 2 * numpy.sin(2*numpy.pi * args.tune * numpy.arange(len(out)) / sample_rate)
        elif args.ootune:
            out += numpy.sin(2*numpy.pi * args.ootune * numpy.arange(len(out)) / sample_rate) * (1 + signal.square(2*numpy.pi * .5 * numpy.arange(len(out)) / sample_rate))
        if args.noise > 0:
            out = out + random.rand(len(out)) * args.noise*max(abs(out))
    
    iout = (out * 20000./max(abs(out)) ).astype(numpy.dtype('>i2'))
    
    wavfile.write(args.wavout, sample_rate, iout)
else:
    print("Either --bitstream or --unmodulated or --baseband must be provided.")
