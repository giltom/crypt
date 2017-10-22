import struct

cdef int SIZE_NGRAM = struct.calcsize('>7p')
cdef int SIZE_CHAR = struct.calcsize('>BI')

def load_file(char* s):
    cdef bytes chunk
    cdef bytes ctrl
    cdef bytes curr
    cdef int count
    cdef char c
    f = open(s, 'rb')
    ngrams = {}
    while True:
        ctrl = f.read(1)
        if len(ctrl) == 0:
            break
        if ctrl[0]:     #new ngram
            chunk = f.read(SIZE_NGRAM)
            curr = struct.unpack('>7p', chunk)[0]
            ngrams[curr] = {}
        else:   #new char in current ngram
            chunk = f.read(SIZE_CHAR)
            c, count = struct.unpack('>BI', chunk)
            ngrams[curr][c] = count
    f.close()
    return ngrams
