'''
CRC calculation routine
'''

def crc(poly, deg, start, finalXor, block):
    allones = pow(2, deg) - 1
    crc = start
    for bit in block:
        msb = (crc >> (deg-1)) & 1
        crc = (crc << 1) & allones
        i = msb ^ bit
        if i != 0:
            crc = crc ^ poly
    return crc ^ finalXor
