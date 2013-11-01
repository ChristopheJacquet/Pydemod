#!/usr/bin/python

#
# Frame structure on an example:
#   AA - sync byte
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

(sampleRate, samples) = wavfile.read(sys.argv[1])

frame = logic.decode_0xAA_prefixed_frame(samples, sampleRate)

if frame.size < 64:
    frame = numpy.append(frame, [0] * (64 - frame.size))

print "Frame: size {0} bits, contents {1}".format(frame.size, frame)

if frame.size >= 64:
    frame = frame[:64]
    matrix = numpy.mat(numpy.reshape(frame, (8, 8)))
    byteSeq = matrix * numpy.mat("128;64;32;16;8;4;2;1")
    allBytes = [int(byteSeq[i]) for i in range(0,8)]
    messageBytes = allBytes[0:7]
    print "Frame hex contents: " + " ".join(["{0:02X}".format(b) for b in messageBytes])
     
    lacrosse.decode_tx29(frame[24:])
    
