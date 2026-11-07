#!/usr/bin/env python3
"""gen_pass.py (fifties/solverwork): copy the validated prereg7 kernel v7gpu.cu unchanged and ADD one filter mode.
Mode 'p': for every proposal i of every stream (same Philox words, same outer(), same automata, same v formula as the
prereg7 hist/dump kernels), T = (HQM & HEM) & S(0x5f) & VMASK[v]; write 'stream index T|v<<16' for T != 0.
The GPU is only a filter: solver_measure.py recomputes every kept proposal from its Philox words with the unchanged
Python reference (run_prereg.eight_words + ref_fields) and asserts the same T."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'pkg19', 'as_subset', 'prereg7', 'v7gpu.cu')
src = open(SRC).read()

KERNEL = r'''
__device__ const unsigned short VMASK_D[8] = {0, 0, 0x3F80, 0x3FFF, 0x3FFF, 0x3F80, 0, 0};
__global__ void pass_kernel(uint32_t k0, uint32_t k1, uint64_t base, uint64_t count,
                            unsigned long long *out, unsigned int *nout, unsigned int cap) {
    uint64_t stride = (uint64_t)gridDim.x * blockDim.x;
    for (uint64_t t = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x; t < count; t += stride) {
        uint32_t e[8], qi, ei, v, vb; Res o;
        step(base + t, k0, k1, e, o, qi, ei, v, vb);
        uint32_t T = (uint32_t)HQM[qi] & (uint32_t)HEM[ei] & 0x5fu & (uint32_t)VMASK_D[v];
        if (T) {
            unsigned int j = atomicAdd(nout, 1u);
            if (j < cap) { out[2 * j] = base + t; out[2 * j + 1] = (unsigned long long)(T | (v << 16) | (vb << 20)); }
        }
    }
}

'''
MODE = r'''
    if (mode[0] == 'p') {
        FILE *f = fopen(argv[12], "w");
        if (!f) { fprintf(stderr, "open\n"); return 1; }
        unsigned int cap = (unsigned int)strtoul(argv[13], 0, 10);
        unsigned long long *d_out; unsigned int *d_n;
        CK(cudaMalloc(&d_out, (size_t)cap * 16)); CK(cudaMalloc(&d_n, 4));
        std::vector<unsigned long long> hout((size_t)cap * 2);
        for (int k = 0; k < 8; k++) {
            CK(cudaMemset(d_n, 0, 4));
            for (uint64_t base = 0; base < per; base += chunk) {
                uint64_t cnt = per - base < chunk ? per - base : chunk;
                pass_kernel<<<GRID, BLOCK>>>((uint32_t)seed[k], (uint32_t)(seed[k] >> 32), base, cnt, d_out, d_n, cap);
                CK(cudaGetLastError());
            }
            CK(cudaDeviceSynchronize());
            unsigned int n; CK(cudaMemcpy(&n, d_n, 4, cudaMemcpyDeviceToHost));
            unsigned int m = n < cap ? n : cap;
            CK(cudaMemcpy(hout.data(), d_out, (size_t)m * 16, cudaMemcpyDeviceToHost));
            fprintf(f, "# stream %d steps %llu found %u kept %u\n", k, (unsigned long long)per, n, m);
            for (unsigned int j = 0; j < m; j++) fprintf(f, "%d %llu %llu\n", k, hout[2 * j], hout[2 * j + 1]);
        }
        fclose(f);
        return 0;
    }
'''
anchor_k = '#define CK(x)'
anchor_m = 'const int BLOCK = 256, GRID = 82 * 8;\n'
assert src.count(anchor_k) == 1 and src.count(anchor_m) == 1
src = src.replace(anchor_k, KERNEL + anchor_k)
src = src.replace(anchor_m, anchor_m + MODE)
open(os.path.join(HERE, 'passgpu.cu'), 'w').write(src)
# Walk R: the same kernel with the root-instance flags of the front-line package (pkgBA16 step CO: FLAGS = 11).
# prereg7's generator is pkg12b ctr_outer with CTR_FLAGS = 3; that constant enters only K3.d1.
f3 = '#define c_CTR_FLAGS 0x00000003u'
assert src.count(f3) == 1
open(os.path.join(HERE, 'passgpu11.cu'), 'w').write(src.replace(f3, '#define c_CTR_FLAGS 0x0000000bu'))
print('passgpu.cu and passgpu11.cu written')
