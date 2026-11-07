'''Write the core word model (ksat.core of wmodel.build) for brute.c: "NW NR" then one relation per line.'''
import sys
from wmodel import build
from ksat import core
for counter in (1, 2):
    R0, W0 = build(counter); R = core(R0); W = sorted(set().union(*R)); ix = {w: i for i, w in enumerate(W)}
    with open('core_c%d.txt' % counter, 'w', newline='\n') as f:
        f.write('%d %d\n' % (len(W), len(R)))
        for r in R: f.write('%d %s\n' % (len(r), ' '.join(str(ix[w]) for w in sorted(r))))
    open('core_c%d_names.txt' % counter, 'w', newline='\n').write('\n'.join('%d %s' % (i, w) for i, w in enumerate(W)) + '\n')
    print('counter %d: core words %d relations %d DOF %d' % (counter, len(W), len(R), len(W) - len(R)))
