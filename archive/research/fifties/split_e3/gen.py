'''Generate solve.cu (GPU exhaustive solve of the single cyclic 32-bit equation of the E3-fixed design over all 2^32 g)
and an instance file: E3 = (Y4, Y9, w8) taken from real points; B = 6 fresh random words per instance.
usage: python gen.py <n_E3> <n_B_per_E3> <seed>'''
import sys, random, json
sys.dont_write_bytecode = True
from ev import Design, DESIGN, real_point, y14_of, M
d = Design(*DESIGN)
lines, chk, ops = d.cuda()
NP = len(d.params)
cu = r'''#include <cstdio>
#include <cstdint>
#include <cstdlib>
#define ROL(x,n) __funnelshift_l((x),(x),(n))
__constant__ uint32_t P[%d];
__global__ void sweep(uint32_t hi, uint32_t *out, unsigned int *cnt) {
  uint32_t g = (hi << 24) | (blockIdx.x * blockDim.x + threadIdx.x);
  %s
  if (%s == 0u) { unsigned int k = atomicAdd(cnt, 1u); if (k < 64) out[k] = g; }
}
int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "r"); FILE *o = fopen(argv[2], "w");
  uint32_t h[%d]; uint32_t *dout; unsigned int *dcnt; cudaMalloc(&dout, 64 * 4); cudaMalloc(&dcnt, 4);
  int id;
  while (fscanf(f, "%%d", &id) == 1) {
    for (int i = 0; i < %d; i++) fscanf(f, "%%x", &h[i]);
    cudaMemcpyToSymbol(P, h, sizeof(h)); cudaMemset(dcnt, 0, 4);
    for (uint32_t hi = 0; hi < 256; hi++) sweep<<<65536, 256>>>(hi, dout, dcnt);
    unsigned int c; uint32_t r[64]; cudaMemcpy(&c, dcnt, 4, cudaMemcpyDeviceToHost);
    cudaMemcpy(r, dout, 64 * 4, cudaMemcpyDeviceToHost);
    fprintf(o, "%%d %%u", id, c); for (unsigned int i = 0; i < c && i < 64; i++) fprintf(o, " %%08x", r[i]); fprintf(o, "\n"); fflush(o);
  }
  fclose(o); return 0;
}
''' % (NP, '\n  '.join(lines), chk, NP, NP)
open('solve.cu', 'w', newline='\n').write(cu)
nE, nB, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rnd = random.Random(seed); inst = []
with open('inst_%d.txt' % seed, 'w', newline='\n') as f:
    for e in range(nE):
        v = real_point(rnd)
        E3 = {w: v[w] for w in d.F}; y14 = y14_of(v)
        for b in range(nB + 1):
            if b == 0:
                B = {w: v[w] for w in d.B}          # the generating point: its g must be a root
            else:
                B = {w: rnd.getrandbits(32) for w in d.B}
            start = dict(E3, **B)
            pv = d.pre_values(start)
            pid = len(inst)
            inst.append({'id': pid, 'e3': e, 'gen': b == 0, 'E3': E3, 'Y14': y14, 'B': B,
                         'g_true': v[d.g] if b == 0 else None})
            f.write('%d %s\n' % (pid, ' '.join('%08x' % pv[p] for p in d.params)))
json.dump(inst, open('inst_%d.json' % seed, 'w'))
print('params', d.params, 'loop ops', ops, 'instances', len(inst))
