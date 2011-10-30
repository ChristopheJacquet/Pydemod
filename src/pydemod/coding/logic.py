import numpy

def decode_0xAA_prefixed_frame(samples, sampleRate):
    threshold = ( max(samples) + min(samples) ) / 2
    
    signs = numpy.array(samples > threshold, int)
    differences = numpy.diff(signs)
    changes = numpy.nonzero(differences)[0]
    
    print "{0} edges at instants: {1}".format(changes.size, changes)
    
    bitlen = float(changes[7] - changes[0]) / 7.
    thbitlen = 356./64. * sampleRate/ 96000     # measured duration at 96kHz: 356 samples (17258 bit/s)
    
    print "Bit length: {0} samples; theoretical {1} samples".format(bitlen, thbitlen)
    
    #bitlen = thbitlen
    
    result = numpy.array([1, 0, 1, 0, 1, 0, 1])
    
    for i in range(8, changes.size):
        count = int(round((changes[i] - changes[i-1]) / bitlen))
        
        # the value of the bits to add is the value of the sample just before
        # the change 
        ##print result
        result = numpy.append(result, [signs[changes[i]-1]] * count)
        
        # adjust bit length depending on the beginning of the frame
        # the more bits received, the better the average value
        bitlen = float(changes[i] - changes[0]) / result.size
        
        print "Edge at {1}: error {0:.3} samples, len={2}, new bitlen={3}".format(bitlen*count - (changes[i] - changes[i-1]), changes[i], count, bitlen)

    return result