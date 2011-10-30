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
    givenCRC = take(binaryMsg, binaryMsg.size-8, 8)
    print "CRC: calculated={0:02X}, received={1:02X}".format(crc.crc(0x31, 8, 0, 0, binaryMsg[:-8]), givenCRC)
    temperature = (take(binaryMsg, 12, 4) * 10 + take(binaryMsg, 16, 4) + take(binaryMsg, 20, 4) * .1) - 40
    humidity = take(binaryMsg, 24, 8)
    if humidity == 106:
        humidity = "N/A"
    print "Temperature: {0:0.1f} C -- Humidity: {1} %".format(temperature, humidity)