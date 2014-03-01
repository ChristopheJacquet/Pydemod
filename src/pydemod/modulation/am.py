# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2014
# Licence: GNU GPL v3
# See: https://github.com/ChristopheJacquet/Pydemod

import math
import numpy

def modulate(baseband_samples, sample_rate, frequency, phase=0):
    carrier = numpy.sin(2*math.pi * numpy.arange(len(baseband_samples)) * frequency / sample_rate + phase)
    return baseband_samples * carrier