# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/


import numpy

def decode_0xAA_prefixed_frame(samples, sampleRate, bitrate=17258, verbose=False):
    threshold = numpy.mean(samples)

    if verbose:
        print("Min={0}, Max={1}, Threshold={2}".format(min(samples), max(samples), threshold))
    
    signs = numpy.array(samples > threshold, int)
    differences = numpy.diff(signs)
    changes = numpy.nonzero(differences)[0]

    if verbose:    
        print "{0} edges at instants: {1}".format(changes.size, changes)
    
    bitlen = sampleRate / bitrate
    
    if verbose:
        print "Theoretical bit length: {0} samples".format(bitlen)
    
    result = numpy.array([])
    
    i = (changes[0]+1) + bitlen/2
    bitpos = bitlen
    precBit = signs[i]
    
    # simple software PLL
    while i < samples.size:
        bit = signs[i]

        if precBit != bit:
            if verbose:
                print("Transition at {0}, expected at {1}".format(i, bitlen/2-bitpos+i))
        
            if bitpos < bitlen/2-1:
                bitpos += bitlen/10.
                if verbose:
                    print("(+)")
            elif bitpos > bitlen/2+1:
                bitpos -= bitlen/10.
                if verbose:
                    print("(-)")

        
        if bitpos >= bitlen:
            result = numpy.append(result, bit)
            bitpos -= bitlen
            
            if verbose:
                print("Sample at {0} => {1} (bitpos={2})".format(i, bit, bitpos))

    
        precBit = bit
        i += 1
        bitpos += 1
    return result.astype(int)
