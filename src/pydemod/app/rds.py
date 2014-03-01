# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod

import numpy

import pydemod.coding.polynomial as poly
import pydemod.filters.shaping as shaping

def generate_basic_wordstream(pi, psName):
    """
    Generates a basic RDS stream composed of 0B groups for a given PI code
    and station name.
    """
    
    if pi < 0 or pi > 0xFFFF:
        raise Exception("PI code must be between 0x0000 and 0xFFFF")
    
    if len(psName) > 8:
        raise Exception("PS name must not be more than 8 characters long")
    
    psName += " " * (8 - len(psName))
    
    while True:
        for i in range(4):
            yield ('A', pi & 0xFFFF)
    
            yield ('B', 0x0800 | i)
    
            yield ("C'", pi & 0xFFFF)
            
            yield ('D', (ord(psName[i*2])<<8) + ord(psName[i*2+1]))



def bitstream(gen, seconds):
    wordstream = [next(gen) for i in range(int(seconds * 1187.5 / 26))]
    return poly.rds_code.wordstream_to_bitstream(wordstream)
    

def pulse_shaping_filter(length, sample_rate):
    return shaping.rrcosfilter(length, 1, 1/(2*1187.5), sample_rate+1) [1]


def unmodulated_signal(bitstream, sample_rate = 228000):
    samples_per_bit = int(sample_rate / 1187.5)
    
    # Differentially encode
    diffbs = numpy.zeros(len(bitstream), dtype=int)
    for i in range(1, len(bitstream)):
        if diffbs[i-1] != bitstream[i]:
            diffbs[i] = 1
    
    # Positive symbol pattern
    symbol = numpy.zeros(samples_per_bit)
    symbol[0] = 1
    symbol[samples_per_bit/2-1] = -1
    
    # Generate the sample array
    samples = numpy.tile(symbol, len(diffbs))
    for i in range(len(diffbs)):
        if diffbs[i] == 0:
            samples[i * samples_per_bit : (i+1)*samples_per_bit] *= -1
    
    # Apply the data-shaping filter
    shapedSamples = numpy.convolve(samples, pulse_shaping_filter(samples_per_bit*2, sample_rate))

    return shapedSamples