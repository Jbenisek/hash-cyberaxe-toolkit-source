"""Per-step profile of the shipped 3-round SWAR circuit (own code, dig-scan-b3r3, 2026-10-12).
Rebuilds the tracer of candidate_blake3/experiments/rho.py with a parameter pitch, per-op step tags, operand-order
variants, rotation variants and single-op ablation. Reproduces 595 ops and the shipped source text at pitch 36.
Validation (run `python step_profile_r1.py validate`): scalar digest vs verifier blake3 (7 rounds, empty input vector,
64-byte msgs at 3 and 7 rounds) and packed circuit vs scalar."""

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

import sys, random, itertools, json, hashlib, importlib.util
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
CALLNAME = ["C0", "C1", "C2", "C3", "D0", "D1", "D2", "D3"]

def _ror(v, k): return ((v >> k) | (v << (32 - k))) & M32
def digest_words(m, rounds=3, flags=11, blen=64, counter=0):
    v = list(IV) + list(IV[:4]) + [counter & M32, counter >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            v[a] = (v[a]+v[b]+x) & M32; v[d] = _ror(v[d]^v[a], 16)
            v[c] = (v[c]+v[d]) & M32; v[b] = _ror(v[b]^v[c], 12)
            v[a] = (v[a]+v[b]+y) & M32; v[d] = _ror(v[d]^v[a], 8)
            v[c] = (v[c]+v[d]) & M32; v[b] = _ror(v[b]^v[c], 7)
        m = [m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]

class Tr:
    def __init__(self, pitch=36, order=None, rotmode=None):
        self.pitch = pitch; self.lanes = 256 // pitch
        self.rep = sum(1 << (pitch*i) for i in range(self.lanes)); self.lim = 1 << pitch
        self.lines, self.tags, self.ops, self.by, self.k = [], [], 0, {}, 0
        self.tag = None; self.order = order or {}; self.rotmode = rotmode or {}
    def emit(self, kind, expr):
        self.k += 1; name = "t%d" % self.k
        self.lines.append("%s=%s" % (name, expr)); self.tags.append((self.tag, kind)); self.ops += 1
        self.by[kind] = self.by.get(kind, 0) + 1
        return name
    def mask(self, a): return ("v", self.emit("and", "%s&%d" % (a[1], self.rep*M32)), M32)
    def add(self, *xs):
        key = self.tag
        if key in self.order and len(xs) == len(self.order[key]): xs = [xs[i] for i in self.order[key]]
        c = sum(x[1] for x in xs if x[0] == "c") & M32
        vs = [x for x in xs if x[0] == "v"]
        if not vs: return ("c", c)
        acc = vs[0]
        for v in vs[1:]:
            while acc[2] + v[2] >= self.lim:
                if acc[2] >= v[2]: acc = self.mask(acc)
                else: v = self.mask(v)
            acc = ("v", self.emit("add", "%s+%s" % (acc[1], v[1])), acc[2] + v[2])
        if c:
            if acc[2] + c >= self.lim: acc = self.mask(acc)
            acc = ("v", self.emit("add", "%s+%d" % (acc[1], self.rep*c)), acc[2] + c)
        return acc
    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c": return ("c", a[1]^b[1])
        if a[0] == "c": a, b = b, a
        if b[0] == "c":
            if b[1] == 0: return a
            return ("v", self.emit("xor", "%s^%d" % (a[1], self.rep*b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("xor", "%s^%s" % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)
    def ror(self, a, r, mode=None):
        if a[0] == "c": return ("c", _ror(a[1], r))
        rep = self.rep
        mode = mode or self.rotmode.get(self.tag, "std")
        hm = rep*((1 << (32-r))-1); lm = rep*(((1 << r)-1) << (32-r))
        if mode == "std":
            s1 = self.emit("shr", "%s>>%d" % (a[1], r)); h = self.emit("and", "%s&%d" % (s1, hm))
            s2 = self.emit("shl", "%s<<%d" % (a[1], 32-r)); l = self.emit("and", "%s&%d" % (s2, lm))
        else:  # maskfirst: and then shift
            m1 = self.emit("and", "%s&%d" % (a[1], rep*(M32 ^ ((1 << r)-1)))); h = self.emit("shr", "%s>>%d" % (m1, r))
            m2 = self.emit("and", "%s&%d" % (a[1], rep*((1 << r)-1))); l = self.emit("shl", "%s<<%d" % (m2, 32-r))
        return ("v", self.emit("or", "%s|%s" % (h, l)), M32)

def build(pitch=36, order=None, rotmode=None, dist=None, rounds=3):
    """dist: set of tags whose  rot(xor(d,a)) is replaced by xor(rot(d),rot(a))."""
    tr = Tr(pitch, order, rotmode); dist = dist or set()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", 11)]
    m = [("c", 0)]*8 + [("v", "i%d" % i, M32) for i in range(8, 16)]
    for rd in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            tr.tag = (rd, j, 1); v[a] = tr.add(v[a], v[b], x)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 16) if tr.tag not in dist else tr.xor(tr.ror(v[d], 16), tr.ror(v[a], 16))
            tr.tag = (rd, j, 2); v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 12) if tr.tag not in dist else tr.xor(tr.ror(v[b], 12), tr.ror(v[c], 12))
            tr.tag = (rd, j, 3); v[a] = tr.add(v[a], v[b], y)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 8) if tr.tag not in dist else tr.xor(tr.ror(v[d], 8), tr.ror(v[a], 8))
            tr.tag = (rd, j, 4); v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 7) if tr.tag not in dist else tr.xor(tr.ror(v[b], 7), tr.ror(v[c], 7))
        m = [m[i] for i in PERM]
    out = []
    tr.tag = (rounds-1, 9, 9)
    for i in range(8):
        z = tr.xor(v[i], v[i+8])
        if z[2] > M32: z = tr.mask(z)
        out.append(z[1])
    return tr, out

