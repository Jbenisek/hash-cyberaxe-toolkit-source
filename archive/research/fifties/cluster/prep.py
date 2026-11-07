#!/usr/bin/env python3
"""Prep + codegen for the cluster exception measurement.
Reconstructs automaton (2) at bit level, computes the exact alive-share table
and the 512-entry alive9 lookup (S-restricted), validates against outer.look,
and emits cluster.cu (RNG + step-CO omega codegen + measurement kernel)."""
import os, sys, json
from fractions import Fraction
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.normpath(os.path.join(HERE, "..", "..", "impl"))
sys.path.insert(0, IMPL)
import outer  # the executable reference

MASK = 0xFFFFFFFF
S_INDICES = [j for j in range(7) if (outer.S_MASK >> j) & 1]  # outcomes kept by S


def ctr_automaton_bits(targets, dy, n=32):
    """Exact copy of outer.ctr_automaton's per-bit construction, exposing the
    per-bit transitions and the state tuples of each layer."""
    layer = [(0, (1,) * len(targets))]
    layers = [layer]
    trans = []
    for i in range(n):
        ids, rows, e = {}, [], dy >> i & 1
        for k, sets in layer:
            row = []
            for a in (0, 1):
                b, new = a ^ e ^ k, []
                for m, (dz, out) in zip(sets, targets):
                    d, r = dz >> i & 1, 0
                    for c in range(4):
                        if m >> c & 1 and (c >> 1) ^ (c & 1) == (out >> i & 1) ^ a ^ b ^ d:
                            for v in (0, 1):
                                r |= 1 << ((a + v + (c >> 1)) >> 1) * 2 + ((b + (v ^ d) + (c & 1)) >> 1)
                    new.append(r)
                state = ((a + e + k) >> 1, tuple(new)) if any(new) else (0, (0,) * len(new))
                row.append(ids.setdefault(state, len(ids)))
            rows.append(row)
        trans.append(rows)
        layer = list(ids)
        layers.append(layer)
    return trans, layers


def alive_S(state_tuple):
    """A layer state is alive w.r.t. S iff some S-outcome is still achievable."""
    sets = state_tuple[1]
    return any(sets[t] for t in S_INDICES)


