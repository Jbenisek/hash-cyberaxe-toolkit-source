#!/usr/bin/env python3
'debug_names.py: which names differ between h12.ctr_outer (prereg7 generator) and pkgBA16 scalar_outer on one step.'
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solver_measure as SM
SM.setup()
h12, BA = SM.h12, SM.BA
print('h12 class', hex(h12.CLASS_MASK), hex(h12.CLASS_VALUE), len(h12.CLASS_FREE), h12.CLASS_FREE)
print('BA  class', hex(BA.CLASS_MASK), hex(BA.CLASS_VALUE), len(BA.CLASS_FREE), BA.CLASS_FREE)
e = SM.RP.eight_words(SM.SEEDS[0], 12345)
o = h12.ctr_outer(e)
vv = BA.scalar_outer(e[:7] + [BA.member_word(e[7] % BA.CLASS_SIZE)])
print('Y4', hex(o['Y4']), hex(vv['Y4']), 'e1', hex((h12.Y3 + o['Y4']) & SM.M), hex(vv['e1']))
common = sorted(set(o) & set(vv))
print('common names', len(common), 'differ:', [n for n in common if o[n] != vv[n]])
print('only h12:', sorted(set(o) - set(vv)))
print('only BA :', sorted(set(vv) - set(o)))
print('h12 consts', [hex(getattr(h12, n)) for n in ('Y3', 'ETA') if hasattr(h12, n)])
print('BA consts', hex(BA.Y3), hex(BA.ETA))
