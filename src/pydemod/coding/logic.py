# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/


import numpy

def decode_0xAA_prefixed_frame(samples, sampleRate, bitrate=17258, verbose=False):
    threshold = numpy.mean(samples)

    if verbose:
        print(f"Min={min(samples)}, Max={max(samples)}, Threshold={threshold}")
    
    signs = numpy.array(samples > threshold, int)
    differences = numpy.diff(signs)
    changes = numpy.nonzero(differences)[0]

    if verbose:    
        print(f"{changes.size} edges at instants: {changes}")
    
    bitlen = sampleRate / bitrate
    
    if verbose:
        print(f"Theoretical bit length: {bitlen} samples")
    
    result = numpy.array([])
    
    i = (changes[0]+1) + bitlen/2
    bitpos = bitlen
    precBit = signs[i]
    
    # simple software PLL
    while i < samples.size:
        bit = signs[i]

        if precBit != bit:
            if verbose:
                print(f"Transition at {i}, expected at {bitlen/2-bitpos+i}")
        
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
                print(f"Sample at {i} => {bit} (bitpos={bitpos})")

    
        precBit = bit
        i += 1
        bitpos += 1
    return result.astype(int)
