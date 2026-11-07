'''State-size bounds for exact bit-serial (carry-graph) solvers of the best cycle (21 equations), for two natural
processing orders.  For each modular addition that reads a loop word: number of loop-word operands and carry bits
per bit position (2 operands -> 1 bit, 3 or 4 operands -> 2 bits).  The check's offset set comes from offsets.py.
  position order (Sol D4 7.2 carry graph): a check bit at position i reads g at i - o for every offset o, so the
    state must hold the g bits of the covering arc (width w) plus one carry state per addition;
  slice order (positions mod 4, possible because every offset is a multiple of 4): the state must hold the
    carries that cross from in-nibble position 3 to position 0, at every nibble boundary of every addition.
usage: python sepbound.py  (writes sepbound_out.txt)'''

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev, offsets
out = open('sepbound_out.txt', 'w')
def p(*a):
    print(*a); print(*a, file=out)
for gw in ('C0.b1', 'C1.a1'):
    d = ev.Design(ev.DESIGN[0], ev.DESIGN[1], gw)
    O, cs, adds, mixes, addmix, info = offsets.analyse(d)
    rows = [(i, w) for i, w in d.loop if ev.REL[i][0] == 'add'] + [(d.chk, 'CHECK')]
    cbits = 0; desc = []
    for i, w in rows:
        r = ev.REL[i]; ops = [x for x in r[1] if x != w]
        gd = [x for x in ops if x in O or x == d.g]
        nop = len(ops) if w != 'CHECK' else len(r[1])
        if not gd and w != 'CHECK': continue
        cb = 1 if nop <= 2 else 2
        cbits += cb; desc.append('%s(%d ops, %d loop)' % (w, nop, len(gd) if w != 'CHECK' else sum(x in O for x in r[1])))
    w = offsets.arcw(cs)
    p('cut %s: check offsets %s (arc width %d); additions reading loop words: %d, carry bits per position %d' % (gw, cs, w, len(desc), cbits))
    p('   ', ', '.join(desc))
    p('   position order: state >= 2^(%d + %d) = 2^%d per position' % (w, cbits, w + cbits))
    p('   slice order: carries crossing the 8 nibble boundaries >= %d bits (7 boundaries x %d)' % (7 * cbits, cbits))
