#!/usr/bin/python

# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013, 2016
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/

# Examples:
#   rtl_fm -M am -f 434.05M -s 160k -  |./decode_weather.py --protocol conrad --squelch 4000 --rawle -
#   rtl_fm -M am -f 868.4M -s 160k -  |./decode_weather.py --protocol tx29 --squelch 4000 --rawle -

import pydemod.coding.logic as logic
from pydemod.app import weather_sensors

import scipy.io.wavfile as wavfile
import numpy

import sys
import io
import argparse
import struct


parser = argparse.ArgumentParser(description='Decodes TFA temperature and humidity sensors')

parser.add_argument("--protocol", type=str, default="", help='Protocol: tx29 or conrad')
parser.add_argument("--bitrate", type=int, default=17200, help='Bit rate of the transmission, in bit/s')
parser.add_argument("--synclen", type=int, default=8, help='Number of sync bits (these bits will be ignored)')
parser.add_argument("--wav", type=str, default="", help='Run in WAV mode. Expects a WAV file that contains a single data frame')
parser.add_argument("--raw", type=str, default="", help='Run in raw mode, continuously. Expects a raw file sampled at 160 kHz, 16-bit signed big endian. Use "-" to read from stdin. \nExample: rtl_fm -M am -f 868.4M -s 160k -  |./decode_weather.py --squelch 4000 --raw -')
parser.add_argument("--rawle", type=str, default="", help='Same as --raw, but reads 16-bit signed *little* endian samples')
parser.add_argument("--squelch", type=int, default=4000, help='Squelch level for raw mode')
parser.add_argument("--window_duration", type=int, default=None, help='Squelch window duration, in samples')
parser.add_argument("--passthrough", type=str, default='')
parser.add_argument("--verbose", help='Print additional debug messages', action="store_true")

args = parser.parse_args()


def rx_tx29(samples, sampleRate, unused_squelch):
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
     
        return weather_sensors.decode_tx29(frame[(synclen + 16):])


def rx_conrad(samples, sampleRate, squelch):
    threshold = squelch #numpy.mean(samples)
    binarized = numpy.array(samples > threshold, dtype=int)
    diff = binarized[1:] - binarized[:-1]
    edges = ((diff > 0).nonzero())[0]
    lengths = edges[1:] - edges[:-1]
    #print(lengths)
    reports = []
    s = ""
    for l in lengths:
        if l < 550:
            s += "0"
        elif l < 1000:
            s += "1"
        else:
            if len(s) > 1:
                print(s)
                r = weather_sensors.decode_conrad(s)
                s = ""
                if r:
                    reports.append(r)
    return weather_sensors.most_frequent_report(reports)


def decode(callback=None):
    global bitrate, synclen, framelen

    bitrate = args.bitrate
    synclen = args.synclen
    
    if args.protocol == "tx29":
        rx = rx_tx29
        framelen = 56 + synclen
        repeats = 1
    elif args.protocol == "conrad":
        rx = rx_conrad
        framelen = 42
        repeats = 6
        bitrate = 200

    print("Bitrate: {0}, synclen: {1}, framelen: {2}".format(bitrate, synclen, framelen))

    if len(args.wav) > 0:
        (sampleRate, samples) = wavfile.read(args.wav)
        # FIXME decode(samples, sampleRate)
    elif len(args.raw) > 0 or len(args.rawle) > 0:
        if len(args.raw) > 0:
            filename = args.raw
        else:
            filename = args.rawle
        if(filename == "-"):
            filename = sys.stdin.fileno()
        srate = 160000
        fin = io.open(filename, mode="rb")

        framedur = 1.2 * ( framelen / float(bitrate) * srate ) * repeats
        print("Using frame duration {0:0.1f} samples".format(framedur))
        print("Squelch at {0}, should be slightly greater than usual max; use --squelch to change".format(args.squelch))

        inFrameCount = 0

        num = srate/10
        if len(args.raw) > 0:
            fmt = ">{}H".format(num)
        else:
            fmt = "<{}H".format(num)

        while True:
            b = fin.read(num*2)
            if len(b) == num*2:
                vals = struct.unpack(fmt, b)
            
                vsum = sum(vals)
                vmin = min(vals)
                vmax = max(vals)
                nvals = numpy.array(vals)
                aboveSquelch = (nvals >= args.squelch).sum()
                fracAboveSquelch = float(aboveSquelch) / len(vals)
                percentile90 = numpy.percentile(nvals, 95)

                sys.stdout.write("\rMin: {} - Mean: {} - Max: {} - 90th percentile: {} - Above squelch: {} %             ".format(vmin, vsum / num, vmax, percentile90, int(fracAboveSquelch*100)))
                sys.stdout.flush()

                # Iterate over all samples if currently decoding frame or if a sample
                # opens the squelch.
                if inFrameCount > 0 or vmax > args.squelch:
                    for val in vals:
                        if(inFrameCount > 0):
                            frameSamples.append(val)
                            inFrameCount += 1
                            if(inFrameCount > framedur):
                                print("\n---------------------------------------")
                                report = rx(numpy.array(frameSamples, dtype=float), srate, args.squelch)
                                print("==> {}".format(report))
                                print("---------------------------------------")
                                inFrameCount = 0
                                if report and callback:
                                    callback(report)
                        elif(val > args.squelch):
                            frameSamples = [0, 0, val]
                            inFrameCount = 3
            else:
                print "\nEOF"
                break
    
    else:
        print("You must use --wav or --raw. See help.")


if __name__ == "__main__":
    decode()