"""Own BLAKE3 engine for dig units U64-U72: scalar compress/tree (validated), generalized SWAR tracer (op counts), DCE.
Validation: py eng.py  (7-round known vectors, verifier cross-check at rounds 1..7, tracer vs scalar)."""

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

import sys, struct, random, re
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments'))
import rho
from rho import Tracer, IV, PERM, GCALLS, M32, REP, LANES, PITCH
MASK = M32
CS, CE, PAR, ROOT = 1, 2, 4, 8


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & MASK


def compress(cv, m, ctr, blen, flags, rounds, v8=IV[:4]):
    v = list(cv) + list(v8) + [ctr & MASK, ctr >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            v[a] = (v[a] + v[b] + x) & MASK; v[d] = ror(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & MASK;     v[b] = ror(v[b] ^ v[c], 12)
            v[a] = (v[a] + v[b] + y) & MASK; v[d] = ror(v[d] ^ v[a], 8)
            v[c] = (v[c] + v[d]) & MASK;     v[b] = ror(v[b] ^ v[c], 7)
        m = [m[i] for i in PERM]
    return [v[i] ^ v[i+8] for i in range(8)] + [v[i+8] ^ cv[i] for i in range(8)]


def words(block):
    return list(struct.unpack("<16I", block.ljust(64, b"\0")))


def b3(data, rounds=7):
    """Own BLAKE3 (standard chunk tree)."""
    chunks = [data[i:i+1024] for i in range(0, max(len(data), 1), 1024)] or [b""]

    def chunk_out(chunk, t):
        cv = list(IV)
        blocks = [chunk[i:i+64] for i in range(0, max(len(chunk), 1), 64)] or [b""]
        for k, blk in enumerate(blocks):
            fl = (CS if k == 0 else 0) | (CE if k == len(blocks)-1 else 0)
            if k == len(blocks)-1:
                return (cv, words(blk), t, len(blk), fl)
            cv = compress(cv, words(blk), t, 64, fl, rounds)[:8]
    outs = [chunk_out(c, t) for t, c in enumerate(chunks)]

    def build(lo, hi):
        if hi - lo == 1:
            return outs[lo]
        n = hi - lo; p = 1
        while p * 2 < n:
            p *= 2
        l = build(lo, lo+p); r = build(lo+p, hi)
        lcv = compress(*l, rounds)[:8]; rcv = compress(*r, rounds)[:8]
        return (list(IV), lcv + rcv, 0, 64, PAR)
    cv, w, t, bl, fl = build(0, len(chunks))
    out = compress(cv, w, 0 if fl & PAR else t, bl, fl | ROOT, rounds)
    return struct.pack("<8I", *out[:8])


def pat(n):
    return bytes(i % 251 for i in range(n))


def validate():
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
    from verifier.blake3 import blake3 as vb
    known = {0: "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262",
             1: "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213",
             2: "7b7015bb92cf0b318037702a6cdd81dee41224f734684c2c122cd6359cb1ee63"}
    ok7 = all(b3(pat(n), 7).hex() == h for n, h in known.items())
    print("known 7-round vectors (len 0,1,2) reproduced:", ok7)
    lens = [0, 1, 2, 3, 63, 64, 65, 127, 128, 129, 1023, 1024, 1025, 2048, 2049, 3072, 4096, 5000, 7168, 8193]
    bad = 0; tot = 0
    for r in range(1, 8):
        for n in lens:
            tot += 1
            if b3(pat(n), r) != vb(pat(n), r):
                bad += 1
    print("own tree vs verifier/blake3.py: %d cases, mismatches %d (rounds 1..7, lengths %s)" % (tot, bad, lens))
    return ok7 and bad == 0


class Cfg:
    def __init__(s, cv=None, v8=None, ctr=0, blen=64, flags=11, mconst=None, mvar=range(8, 16), rounds=3,
                 outs=range(8), hi=False, cvvar=False):
        s.cv = list(cv) if cv is not None else list(IV)
        s.v8 = list(v8) if v8 is not None else list(IV[:4])
        s.ctr, s.blen, s.flags = ctr, blen, flags
        s.mconst = dict(mconst or {})
        s.mvar = list(mvar); s.rounds = rounds; s.outs = list(outs); s.hi = hi; s.cvvar = cvvar


def trace(cfg, dce=True):
    """Return (ops, by_kind, source, want, outs). Variable message words are inputs i<slot>; if cvvar the chaining value words are inputs c<i>."""
    tr = Tracer()
    cv = [("v", "c%d" % i, M32) if cfg.cvvar else ("c", cfg.cv[i]) for i in range(8)]
    v = cv + [("c", w) for w in cfg.v8] + [("c", cfg.ctr & M32), ("c", cfg.ctr >> 32), ("c", cfg.blen), ("c", cfg.flags)]
    m = [("v", "i%d" % i, M32) if i in cfg.mvar else ("c", cfg.mconst.get(i, 0) & M32) for i in range(16)]
    if getattr(cfg, "mbuilder", None):
        m = cfg.mbuilder(tr)
    for _ in range(cfg.rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            v[a] = tr.add(v[a], v[b], x); v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            v[c] = tr.add(v[c], v[d]);    v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            v[a] = tr.add(v[a], v[b], y); v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            v[c] = tr.add(v[c], v[d]);    v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    outs = {}
    for i in range(8):
        z = tr.xor(v[i], v[i+8])
        if z[0] == "v" and z[2] > M32:
            z = tr.mask(z)
        outs[i] = z
    if cfg.hi:
        for i in range(8):
            z = tr.xor(v[i+8], ("v", "c%d" % i, M32) if cfg.cvvar else ("c", cfg.cv[i]))
            if z[0] == "v" and z[2] > M32:
                z = tr.mask(z)
            outs[8+i] = z
    want = [k for k in sorted(outs) if (k < 8 and k in cfg.outs) or (k >= 8)]
    names = [outs[k][1] if outs[k][0] == "v" else None for k in want]
    lines = tr.lines
    if dce:
        defs = {ln.split("=")[0]: ln for ln in lines}
        need = set(n for n in names if n and n in defs); stack = list(need)
        while stack:
            n = stack.pop()
            for t in re.findall(r"t\d+", defs[n].split("=", 1)[1]):
                if t not in need:
                    need.add(t); stack.append(t)
        lines = [ln for ln in lines if ln.split("=")[0] in need]
    by = {}
    for ln in lines:
        e = ln.split("=", 1)[1]
        k = "add" if "+" in e else "xor" if "^" in e else "shr" if ">>" in e else "shl" if "<<" in e else "or" if "|" in e else "and"
        by[k] = by.get(k, 0) + 1
    ins = ["c%d" % i for i in range(8)] if cfg.cvvar else []
    ins += ["i%d" % i for i in cfg.mvar]
    src = "def f(%s):\n" % ",".join(ins) + "".join("    %s\n" % ln for ln in lines)
    src += "    return (%s,)\n" % ",".join(n if n else "0" for n in names)
    return len(lines), by, src, want, outs


def check_trace(cfg, trials=4):
    """Run the traced circuit on 7 lanes and compare with the scalar compress for each lane and each requested output."""
    ops, by, src, want, outs = trace(cfg, dce=False)
    ns = {}
    exec(src, {}, ns)
    rng = random.Random(7)
    for _ in range(trials):
        lane = [[rng.getrandbits(32) for _ in range(16)] for _ in range(LANES)]
        cvl = [[rng.getrandbits(32) for _ in range(8)] for _ in range(LANES)]
        args = []
        if cfg.cvvar:
            args += [sum(cvl[l][i] << (PITCH*l) for l in range(LANES)) for i in range(8)]
        args += [sum(lane[l][i] << (PITCH*l) for l in range(LANES)) for i in cfg.mvar]
        res = ns["f"](*args)
        for l in range(LANES):
            m = [lane[l][i] if i in cfg.mvar else cfg.mconst.get(i, 0) & M32 for i in range(16)]
            cv = cvl[l] if cfg.cvvar else cfg.cv
            exp = compress(cv, m, cfg.ctr, cfg.blen, cfg.flags, cfg.rounds, cfg.v8)
            for idx, k in enumerate(want):
                if outs[k][0] != "v":
                    continue
                got = (res[idx] >> (PITCH*l)) & M32
                if got != exp[k]:
                    return False
    return True


if __name__ == "__main__":
    print("validate:", validate())
    base = Cfg()
    t = trace(base)
    print("baseline ops (dce)", t[0], t[1], "trace check:", check_trace(base))
    print("rho.PH", rho.PH)
