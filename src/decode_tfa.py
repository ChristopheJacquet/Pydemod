#!/usr/bin/python

# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/

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
import io
import argparse


parser = argparse.ArgumentParser(description='Decodes TFA temperature and humidity sensors')

parser.add_argument("--bitrate", type=int, default=17200, help='Bit rate of the transmission, in bit/s')
parser.add_argument("--synclen", type=int, default=8, help='Number of sync bits (these bits will be ignored)')
parser.add_argument("--wav", type=str, default="", help='Run in WAV mode. Expects a WAV file that contains a single data frame')
parser.add_argument("--raw", type=str, default="", help='Run in raw mode, continuously. Expects a raw file sampled at 160 kHz, 16-bit signed big endian. Use "-" to read from stdin. \nExample: rtl_fm -M -f 868.4M -s 160k -  |./decode_tfa.py --squelch 4000 -')
parser.add_argument("--squelch", type=int, default=4000, help='Squelch level for raw mode')
parser.add_argument("--verbose", help='Print additional debug messages', action="store_true")

args = parser.parse_args()


def decode(samples, sampleRate):
    frame = logic.decode_0xAA_prefixed_frame(samples, sampleRate, bitrate=bitrate, verbose=args.verbose)

    if frame.size < framelen:
        frame = numpy.append(frame, [0] * (framelen - frame.size))

    print "Frame: size {0} bits, contents {1}, framelen={2}".format(frame.size, "".join(map(str, frame.tolist())), framelen)

    if frame.size >= framelen:
        frame = frame[:framelen]
        # reconstruct bytes
        matrix = numpy.mat(numpy.reshape(frame, (framelen/8, 8)))
        byteSeq = matrix * numpy.mat("128;64;32;16;8;4;2;1")
        allBytes = [int(byteSeq[i]) for i in range(0,len(byteSeq))]
        print "Frame hex contents: " + " ".join(["{0:02X}".format(b) for b in allBytes])
     
        lacrosse.decode_tx29(frame[(synclen + 16):])
    



bitrate = args.bitrate
synclen = args.synclen
framelen = 56 + synclen

print("Bitrate: {0}, synclen: {1}, framelen: {2}".format(bitrate, synclen, framelen))

if len(args.wav) > 0:
    (sampleRate, samples) = wavfile.read(args.wav)
    decode(samples, sampleRate)
elif len(args.raw) > 0:
    filename = args.raw
    if(filename == "-"):
        filename = sys.stdin.fileno()
    srate = 160000
    fin = io.open(filename, mode="rb")

    framedur = 1.2 * ( framelen / float(bitrate) * srate )
    print("Using frame duration {0:0.1f} samples".format(framedur))
    print("Squelch at {0}, should be slightly greater than usual max; use --squelch to change".format(args.squelch))

    count = 0
    sum = 0.
    max = 0.
    min = 100000.
    
    inFrameCount = 0

    while True:
        b = fin.read(2)
        if len(b) == 2:
            val = ord(b[0])*256+ord(b[1])  # big endian
            sum += val
            if val < min: min = val
            if val > max: max = val
            count += 1
            
            if(inFrameCount > 0):
                frameSamples.append(val)
                inFrameCount += 1
                if(inFrameCount > framedur):
                    print("\n---------------------------------------")
                    decode(numpy.array(frameSamples, dtype=float), srate)
                    print("---------------------------------------")
                    inFrameCount = 0
            elif(val > args.squelch):
                frameSamples = [0, 0, val]
                inFrameCount = 3
    
        if count == srate/2:
            sys.stdout.write("\rMin: {0} - Mean: {1} - Max: {2}             ".format(min, sum / count, max))
            sys.stdout.flush()
            sum = 0.
            max = 0.
            min = 100000.
            count = 0
else:
    print("You must use --wav or --raw. See help.")


