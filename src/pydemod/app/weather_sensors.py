# This file is part of Pydemod
# Copyright Christophe Jacquet (F8FTK), 2011, 2013, 2016
# Copyright Krzysztof Burghardt, 2016
# Licence: GNU GPL v3
# See: https://code.google.com/p/pydemod/


import pydemod.coding.crc as crc
import numpy


class Report:
    def __init__(self, temperature, humidity, type, id, channel=None):
        self.temperature = temperature
        self.humidity = humidity
        self.type = type
        self.id = id
        self.channel = channel
    
    def __eq__(self, other):
        return (self.temperature == other.temperature and self.humidity == other.humidity and
            self.type == other.type and self.id == other.id and self.channel == other.channel)
    
    def __str__(self):
        return "//{}/{:02X}{}: Temp={:+0.1f} C, Humid={} %".format(
            self.type, self.id, "/{}".format(self.channel) if self.channel != None else "",
            self.temperature, self.humidity)
        
    def __hash__(self):
        return hash(repr(self))


def most_frequent_report(reports):
    counts = {}
    most_frequent_report = None
    most_frequent_count = 0
    for r in reports:
        counts[r] = counts.setdefault(r, 0) + 1
        if counts[r] > most_frequent_count:
            most_frequent_count = counts[r]
            most_frequent_report = r
    return most_frequent_report
    

def take(vec, u, l):
    return numpy.dot( numpy.power(2, numpy.arange(l-1, -1, -1)), vec[u:u+l])


def int_from_bits(bits):
    res = 0
    for b in bits:
        res = (res<<1) + int(b)
    return res


def parse_bitfield(descriptor, bitfield):
    # Check if bitfield has the length prescribed by the descriptor.
    if sum(d[1] for d in descriptor) != len(bitfield):
        return None
    pos = 0
    result = {}
    for d in descriptor:
        if len(d) == 2:
            field, length = d
            endianness = True # Big Endian
        elif len(d) == 3:
            field, length, endianness = d
        if field:
            result[field] = int_from_bits(bitfield[pos:pos+length] if endianness else bitfield[pos+length-1:pos-1:-1])
        pos += length
    return result


#
# Frame structure on an example:
#   AA - sync byte (sometimes multiple sync bytes)
#   2D \ presumably a vendor/sensor type identifier
#   D4 /
#   96 \   follows the same protocol as LaCrosse's TX29  -> 9 nibbles following
#   45  |  0x64 -> sensor ID ?
#   47  |  0x574 -> (temperature + 40) * 10 in BCD  --> 17.4 C
#   4D  |  0x4D -> 77 % humidity
#   0B /
# The CRC is calculated on the last 4 bytes before the 1-byte CRC
#
# CRC parameters: 8 bits, polynomial x^8 + x^5 + x^4 + 1 (0x31)
#                 initial value 0, final xor value 0
#
def decode_tx29(binaryMsg):
    '''
    Decoding a LaCrosse/TFA sensor message.
    '''
    # lengths counts 4 bits (nibbles) excluding 1st one
    givenLength = take(binaryMsg, 0, 4)
    actualLength = len(binaryMsg) / 4 - 1
    print("Length: actual={:02X}, received={:02X}, valid={}".format(actualLength, givenLength, "yes" if (givenLength == actualLength) else "no"))
    givenCRC = take(binaryMsg, binaryMsg.size-8, 8)
    computedCRC = crc.crc(0x31, 8, 0, 0, binaryMsg[:-8])
    print("CRC: computed={:02X}, received={:02X}, valid={}".format(computedCRC, givenCRC, "yes" if (givenCRC == computedCRC) else "no"))
    devID = take(binaryMsg, 4, 6)
    print("Device: id={:02X}".format(devID))
    newBattery = take(binaryMsg, 10, 1)
    weakBattery = take(binaryMsg, 24, 1)
    print("Battery: new={}, weak={}".format("yes" if newBattery else "no", "yes" if weakBattery else "no"))
    temperature = (take(binaryMsg, 12, 4) * 10 + take(binaryMsg, 16, 4) + take(binaryMsg, 20, 4) * .1) - 40
    reserved = take(binaryMsg, 11, 1)
    print("Reserved 0 bit: received={:01X}, valid={}".format(reserved, "yes" if (reserved == 0) else "no"))
    humidity = take(binaryMsg, 25, 7)
    if humidity == 106:
        humidity = "N/A"
    print("Temperature: {:+0.1f} C -- Humidity: {} %".format(temperature, humidity))
    if givenCRC == computedCRC:
        return Report(temperature, humidity, "TX29", devID)


def conrad_crc(msg, final):
    c = 0
    for bit in msg:
        if int(bit) != (c&1):
            c = (c>>1) ^ 12
        else:
            c = c>>1
    return c ^ final


def decode_conrad(message):
    """
    TFA Dostmann 30.3200, s014, TCM, Conrad.
    """
    data = parse_bitfield([
        (None, 2),
        ("id", 8),
        (None, 2),
        ("channel", 2),
        ("temp_a", 4),
        ("temp_b", 4),
        ("temp_c", 4),
        ("humid_a", 4),
        ("humid_b", 4),
        ("final", 4, False),
        ("crc", 4, False),], message)
    # If the message does not have the expected length, return.
    if data == None:
        return
    temperature = ((data["temp_c"]*256 + data["temp_b"]*16 + data["temp_a"])/10. - 90 - 32) * 5/9.
    humidity = data["humid_b"]*16 + data["humid_a"]

    crc = conrad_crc(message[2:34], data["final"])
    
    print("Id={:02X}, Ch={}, Temp={:+0.1f} C, Humid={} %, CRC={} vs {}".format(
        data["id"], data["channel"], temperature, humidity, crc, data["crc"]))
    
    if crc == data["crc"]:
        return Report(temperature, humidity, "Conrad", data["id"], data["channel"])