def main():
    # automaton (2): targets (ror(ctr_g(tau),12), EPS), dy = DY3  (outer.build_tables)
    th = [outer.ctr_g(t) for t in outer.TAUS]
    targets2 = [(outer.ror(x, 12), outer.EPS) for x in th]
    trans, layers = ctr_automaton_bits(targets2, outer.DY3, 32)

    # exact alive-share table (fraction of 32-bit words not yet S-dead after b bits)
    counts = {0: 1}
    shares = []
    for i in range(32):
        nxt = defaultdict(int)
        for idx, cnt in counts.items():
            for a in (0, 1):
                nxt[trans[i][idx][a]] += cnt
        counts = dict(nxt)
        alive = sum(c for idx, c in counts.items() if alive_S(layers[i + 1][idx]))
        shares.append((i + 1, alive, Fraction(alive, 1 << (i + 1))))

    share9 = shares[8][2]      # after low 9 bits (bits 0..8)
    share14 = shares[13][2]    # after low 14 bits
    assert shares[31][1] == outer.E_COUNT, (shares[31][1], outer.E_COUNT)

    # alive9[v] for v in 0..511 : S-alive after reading the 9 low bits of v
    alive9 = [0] * 512
    for v in range(512):
        idx = 0
        for i in range(9):
            idx = trans[i][idx][(v >> i) & 1]
        alive9[v] = 1 if alive_S(layers[9][idx]) else 0
    n_alive9 = sum(alive9)

    # flattened T2 table (final AND S) and base, for look() on the GPU
    S = outer.Search()
    fe, fe_base = outer.flatten(S.t2)
    assert fe_base == 0 and fe == S.fe

    # validate alive9 against the authoritative look(): dead prefix => look==0 for all words
    import random
    rnd = random.Random(12345)
    bad = 0
    for _ in range(300000):
        x = rnd.getrandbits(32)
        m = outer.look(S.t2, x)
        if alive9[x & 0x1FF] == 0 and m != 0:
            bad += 1
    assert bad == 0, bad
    # and share9 should equal (count of 32-bit words whose low9 is alive)/2^32 restricted form
    assert Fraction(n_alive9, 512) == share9, (n_alive9, share9)

    # ---------- codegen the step-CO omega computation ----------
    slice_lines = outer.slice_lines(("w8",))
    memberset = {"Y4"}
    for name, e in slice_lines:
        d = set(); outer.deps(e, d)
        if d & memberset:
            memberset.add(name)
    ctx_words = {"C0.d1": "C0_d1", "D2.a1": "D2_a1", "D2.b1": "D2_b1",
                 "S11": "S11", "S4": "S4", "X9": "X9", "w6": "w6"}
    linenames = {name for name, _ in slice_lines}

    def san(nm):
        if nm == "Y4":
            return "y"
        if nm in ctx_words:
            return ctx_words[nm]
        assert nm in linenames, nm
        return nm.replace(".", "_")

    def emit(e):
        if isinstance(e, int):
            return "0x%08xu" % (e & MASK)
        if isinstance(e, str):
            return san(e)
        k = e[0]
        if k == "sum":
            parts = ["0u"]
            for t in e[1]:
                if isinstance(t, tuple) and t[0] == "neg":
                    parts.append("- (%s)" % emit(t[1]))
                else:
                    parts.append("+ (%s)" % emit(t))
            return "(" + " ".join(parts) + ")"
        if k == "xor":
            return "((%s) ^ (%s))" % (emit(e[1]), emit(e[2]))
        if k == "ror":
            r = e[2]
            assert 1 <= r <= 31, r
            return "ror32((%s), %d)" % (emit(e[1]), r)
        raise ValueError(k)

    ctx_code, mem_code = [], []
    for name, e in slice_lines:
        line = "uint32_t %s = %s;" % (san(name), emit(e))
        (mem_code if name in memberset else ctx_code).append(line)

    FE_STR = ",".join(str(int(x)) for x in fe)
    AL_STR = ",".join(str(int(x)) for x in alive9)
    Y3 = outer.Y3
    CLASS_VALUE = outer.CLASS_VALUE
    FREE_MASK = outer.FREE_MASK

    cu = CU_TEMPLATE.format(
        FE_LEN=len(fe), FE=FE_STR, ALIVE9=AL_STR,
        Y3=Y3, CLASS_VALUE=CLASS_VALUE, FREE_MASK=FREE_MASK, FE_BASE=fe_base,
        CTX_LINES="\n        ".join(ctx_code),
        MEM_LINES="\n            ".join(mem_code))
    with open(os.path.join(HERE, "cluster.cu"), "w") as f:
        f.write(cu)

    info = {
        "Y3": "%08x" % Y3, "CLASS_VALUE": "%08x" % CLASS_VALUE,
        "FREE_MASK": "%08x" % FREE_MASK, "E_COUNT": outer.E_COUNT,
        "fe_len": len(fe), "fe_base": fe_base,
        "n_context_lines": len(ctx_code), "n_member_lines": len(mem_code),
        "member_lines": [san(n) for n, _ in slice_lines if n in memberset],
        "alive9_count": n_alive9, "alive9_of_512": n_alive9,
        "share_after_9bits": [share9.numerator, share9.denominator, float(share9)],
        "share_after_14bits": [share14.numerator, share14.denominator, float(share14)],
        "dead_share_9bits": float(1 - share9),
        "alive_share_table": [[b, a, [frac.numerator, frac.denominator], float(frac)]
                              for b, a, frac in shares],
        "validation_dead_implies_look0_fails": bad,
    }
    with open(os.path.join(HERE, "prep.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps({k: info[k] for k in
          ("Y3", "CLASS_VALUE", "FREE_MASK", "E_COUNT", "fe_len",
           "n_context_lines", "n_member_lines", "member_lines",
           "alive9_count", "share_after_9bits", "share_after_14bits",
           "dead_share_9bits", "validation_dead_implies_look0_fails")}, indent=1))
    print("alive share b=1..32:",
          [round(float(f), 4) for _, _, f in shares])


