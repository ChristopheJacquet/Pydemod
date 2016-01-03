# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013, 2016
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/


'''
Decoding of LaCrosse sensor data
'''

import pydemod.coding.crc as crc
import numpy


def take(vec, u, l):
    return numpy.dot( numpy.power(2, numpy.arange(l-1, -1, -1)), vec[u:u+l])

# CRC parameters: 8 bits, polynomial x^8 + x^5 + x^4 + 1 (0x31)
#                 initial value 0, final xor value 0
#
def decode_tx29(binaryMsg):
    # lengths counts 4 bits (nibbles) excluding 1st one
    givenLength = take(binaryMsg, 0, 4)
    actualLength = len(binaryMsg) / 4 - 1
    print "Length: actual={0:02X}, received={1:02X}, valid={2}".format(actualLength, givenLength, "yes" if (givenLength == actualLength) else "no")
    givenCRC = take(binaryMsg, binaryMsg.size-8, 8)
    computedCRC = crc.crc(0x31, 8, 0, 0, binaryMsg[:-8])
    print "CRC: computed={0:02X}, received={1:02X}, valid={2}".format(computedCRC, givenCRC, "yes" if (givenCRC == computedCRC) else "no")
    devID = take(binaryMsg, 4, 6)
    print "Device: id={0:02X}".format(devID)
    newBattery = take(binaryMsg, 10, 1)
    weakBattery = take(binaryMsg, 24, 1)
    print "Battery: new={0}, weak={1}".format("yes" if newBattery else "no", "yes" if weakBattery else "no")
    temperature = (take(binaryMsg, 12, 4) * 10 + take(binaryMsg, 16, 4) + take(binaryMsg, 20, 4) * .1) - 40
    reserved = take(binaryMsg, 11, 1)
    print "Reserved 0 bit: received={0:01X}, valid={1}".format(reserved, "yes" if (reserved == 0) else "no")
    humidity = take(binaryMsg, 25, 7)
    if humidity == 106:
        humidity = "N/A"
    print "Temperature: {0:0.1f} C -- Humidity: {1} %".format(temperature, humidity)
