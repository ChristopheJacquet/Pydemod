#!/usr/bin/python

# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod

import argparse
import numpy
import scipy.io.wavfile as wavfile

import pydemod.app.rds as rds
import pydemod.modulation.am as am


parser = argparse.ArgumentParser(description='Generates RDS bitstreams, or RDS baseband samples')

parser.add_argument("--ps", type=str, default="PyDemod", help='Program Service Name')
parser.add_argument("--pi", type=str, default="FFFF", help='PI code')
parser.add_argument("--len", type=int, default=2, help='Duration in seconds')
parser.add_argument("--bitstream", help='Generates a bitstream', action="store_true")
parser.add_argument("--unmodulated", help='Generates the unmodulated signal at 228 kHz', action="store_true")
parser.add_argument("--baseband", help='Generates basedband samples at 228 kHz', action="store_true")
parser.add_argument("--phase", type=float, default=0, help='Phase of the 57 kHz carrier (use in cunjunction with --baseband)')
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
        out = am.modulate(shapedSamples, sample_rate, 57000, args.phase)
    
    iout = (out * 20000./max(abs(out)) ).astype(numpy.dtype('>i2'))
    
    wavfile.write(args.wavout, sample_rate, iout)
else:
    print("Either --bitstream or --unmodulated or --baseband must be provided.")
