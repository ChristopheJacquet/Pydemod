#!/usr/bin/python

#
# Frame structure on an example:
#   AA - sync byte (sometimes multiple sync bytes)
#   2D \ presumably a vendor/sensor type identifier
#   D4 /
#   96 \   follows the same protocol as LaCrosse's TX29  -> 9 nibbles following
#   45  |  0x64 -> sensor ID ?
#   47  |  0x574 -> (temperature + 40) * 10 in BCD  --> 17.4 C
#   4D  |  0x4D -> 77 % humidity
#   0B /
# The CRC is calculated on the last 4 bytes before the 1-byte CRC
#

import pydemod.app.lacrosse as lacrosse
import pydemod.coding.logic as logic

import scipy.io.wavfile as wavfile
import numpy

import sys


import argparse

parser = argparse.ArgumentParser(description='Decodes TFA temperature and humidity sensors')

parser.add_argument("filename", type=str, help='WAV file to process')
parser.add_argument("--bitrate", type=int, default=17200, help='Bit rate of the transmission, in bit/s')
parser.add_argument("--synclen", type=int, default=8, help='Number of sync bits (these bits will be ignored)')
parser.add_argument("--verbose", help='Print additional debug messages', action="store_true")

args = parser.parse_args()

bitrate = args.bitrate
synclen = args.synclen
framelen = 56 + synclen

print("Bitrate: {0}, synclen: {1}, framelen: {2}".format(bitrate, synclen, framelen))

(sampleRate, samples) = wavfile.read(args.filename)

frame = logic.decode_0xAA_prefixed_frame(samples, sampleRate, bitrate=bitrate, verbose=args.verbose)

if frame.size < framelen:
    frame = numpy.append(frame, [0] * (framelen - frame.size))

print "Frame: size {0} bits, contents {1}, framelen={2}".format(frame.size, frame, framelen)

if frame.size >= framelen:
    frame = frame[:framelen]
    # reconstruct bytes
    matrix = numpy.mat(numpy.reshape(frame, (framelen/8, 8)))
    byteSeq = matrix * numpy.mat("128;64;32;16;8;4;2;1")
    allBytes = [int(byteSeq[i]) for i in range(0,len(byteSeq))]
    print "Frame hex contents: " + " ".join(["{0:02X}".format(b) for b in allBytes])
     
    lacrosse.decode_tx29(frame[(synclen + 16):])
    
