import numpy


# naive phase demodulation
def naive_phase_demod(samples):
    size = samples.size
    
    print(f"{size} samples, min={samples.min()}, max={samples.max()}")
    
    # find zero crossings
    signs = numpy.array(samples >= 0, int)      # need to have integers
    
    differences = numpy.diff(signs)
    
    print(differences)
    
    crossings = numpy.nonzero(differences < 0)[0]
    
    # the first zero crossing is meaningless, since it does not count time since
    # another zero crossing, but since t = 0
    cumulWidths = crossings[1:] - crossings[0]
    print(f"cumulWidths = {cumulWidths}")
    
    # average period
    numPeriods = cumulWidths.size
    avgPeriod = cumulWidths[-1] / (1. * numPeriods)
    print(f"number of periods considered: {numPeriods}, average period length: {avgPeriod}")
    
    # deltaPhi
    deltaPhi = cumulWidths - numpy.linspace(avgPeriod, avgPeriod * numPeriods, numPeriods)
    print(f"deltaPhi = {deltaPhi} (sz={deltaPhi.size})")
    
    #filterNum = signal.firwin(5000, 1./5, window='hamming')
    #filterDen = 1
    #deltaPhiF = signal.lfilter(filterNum, filterDen, deltaPhi) 
    
    # filter deltaPhi with a high-pass filter
    # TODO: properly design this filter
    # TODO: use scipy to apply this filter
    S = 50
    deltaPhiF = numpy.zeros(numPeriods)
    for i in range(S-1, numPeriods-S-1):
        win = deltaPhi[i-S//2 : i+S//2]
        # right bound is excluded in Python -> S samples
        deltaPhiF[i] = deltaPhi[i] - numpy.sum(win) / S
    
    return (avgPeriod, deltaPhiF)
