# pic18fdasm.py -- Disassembler in Python.

import sys
import pprint
from ctypes import c_ubyte, c_ushort, c_uint, c_ulong
from intelhex import IntelHex


usage = """PIC 18F2455 Disassembler
Usage:
    python pic18fdasm.py INTEL_HEX_FILE ADDR_START ADDR_END

Descriptions:
    Reads in an Intel-formatted hexdump from a PIC 18Fxxxx-family
    microcontroller, and prints assembly code to stdout.
"""


def bin2str(v):
    return format(v, '016b')


isa = {
    'ADDWF':  ['001001',  'd', 'a', 'ffffffff'],
    'ADDWFC': ['001000',  'd', 'a', 'ffffffff'],
    'ANDWF':  ['000101',  'd', 'a', 'ffffffff'],
    'CLRF':   ['0110101', 'a', 'ffffffff'],
    'COMF':   ['000111',  'd', 'a', 'ffffffff'],
    'CPFSEQ': ['0110001', 'a', 'ffffffff'],
    'CPFSGT': ['0110010', 'a', 'ffffffff'],
    'CPFSLT': ['0110000', 'a', 'ffffffff'],
    'DECF':   ['000001',  'd', 'a', 'ffffffff'],
    'DECFSZ': ['001011',  'd', 'a', 'ffffffff'],
    'DCFSNZ': ['010011',  'd', 'a', 'ffffffff'],
    'INCF':   ['001010',  'd', 'a', 'ffffffff'],
    'INCFSZ': ['001111',  'd', 'a', 'ffffffff'],
    'INFSNZ': ['010010',  'd', 'a', 'ffffffff'],
    'IORWF':  ['000100',  'd', 'a', 'ffffffff'],
    'MOVF':   ['010100',  'd', 'a', 'ffffffff'],
    'MOVFF':  ['1100',    'ffffffffffff'], #'1111',
    'MOVWF':  ['0110111', 'a', 'ffffffff'],
    'MULWF':  ['0000001', 'a', 'ffffffff'],
    'NEGF':   ['0110110', 'a', 'ffffffff'],
    'RLCF':   ['001101',  'd', 'a', 'ffffffff'],
    'RLNCF':  ['010001',  'd', 'a', 'ffffffff'],
    'RRCF':   ['001100',  'd', 'a', 'ffffffff'],
    'RRNCF':  ['010000',  'd', 'a', 'ffffffff'],
    'SETF':   ['0110100', 'a', 'ffffffff'],
    'SUBFWB': ['010101',  'd', 'a', 'ffffffff'],
    'SUBWF':  ['010111',  'd', 'a', 'ffffffff'],
    'SUBWFB': ['010110',  'd', 'a', 'ffffffff'],
    'SWAPF':  ['001110',  'd', 'a', 'ffffffff'],
    'TSTFSZ': ['0110011', 'a', 'ffffffff'],
    'XORWF':  ['000110',   'd', 'a', 'ffffffff'],
}


def prefix_match(prefixes, bits):
    possible_matches = []
    for instr in prefixes.keys():
        prefix = prefixes[instr][0]
        prefix_len = len(prefix)
        args = {}
        # Decode instr fields.
        idx = prefix_len
        for arg in prefixes[instr][1:]:
            # 1st char of field becomes key.
            # Value of field
            args[arg[0]] = int(bits[idx:idx+len(arg)], 2)
            idx += len(arg)
        # Determine if we actually have a match.
        candidate = False
        for i in range(0, len(prefix)):
            if prefix[i] == bits[i]:
                candidate = True
            else:
                candidate = False
                break
        if candidate:
            possible_matches.append((instr, prefix_len, args))
    # Matches sorted by greatest length.
    possible_matches = sorted(possible_matches, key=(lambda x: x[1]), reverse=True)
    if len(possible_matches) > 0:
        return [possible_matches[0][0], possible_matches[0][2]] # Longest match, instr.
    else:
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print usage
        exit(1)
    else:
        ih = IntelHex(sys.argv[1])
        mem_layout = ih.todict()
        instrs = []
        for i in range(0, 2200, 2):
            value = c_uint()
            value = (ih[i] << 8) | ih[i+1]
            instrs.append(value)
            #print "%6d %3d %3d" % (value, ih[i], ih[i+1])
        for instr in instrs:
            print prefix_match(isa, bin2str(instr))
        #pprint.pprint(instrs)
