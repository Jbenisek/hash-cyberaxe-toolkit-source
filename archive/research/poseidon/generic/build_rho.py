import os
H = os.path.dirname(os.path.abspath(__file__))
c = open(os.path.join(H, '..', 'impl', 'constants_own.py')).read()
c = c[:c.index('MDS_INV')].rstrip() + "\n"
c = c.split('\n', 1)[1]  # drop the docstring line
hdr = '''"""Generic collision search on the complete Orchard hash (56 partial rounds): one trail of x -> digest(x, 0), distinguished points, one table.

Target: poseidon-orchard-r56-prefix-v1 (initial state [x, 0, 2^65], 8 full + 56 partial rounds, digest = state[0], no feed-forward).
Sections: 1 deployed constants (halo2_poseidon 0.2.0, copied from our own checked file), 2 the hash, 3 the search (`search`),
4 parameters and ledger (`plan`, `python3 rho.py --plan`), 5 organizer experiments at reduced width and command line.
No outside code or library is used; standard library only.
"""
import sys
import json
import hashlib
from math import log, log2, exp, sqrt, ceil

# ================================================================ 1 constants
'''
core = open(os.path.join(H, 'core_rho.py')).read()
d = os.path.join(H, 'pkg', 'experiments')
os.makedirs(d, exist_ok=True)
open(os.path.join(d, 'rho.py'), 'w', newline='\n').write(hdr + c + "\n" + core)
