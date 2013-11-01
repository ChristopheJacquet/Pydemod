import numpy

def decode_0xAA_prefixed_frame(samples, sampleRate):
    threshold = ( max(samples) + min(samples) ) / 2

    print("Min={0}, Max={1}, Threshold={2}".format(min(samples), max(samples), threshold))
    
    signs = numpy.array(samples > threshold, int)
    differences = numpy.diff(signs)
    changes = numpy.nonzero(differences)[0]

    print("27:{2}, 28:{0}, 29:{1}".format(signs[28], signs[29], signs[27]))
    
    print "{0} edges at instants: {1}".format(changes.size, changes)
    
    bitlen = 356./64. * sampleRate/ 96000     # measured duration at 96kHz: 356 samples (17258 bit/s)
    
    print "Theoretical bit length: {0} samples".format(bitlen)
    
    result = numpy.array([])
    
    i = (changes[0]+1) + bitlen/2
    bitpos = bitlen
    precBit = signs[i]
    
    # simple software PLL
    while i < samples.size:
        bit = signs[i]

        if precBit != bit:
            print("Transition at {0}, expected at {1}".format(i, bitlen/2-bitpos+i))
        
            if bitpos < bitlen/2-1:
                bitpos += bitlen/20.
                print("(+)")
            elif bitpos > bitlen/2+1:
                bitpos -= bitlen/20.
                print("(-)")

        
        if bitpos >= bitlen:
            result = numpy.append(result, bit)
            bitpos -= bitlen
            
            print("Sample at {0} => {1} (bitpos={2})".format(i, bit, bitpos))

    
        precBit = bit
        i += 1
        bitpos += 1
    return result.astype(int)
