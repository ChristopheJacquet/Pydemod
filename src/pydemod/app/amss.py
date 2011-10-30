#!/usr/bin/python

import numpy
#import pydemod.coding.polynomial as poly
import math

import pydemod.coding.crc as crc

def copyto(dest, src, addr):
    for i in range(src.size):
        dest[addr+i] = src[i]


def decode_mjd(mjd):
    """
    Decodes a Modified Julian Date
    """
    yp = int((mjd - 15078.2)/365.25)
    mp = int( ( mjd - 14956.1 - math.floor(yp * 365.25) ) / 30.6001 )
    day = int(mjd - 14956 - math.floor( yp * 365.25 ) - math.floor( mp * 30.6001 ))
    if mp == 14 or mp == 15:
        k = 1
    else:
        k = 0
    year = int(1900 + yp + k)
    month = mp - 1 - k * 12
    return (year, month, day)

class Station:
    entry_types = ["Multiplex description", "Label", "Conditional access parameters", "AF: Multiple frequency network", "AF: Schedule definition", "Application information", "Announcement support and switching data", "AF: Region definition", "Time and date information", "Audio information", "FAC channel parameters", "AF: Other services", "Language and country", "AF: Detailed region definition", "Packet stream FEC parameters"]

    def take(self, vec, u, l):
        return numpy.dot( numpy.power(2, numpy.arange(l-1, -1, -1)), vec[u:u+l])
        
    def takestr(self, vec, u, nbchars):
        s = ""
        for i in range(nbchars):
            s = s + chr(self.take(vec, u+8*i, 8))
        return s
        

    def process_block(self, type, word):
        print "Block type: {0}".format(type)
        if type == 1:
            vflag = self.take(word, 0, 1)
            n_segments = self.take(word, 4, 4)+1
		
            if vflag != self.current_vflag:
                if self.num_segments != -1 and not self.processed and self.segments_ok[0]:
                    # if partially received, but segment 0 OK, try to decode anyway
                    self.process_sdc_group(self.current_data)
                # start of new data
                self.current_data = numpy.array(32 * n_segments * [0])
                self.current_vflag = vflag
                self.num_segments = n_segments
                self.segments_ok = [0] * self.num_segments
                self.processed = False
		
            print("\tVersion flag: {0}".format(vflag));
            print("\tAM carrier mode: {0}".format(self.take(word, 1, 3)) );
            print("\tNumber of segments: {0}".format(n_segments) );
            print("\tLanguage: {0}".format(self.take(word, 8, 4)) );
            print("\tService Identifier: {0:06X}".format(self.take(word, 12, 24) ));
        elif type == 2:
            addr = self.take(word, 0, 4)
            print("\tSegment address: {0}".format(addr))
            
            if self.num_segments != -1:
                self.segments_ok[addr] = 1
                copyto(self.current_data, word[4:36], 32*addr)
                print("\tMemorizing data: segment {0}/{1}. Segments ok: {2}".format(addr+1, self.num_segments, self.segments_ok))
                
                if numpy.sum(self.segments_ok) == self.num_segments and not self.processed:
                    self.processed = True
                    self.process_sdc_group(self.current_data)


    def process_sdc_group(self, data):
        print("************************************************************")
        print("SDC ENTRY GROUP: total {0} bits ({1} bytes)".format(data.size, data.size/8))
        given_crc = self.take(data, data.size-16, 16)
        data = data[:data.size-16]
        print "\tCRC: calc={0:04X}, given={1:04X}".format(crc.crc(0b0001000000100001, 16, 0xFFFF, 0xFFFF, data), given_crc)
        print("************************************************************")

        cont = True
        while cont:
            pos = self.process_sdc_entry(data)
            if pos < data.size:
                data = data[pos:]
            else:
                cont = 0

    
    # return total entry length
    def process_sdc_entry(self, data):
        len = self.take(data, 0, 7)
        version = self.take(data, 7, 1)
        type = self.take(data, 8, 4)
        
        print("SDC ENTRY: type={0}, version={1}, len=4 bits + {2} bytes (rem={3})".format(type, version, len, data.size/8))
        print(">> " + self.entry_types[type])
        print("------------------------------------------------------------")
        
        if type == 1:
            print("Short Id: {0}".format(self.take(data, 12, 2)))
            label = self.takestr(data, 16, len)
            print("Label: '{0}'".format(label))
            
        if type == 4:
            print("Schedule Id: {0}".format(self.take(data, 12, 4)))
            print("Days of week: {0:07b}".format(self.take(data, 16, 7)))
            time = self.take(data, 23, 11)
            print("Start time: {0:02d}:{1:02d}".format(time/60, time % 60))
            print("Duration: {0} min".format(self.take(data, 34, 14)))
            
        if type == 7:
            print("Region Id: {0}".format(self.take(data, 12, 4)))
            print("Latitude: {0}".format(self.take(data, 16, 8)))
            print("Longitude: {0}".format(self.take(data, 24, 9)))
            print("Latitude ext: {0}".format(self.take(data, 33, 7)))
            print("Longitude ext: {0}".format(self.take(data, 40, 8)))
            
            for i in range(len-4):
                print("CIRAF zone #{0}".format(self.take(data, 48+i*8, 8)))
            
        if type == 8:
            mjd = self.take(data, 12, 17)
            (year, month, day) = decode_mjd(mjd)
            time = self.take(data, 29, 11)
            print("Date: {0:04d}-{1:02d}-{2:02d}".format(year, month, day))
            print("UTC time: {0:02d}:{1:02d}".format(time/60, time%60))
            
        if type == 11:
            siaFlag = self.take(data, 12, 1)
            siaField = self.take(data, 13, 2)
            region = self.take(data, 15, 1)
            same = self.take(data, 16, 1)
            sysId = self.take(data, 19, 5)
            data = data[24:]
            aflen = len - 1     # must no touch len
            if region==1:   # if region/schedule bit set, additional byte:
                regionID = self.take(data, 0, 4)
                scheduleID = self.take(data, 4, 4)
                data = data[8:]
                aflen = aflen - 1
    
            
            print("AF,  same={0}, system={1}, len={2}, reg/sched={3}".format(same, sysId, len, region))
            
            if region == 1:
                print("Restricted to region Id {0} / schedule Id {1}".format(regionID, scheduleID))
    
            if sysId==0:
                print("DRM service, DRM Id = {0:06X}".format(self.take(data, 0, 24)))
                for i in range(0, aflen, 2):
                    mult = self.take(data, i*8+24, 1)
                    freq = self.take(data, i*8+25, 15)
                    print("\tfreq = {0} kHz".format(freq + mult*9*freq))
            
            if sysId == 1:
                print("AM service with AMSS, Id = {0:06X}".format(self.take(data, 0, 24)))
                for i in range(0, aflen-3, 2):
                    print("\tfreq = {0} kHz".format(self.take(data, i*16+24, 16)))
            
            if sysId==2:
                print("AM service without AMSS\n")
                for i in range(0, aflen, 2):
                    print("\tfreq = {0} kHz", self.take(data, i*16, 16))
            
            if sysId==4:
                print("FM-RDS service, 16-bit PI = {0:04X}".format(self.take(data, 0, 16)))
                for i in range(0, aflen-1, 2):
                    print("\tfreq = {0:0.01f} MHz".format(87.5 + .1 * self.take(data, i*8+16, 8)) )
            
            if sysId==9:
                print("DAB service, ECC + audio service Id = {0:06X}".format(self.take(data, 0, 24)))

            
        if type == 12:
            lang = self.takestr(data, 16, 3)
            cc = self.takestr(data, 40, 2)
            print("Language code: {0}".format(lang))
            print("Country code: {0}".format(cc))

        print("============================================================")
        return 16+8*len

                
    def process_stream(self, wordStream):
        for type, word in wordStream:
            self.process_block(type, word)
            
        if self.num_segments != -1 and not self.processed and self.segments_ok[0]:
                # if partially received, but segment 0 OK, try to decode anyway
                self.process_sdc_group(self.current_data)
            
    def __init__(self):
        self.current_vflag = -1
        self.current_data = -1
        self.num_segments = -1
        self.segments_ok = -1
        self.processed = False
        

#s = Station()

#print s.take(numpy.array([1, 1, 0, 1, 0, 1, 0, 0]), 1, 5)