#!/usr/bin/python

import numpy

class Code:
    def __init__(self, poly, word_size, offset_words):
        self.word_size = word_size
        self.poly = numpy.array(poly, dtype=int)
        self.offset_words = offset_words
        
        # calculate the P matrix by polynomial division
        # each row is: e(i)*x^10 mod rds_poly
        # where e(i) is the i-th base vector in the canonical orthogonal base
        self.check_size = self.poly.size - 1
        self.matP = numpy.empty([0, self.check_size], dtype=int)
        for i in range(word_size):
            (q, r) = numpy.polydiv(numpy.identity(self.word_size+self.check_size, dtype=int)[i], self.poly)
            #print q, r
            # r may be "left-trimmed" => add missing zeros
            if self.check_size - r.size > 0:
                #print r
                #print numpy.zeros(check_size - r.size)
                r = numpy.append(numpy.zeros(self.check_size - r.size, dtype=int), r)

            rr = numpy.mod(numpy.array([r], dtype=int), 2)
            self.matP = numpy.append(self.matP, rr, axis=0)
            
        self.matG = numpy.append(numpy.identity(self.word_size, dtype=int), self.matP, axis=1)
        self.matH = numpy.append(self.matP, numpy.identity(self.check_size, dtype=int), axis=0)
        
        #self.offset_words = numpy.array(offset_words, dtype=int)
        self.syndromes = {}
        for ow_name, ow in offset_words.items():
            # actually it's useless to call syndrome here, because of the way
            # our H is constructed. Do the block-wise matrix multiplication
            # to be convinced of this.
            self.syndromes[ow_name] = self.syndrome(numpy.append(numpy.zeros(self.word_size, dtype=int), numpy.array(ow, dtype=int)))
        
    
    def syndrome(self, v):
        return numpy.mod(numpy.dot(v, self.matH), 2)
        
        
    def bitstream_to_wordstream(self, bitstream):
        bits = numpy.array(bitstream, dtype=int)
        wordStream = []
        i = self.word_size+self.check_size
        while i <= bits.size:
            candidate = bits[i-self.word_size-self.check_size:i]
            for sname, synd in self.syndromes.items():
                if (synd == self.syndrome(candidate)).all():
                    wordStream.append((sname, candidate[0:self.word_size]))
                    i = i + self.word_size + self.check_size - 1
            i = i + 1
        return wordStream
    
    
    def wordstream_to_bitstream(self, wordstream):
        #total_size = self.word_size + self.check_size
        #bitstream = numpy.zeros(total_size * len(wordstream), dtype=int)
        def to_bin(x):
            res = []
            for i in range(self.word_size):
                res.insert(0, x % 2)
                x >>= 1
            return res
        
        offsets = numpy.array(map(lambda (ofs, wrd): numpy.array(self.offset_words[ofs]), wordstream))
        words = numpy.array(map(lambda (o, w): to_bin(w), wordstream))
        
        res = numpy.dot(numpy.array(words), self.matG) % 2
        res[:,self.word_size:] ^= offsets
        
        return res.flatten()
    
        
    def __repr__(self):
        return "Poly = " + repr(self.poly) + "\nWord size = " + repr(self.word_size) + "\nP = " + repr(self.matP) + "\nG = " + repr(self.matG) + "\nH = " + repr(self.matH) + "\nSyndromes = " + repr(self.syndromes)
        
    
    def __str__(self):
        return repr(self)


amss_code = Code([1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1], 36, {1: [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], 2:[1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1]})
rds_code = Code([1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1], 16, {'A': [0, 0, 1, 1, 1, 1, 1, 1, 0, 0], 'B': [0, 1, 1, 0, 0, 1, 1, 0, 0, 0], 'C': [0, 1, 0, 1, 1, 0, 1, 0, 0, 0], "C'": [1, 1, 0, 1, 0, 1, 0, 0, 0, 0], 'D': [0, 1, 1, 0, 1, 1, 0, 1, 0, 0]})



def main():
    #print amss_code
    print amss_code

if __name__ == "__main__":
    main()