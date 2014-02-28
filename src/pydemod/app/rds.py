import pydemod.coding.polynomial as poly

def generate_basic_wordstream(pi, psName):
    """
    Generates a basic stream of 0B group stream for a given station name.
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
    wordstream = [next(gen) for i in range(int(seconds * 1187.5 / 104))]
    return poly.rds_code.wordstream_to_bitstream(wordstream)