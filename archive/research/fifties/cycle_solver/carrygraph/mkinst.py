'''Instance files for cg.c.
  python mkinst.py real <count> <out>     first <count> real instances of split_e3/inst_2.txt (32-bit, generator output)
  python mkinst.py rand <n> <count> <seed> <out>   random 14-word params masked to n bits (keeps the complement/+1
                                                   structure of the subtractions), for the scaled cycle'''

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

import sys, random
sys.dont_write_bytecode = True
import cyc
from sched import consts32
SRC = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/inst_2.txt')
if sys.argv[1] == 'real':
    cnt, out = int(sys.argv[2]), sys.argv[3]
    with open(SRC) as fi, open(out, 'w', newline='\n') as fo:
        for line in fi:
            p = line.split()
            if not p: continue
            if int(p[0]) >= cnt: break
            P = [int(x, 16) for x in p[1:]]
            fo.write(p[0] + ' ' + ' '.join('%x' % c for c in consts32(P)) + '\n')
else:
    n, cnt, seed, out = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    rnd = random.Random(seed); m = (1 << n) - 1
    with open(out, 'w', newline='\n') as fo:
        for i in range(cnt):
            P = [rnd.getrandbits(32) for _ in range(14)]
            fo.write('%d ' % i + ' '.join('%x' % (c & m) for c in consts32(P)) + '\n')