CU_TEMPLATE = r"""// cluster.cu  -- generated by prep.py.  Measures the e1-bits-10..14 cluster
// omega-prefix exception rate and the DEAD-representative claim for automaton (2).
#include <cstdio>
#include <cstdint>
#include <cstdlib>

#define Y3c 0x{Y3:08x}u
#define CLASS_VALUE 0x{CLASS_VALUE:08x}u
#define FREE_MASK 0x{FREE_MASK:08x}u
#define FE_BASE {FE_BASE}
#define FE_LEN {FE_LEN}

__device__ __forceinline__ uint32_t ror32(uint32_t x, int n) {{
    return (x >> n) | (x << (32 - n));
}}

__constant__ int d_fe[FE_LEN];
__constant__ unsigned char d_alive9[512];

__device__ __forceinline__ uint32_t mask2_of(uint32_t om) {{
    int s = d_fe[FE_BASE + (om & 0xff)];
    s = d_fe[s + ((om >> 8) & 0xff)];
    s = d_fe[s + ((om >> 16) & 0xff)];
    return (uint32_t)d_fe[s + ((om >> 24) & 0xff)];
}}

__device__ __forceinline__ uint64_t splitmix64(uint64_t *x) {{
    uint64_t z = (*x += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}}

// counters: [0]=partner_pairs [1]=exceptions [2]=dead_clusters
//           [3]=dead_partner_pass2 [4]=dead_partner_pass2_nonexc [5]=clusters
__global__ void kern(uint64_t seed, uint64_t total_clusters, unsigned long long *g) {{
    uint64_t stride = (uint64_t)gridDim.x * blockDim.x;
    unsigned long long l_pairs = 0, l_exc = 0, l_dead = 0, l_dp = 0, l_dpn = 0, l_cl = 0;
    for (uint64_t c = (uint64_t)blockIdx.x * blockDim.x + threadIdx.x;
         c < total_clusters; c += stride) {{
        uint64_t st = (uint64_t)seed * 0x9E3779B97F4A7C15ULL
                      ^ (c * 0xD1B54A32D192ED03ULL + 0x632BE59BD9B4E019ULL);
        uint32_t w[8];
        for (int kk = 0; kk < 4; ++kk) {{
            uint64_t r = splitmix64(&st);
            w[2 * kk] = (uint32_t)(r & 0xffffffffULL);
            w[2 * kk + 1] = (uint32_t)(r >> 32);
        }}
        uint32_t ctx0 = w[0], ctx1 = w[1], ctx2 = w[2], ctx3 = w[3],
                 ctx4 = w[4], ctx5 = w[5], ctx6 = w[6], W = w[7];
        uint32_t C0_d1 = ctx0, D2_a1 = ctx1, D2_b1 = ctx2, S11 = ctx3,
                 S4 = ctx4, X9 = ctx5, w6 = ctx6;
        uint32_t base_e1 = CLASS_VALUE | (W & FREE_MASK);
        uint32_t rep_e1 = base_e1 & ~(0x1Fu << 10);   // cluster bits 10..14 cleared

        // context-only lines (once)
        {CTX_LINES}

        uint32_t om_rep = 0, rep_low9 = 0; int rep_dead = 0;
        for (int p = 0; p < 32; ++p) {{
            uint32_t e1p = rep_e1 | ((uint32_t)p << 10);
            uint32_t y = e1p - Y3c;
            {MEM_LINES}
            uint32_t omega = e1p + w8;
            if (p == 0) {{
                om_rep = omega;
                rep_low9 = omega & 0x1ffu;
                rep_dead = (d_alive9[rep_low9] == 0);
                l_cl += 1;
                if (rep_dead) l_dead += 1;
            }} else {{
                l_pairs += 1;
                int is_exc = ((omega & 0x1ffu) != rep_low9);
                if (is_exc) l_exc += 1;
                if (rep_dead) {{
                    uint32_t m2 = mask2_of(omega);
                    if (m2 != 0) {{
                        l_dp += 1;
                        if (!is_exc) l_dpn += 1;
                    }}
                }}
            }}
        }}
    }}
    atomicAdd(&g[0], l_pairs);
    atomicAdd(&g[1], l_exc);
    atomicAdd(&g[2], l_dead);
    atomicAdd(&g[3], l_dp);
    atomicAdd(&g[4], l_dpn);
    atomicAdd(&g[5], l_cl);
}}

static const int h_fe[FE_LEN] = {{{FE}}};
static const unsigned char h_alive9[512] = {{{ALIVE9}}};

int main(int argc, char **argv) {{
    uint64_t seed = argc > 1 ? strtoull(argv[1], 0, 0) : 1;
    uint64_t total = argc > 2 ? strtoull(argv[2], 0, 0) : (1ULL << 26);
    int blocks = argc > 3 ? atoi(argv[3]) : 4096;
    int tpb = argc > 4 ? atoi(argv[4]) : 256;

    cudaMemcpyToSymbol(d_fe, h_fe, sizeof(h_fe));
    cudaMemcpyToSymbol(d_alive9, h_alive9, sizeof(h_alive9));
    unsigned long long *g; cudaMallocManaged(&g, 6 * sizeof(unsigned long long));
    for (int i = 0; i < 6; ++i) g[i] = 0;

    kern<<<blocks, tpb>>>(seed, total, g);
    cudaError_t err = cudaDeviceSynchronize();
    if (err != cudaSuccess) {{ printf("CUDA error: %s\n", cudaGetErrorString(err)); return 1; }}

    printf("{{\"seed\": %llu, \"clusters\": %llu, \"partner_pairs\": %llu, "
           "\"exceptions\": %llu, \"dead_clusters\": %llu, "
           "\"dead_partner_pass2\": %llu, \"dead_partner_pass2_nonexc\": %llu}}\n",
           (unsigned long long)seed, g[5], g[0], g[1], g[2], g[3], g[4]);
    cudaFree(g);
    return 0;
}}
"""


if __name__ == "__main__":
    main()