def compile_circuit(tr, out, lines=None):
    src = "def batch(%s):\n" % ",".join("i%d" % i for i in range(8, 16))
    src += "".join("    %s\n" % ln for ln in (lines or tr.lines)) + "    return (%s,)\n" % ",".join(out)
    ns = {}; exec(src, {}, ns); return ns["batch"], src

def pack(tr, vals): return sum(v << (tr.pitch*l) for l, v in enumerate(vals))
def test_inputs(tr, n_rand=300, seed=7):
    rng = random.Random(seed); L = tr.lanes; sets = []
    sets.append([[M32]*8 for _ in range(L)]); sets.append([[0]*8 for _ in range(L)])
    for _ in range(n_rand // L + 1): sets.append([[rng.getrandbits(32) for _ in range(8)] for _ in range(L)])
    for _ in range(8): sets.append([[rng.choice([0, M32, 0x80000000, 0x7FFFFFFF, rng.getrandbits(32)]) for _ in range(8)] for _ in range(L)])
    return sets
_EXP = {}
def check(tr, fn, sets):
    """returns (wrong lanes, total lanes) or None on exception"""
    bad = tot = 0
    for xs in sets:
        w = [pack(tr, [xs[l][i] for l in range(tr.lanes)]) for i in range(8)]
        try: o = fn(*w)
        except Exception: return None
        for l in range(tr.lanes):
            key = tuple(xs[l])
            if key not in _EXP: _EXP[key] = digest_words([0]*8 + xs[l])
            got = [(o[i] >> (tr.pitch*l)) & M32 for i in range(8)]
            tot += 1; bad += (_EXP[key] != got)
    return bad, tot

def validate():
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
    from verifier.blake3 import blake3 as vb
    res = {}
    res["empty_7r"] = vb(b"", 7).hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    rng = random.Random(3); ok7 = ok3 = True
    for _ in range(50):
        msg = bytes(rng.getrandbits(8) for _ in range(64)); w = [int.from_bytes(msg[4*i:4*i+4], "little") for i in range(16)]
        for r in (7, 3):
            d = digest_words(w, r); b = vb(msg, r)[:32]
            e = b"".join(x.to_bytes(4, "little") for x in d)
            if e != b:
                if r == 7: ok7 = False
                else: ok3 = False
    res["scalar_vs_verifier_64B_7r"] = ok7; res["scalar_vs_verifier_64B_3r"] = ok3
    tr, out = build(); fn, src = compile_circuit(tr, out)
    res["ops_default"] = tr.ops; res["by"] = tr.by
    res["packed_vs_scalar_wrong_total"] = check(tr, fn, test_inputs(tr))
    spec = importlib.util.spec_from_file_location("rho", _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments/rho.py'))
    rho = importlib.util.module_from_spec(spec); spec.loader.exec_module(rho)
    res["same_source_as_shipped_rho"] = (src == rho._SRC); res["shipped_ops"] = rho.PH
    return res

if __name__ == "__main__":
    if sys.argv[1:] == ["validate"]: print(json.dumps(validate(), default=str))
