'''Generate cpu_scan.c: exhaustive CPU scan of the 21-equation cycle cut at a chosen loop word (default C1.a1), with
the front design's free words (so split_e3/inst_2.txt parameter lines feed it unchanged: same 14 parameters).
On every root it prints the root and the value of C0.b1 computed on the way, so the root set can be compared with
the GPU reference (split_e3/roots_2.txt, loop word C0.b1).
usage: python gen_cpu.py [loopword]'''

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
import ev
gw = sys.argv[1] if len(sys.argv) > 1 else 'C1.a1'
front = ev.Design(*ev.DESIGN)
d = ev.Design(ev.DESIGN[0], ev.DESIGN[1], gw)
assert d.params == front.params, (d.params, front.params)
lines, chk, ops = d.cuda()
c0b1 = 'v_C0_b1' if gw != 'C0.b1' else 'g'
src = r'''#include <stdio.h>
#include <stdint.h>
#define ROL(x,n) (((x) << (n)) | ((x) >> (32 - (n))))
static inline uint32_t loopc(uint32_t g, const uint32_t *P, uint32_t *c0b1) {
  %s
  *c0b1 = %s;
  return %s;
}
int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "r"); FILE *o = fopen(argv[2], "w");
  int lo = atoi(argv[3]), hi = atoi(argv[4]);
  uint32_t P[%d]; int id;
  while (fscanf(f, "%%d", &id) == 1) {
    for (int i = 0; i < %d; i++) fscanf(f, "%%x", &P[i]);
    if (id < lo || id >= hi) continue;
    unsigned n = 0; uint32_t r[64], rb[64];
    uint32_t g = 0;
    do { uint32_t cb; if (loopc(g, P, &cb) == 0u) { if (n < 64) { r[n] = g; rb[n] = cb; } n++; } } while (++g != 0u);
    fprintf(o, "%%d %%u", id, n);
    for (unsigned i = 0; i < n && i < 64; i++) fprintf(o, " %%08x:%%08x", r[i], rb[i]);
    fprintf(o, "\n"); fflush(o);
  }
  fclose(o); return 0;
}
''' % ('\n  '.join(lines), c0b1, chk, len(d.params), len(d.params))
src = src.replace('#include <stdint.h>', '#include <stdint.h>\n#include <stdlib.h>')
open('cpu_scan.c', 'w', newline='\n').write(src)
print('loop word', gw, 'loop eqs', len(d.loop), 'ops per candidate', ops, 'params', d.params)
