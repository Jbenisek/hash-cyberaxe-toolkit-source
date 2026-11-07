#!/usr/bin/env python3
"""Export the raw carry-automaton tables of impl/outer.py (fq on Q=Y9, fe on E=omega; all 7 outcome bits, no S mask)
to tables.h for rates.cu, and print exact uniform-input per-outcome probabilities (pattern counts) for reference.
Also checks solver.mask_X(Q) == look(raw fq, Q) on random Q (the pre-check's X is the fq automaton)."""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
IMPL = os.path.join(HERE, "..", "..", "impl")
sys.path.insert(0, IMPL)
import outer, solver

raw, t1, t2 = outer.build_tables()
fq, fq_base = outer.flatten(raw[0])
fe, fe_base = outer.flatten(raw[1])
assert fq_base == 0 and fe_base == 0
with open(os.path.join(HERE, "tables.h"), "w") as f:
    for nm, arr in (("FQ", fq), ("FE", fe)):
        assert max(arr) < 2 ** 32
        f.write("static const unsigned int %s_H[%d] = {\n" % (nm, len(arr)))
        for i in range(0, len(arr), 16):
            f.write(",".join("%du" % x for x in arr[i:i + 16]) + ",\n")
        f.write("};\n")
    f.write("#define FQ_N %d\n#define FE_N %d\n" % (len(fq), len(fe)))
    f.write("#define Y3_C 0x%08xu\n#define DY3_C 0x%08xu\n" % (outer.Y3, outer.DY3))
    f.write("#define K2A_C 0x%08xu\n#define K2B_C 0x%08xu\n#define K2C_C 0x%08xu\n#define K2D_C 0x%08xu\n"
            % (outer.K2A, outer.K2B, outer.K2C, outer.K2D))
    f.write("#define CTR_FLAGS_C %du\n" % outer.CTR_FLAGS)

def bitprob(tables):
    pc = outer.pattern_counts(tables)
    out = []
    for j in range(7):
        out.append(sum(c for p, c in pc.items() if p >> j & 1) / 2 ** 32)
    anyS = sum(c for p, c in pc.items() if p & outer.S_MASK) / 2 ** 32
    return out, anyS

pq, pqS = bitprob(raw[0])
pe, peS = bitprob(raw[1])
rnd = random.Random(5)
agree = 0
for _ in range(3000):
    Q = rnd.getrandbits(32)
    agree += solver.mask_X(Q) == outer.look(raw[0], Q)
res = {"fq_len": len(fq), "fe_len": len(fe), "Y3": "%08x" % outer.Y3, "DY3": "%08x" % outer.DY3,
       "CTR_FLAGS": outer.CTR_FLAGS,
       "uniform_fq_bit_prob": pq, "uniform_fq_mean7": sum(pq) / 7, "uniform_fq_anyS": pqS,
       "uniform_fe_bit_prob": pe, "uniform_fe_mean7": sum(pe) / 7, "uniform_fe_anyS": peS,
       "E_COUNT/2^32": outer.E_COUNT / 2 ** 32, "SHARE/2^64": outer.SHARE / 2 ** 64,
       "maskX_eq_fq_raw": "%d of 3000" % agree}
print(json.dumps(res, indent=1))
with open(os.path.join(HERE, "exact_uniform.json"), "w") as f:
    json.dump(res, f, indent=1)
