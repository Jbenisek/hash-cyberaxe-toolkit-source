"""ctr x join, part N: coupling.py's two-sided split search with the chunk counter t free.

Imports World (constants, G, diffs) from grok/work/job30_split/coupling.py unchanged.
build_t() is coupling.py's World.build with two changes only:
  K0's d input is T0 (t low word):  K0_a1 = rol(K0_d1,16) ^ T0   (was rol(K0_d1,16))
  K1's d input is T1 (t high word): K1_a1 = rol(K1_d1,16) ^ T1   (was rol(K1_d1,16))
Parametrizations (free words, all others solved):
  C0   : filed 8, t = 0                          (control, reproduces the counter-fixed search)
  T0   : filed 8 + T0                            (model.py 'filed 8 + T0', t free)
  T0T1 : filed 8 + T0 + T1                       (model.py counter=2; T1 is really < 2^22)
  E1d1 : filed 8 + E1.d1 prescribed, T0 solved   (model.py 'filed 8 + E1.d1 (T0 determined)')
  E3h1 : filed 8 + E3.h1 prescribed, T0 solved   (model.py 'filed 8 + E3.h1 (T0 determined)')
Every parametrization is checked against a full 2-round compression with counter t
(pins, E1/E3 inputs, half match, residual = key1 XOR key3) before any search.
"""

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

import random
import sys
import time

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job30_split'))
import coupling  # noqa: E402
from coupling import World, FREE_NAMES  # noqa: E402

MODES = {
    'C0': FREE_NAMES,
    'T0': FREE_NAMES + ('T0',),
    'T0T1': FREE_NAMES + ('T0', 'T1'),
    'E1d1': FREE_NAMES + ('E1d1',),
    'E3h1': FREE_NAMES + ('E3h1',),
}


class WorldT(World):
    def __init__(self, W, mode):
        World.__init__(self, W)
        self.mode = mode
        self.names = MODES[mode]
        self.nf = len(self.names)

    def build_t(self, free):
        M = self.MASK
        free = [z & M for z in free]
        c1, d1, dd, s15, s9, w5, x2, y = free[:8]
        T0 = T1 = 0
        if self.mode in ('T0', 'T0T1'):
            T0 = free[8]
        if self.mode == 'T0T1':
            T1 = free[9]
        IV = self.IV
        ror, rol = self.ror, self.rol
        R16, R12, R8, R7 = self.R16, self.R12, self.R8, self.R7

        K2_a1 = (IV[2] + IV[6] + self.W4) & M
        K2_d1 = ror(self.N55 ^ K2_a1, R16)
        K2_c1 = (IV[2] + K2_d1) & M
        K2_b1 = ror(IV[6] ^ K2_c1, R12)
        S2 = (K2_a1 + K2_b1 + w5) & M
        S14 = ror(K2_d1 ^ S2, R8)
        S10 = (K2_c1 + S14) & M
        S6 = ror(K2_b1 ^ S10, R7)

        D3_a1 = rol(dd, R16) ^ S14
        D3_c1 = (s9 + dd) & M
        D3_b1 = (self.X3 - D3_a1) & M
        S4 = rol(D3_b1, R12) ^ D3_c1
        S3 = (D3_a1 - S4) & M
        X14 = ror(dd ^ self.X3, R8)
        X9 = (D3_c1 + X14) & M
        X4 = ror(D3_b1 ^ X9, R7)

        K3_d1 = rol(s15, R8) ^ S3
        K3_c1 = (IV[3] + K3_d1) & M
        K3_b1 = ror(IV[7] ^ K3_c1, R12)
        S11 = (K3_c1 + s15) & M
        S7 = ror(K3_b1 ^ S11, R7)
        K3_a1 = rol(K3_d1, R16) ^ self.FLAG
        w6 = (K3_a1 - IV[3] - IV[7]) & M
        w7 = (S3 - K3_a1 - K3_b1) & M

        X8 = (c1 - d1) & M
        C0_b1 = ror(X4 ^ c1, R12)
        D2_b1 = rol(self.X7, R7) ^ X8
        D2_c1 = rol(D2_b1, R12) ^ S7
        X13 = (X8 - D2_c1) & M

        D2_a1 = (x2 - D2_b1 - self.W13) & M
        D2_d1 = rol(X13, R8) ^ x2
        S13 = rol(D2_d1, R16) ^ D2_a1
        S8 = (D2_c1 - D2_d1) & M
        w12 = (D2_a1 - S2 - S7) & M

        K1_c1 = (s9 - S13) & M
        K1_d1 = (K1_c1 - IV[1]) & M
        K1_a1 = rol(K1_d1, R16) ^ T1
        K1_b1 = ror(IV[5] ^ K1_c1, R12)
        S1 = rol(S13, R8) ^ K1_d1
        S5 = ror(K1_b1 ^ s9, R7)
        w2 = (K1_a1 - IV[1] - IV[5]) & M
        w3 = (S1 - K1_a1 - K1_b1) & M

        K0_b1 = rol(S4, R7) ^ S8
        K0_c1 = rol(K0_b1, R12) ^ IV[4]
        K0_d1 = (K0_c1 - IV[0]) & M
        S12 = (S8 - K0_c1) & M
        S0 = rol(S12, R8) ^ K0_d1

        Y8 = rol(y, R7) ^ C0_b1
        Y12 = (Y8 - c1) & M
        Y0 = rol(Y12, R8) ^ d1
        C0_a1 = (Y0 - C0_b1 - w6) & M
        X12 = rol(d1, R16) ^ C0_a1

        D1_c1 = (self.X11 - X12) & M
        D1_b1 = ror(S6 ^ D1_c1, R12)
        X6 = ror(D1_b1 ^ self.X11, R7)
        D1_d1 = (D1_c1 - S11) & M
        X1 = rol(X12, R8) ^ D1_d1

        X0 = (C0_a1 - X4 - w2) & M
        D0_d1 = rol(self.X15, R8) ^ X0
        D0_c1 = (S10 + D0_d1) & M
        X10 = (D0_c1 + self.X15) & M
        D0_b1 = ror(S5 ^ D0_c1, R12)
        X5 = ror(D0_b1 ^ X10, R7)
        D0_a1 = rol(D0_d1, R16) ^ s15
        w8 = (D0_a1 - S0 - S5) & M
        w9 = (X0 - D0_a1 - D0_b1) & M

        D1_a1 = rol(D1_d1, R16) ^ S12
        w10 = (D1_a1 - S1 - S6) & M
        w11 = (X1 - D1_a1 - D1_b1) & M

        Y1, Y5, Y9, Y13 = self.G(X1, X5, X9, X13, w3, w10)

        # C2 first half (needed to solve w0 when a C2 output is prescribed)
        C2_a1 = (x2 + X6 + w7) & M
        C2_d1 = ror(X14 ^ C2_a1, R16)
        C2_c1 = (X10 + C2_d1) & M
        C2_b1 = ror(X6 ^ C2_c1, R12)
        if self.mode in ('C0', 'T0', 'T0T1'):
            K0_a1 = rol(K0_d1, R16) ^ T0
            w0 = (K0_a1 - IV[0] - IV[4]) & M
        else:
            P = free[8]
            if self.mode == 'E1d1':
                E1_a1 = rol(P, R16) ^ Y12          # E1.d1 = ror(Y12 ^ E1.a1, 16)
                Y6t = (E1_a1 - Y1 - w12) & M      # E1.a1 = Y1 + Y6 + w12
                c2 = rol(Y6t, R7) ^ C2_b1         # Y6 = ror(b1 ^ c2, 7)
                d2 = (c2 - C2_c1) & M
                a2 = rol(d2, R8) ^ C2_d1
            else:  # E3h1
                ea1 = (self.Y3 + y) & M           # Y4 = y, w15 = 0
                Y14t = rol(P, R16) ^ ea1          # E3.h1 = ror(Y14 ^ ea1, 16)
                a2 = rol(Y14t, R8) ^ C2_d1        # Y14 = ror(d1 ^ a2, 8)
            w0 = (a2 - C2_a1 - C2_b1) & M
            K0_a1 = (w0 + IV[0] + IV[4]) & M
            T0 = K0_a1 ^ rol(K0_d1, R16)
        w1 = (S0 - K0_a1 - K0_b1) & M

        Y2, Y6, Y10, Y14 = self.G(x2, X6, X10, X14, w7, w0)
        Y4 = y
        words = [w0, w1, w2, w3, self.W4, w5, w6, w7,
                 w8, w9, w10, w11, w12, self.W13, 0, 0]
        return {"Y1": Y1, "Y6": Y6, "Y12": Y12, "w12": w12, "w5": w5,
                "Y4": Y4, "Y9": Y9, "Y14": Y14, "w8": w8,
                "T0": T0, "T1": T1, "words": words}

    def e_inputs_t(self, free):
        st = self.build_t(free)
        e1 = (st["Y1"], st["Y6"], st["Y12"], st["w12"], st["w5"])
        e3 = (st["Y4"], st["Y9"], st["Y14"], st["w8"])
        return e1, e3, st

    def compress_t(self, words, n, t0, t1):
        M = self.MASK
        v = list(self.IV) + list(self.IV[:4]) + [t0 & M, t1 & M, n & M, self.FLAG]
        sched = ((0, 4, 8, 12, 0, 1), (1, 5, 9, 13, 2, 3), (2, 6, 10, 14, 4, 5), (3, 7, 11, 15, 6, 7),
                 (0, 5, 10, 15, 8, 9), (1, 6, 11, 12, 10, 11), (2, 7, 8, 13, 12, 13), (3, 4, 9, 14, 14, 15),
                 (0, 4, 8, 12, 2, 6), (1, 5, 9, 13, 3, 10), (2, 6, 10, 14, 7, 0), (3, 7, 11, 15, 4, 13),
                 (0, 5, 10, 15, 1, 11), (1, 6, 11, 12, 12, 5), (2, 7, 8, 13, 9, 14), (3, 4, 9, 14, 15, 8))
        snap = {}
        for i, (a, b, c, d, x, y) in enumerate(sched):
            v[a], v[b], v[c], v[d] = self.G(v[a], v[b], v[c], v[d], words[x], words[y])
            if i == 7:
                snap["X"] = v[:]
            elif i == 11:
                snap["Y"] = v[:]
        snap["o"] = [(v[i] ^ v[i + 8]) & M for i in range(8)]
        return snap


def rand_free(rng, W, nf):
    return [rng.getrandbits(W) for _ in range(nf)]


def keys(world, free):
    e1, e3, _ = world.e_inputs_t(free)
    k1, k3, _, _ = world.diffs(e1, e3)
    W = world.W
    p1 = k1[0] | (k1[1] << W) | (k1[2] << (2 * W)) | (k1[3] << (3 * W))
    p3 = k3[0] | (k3[1] << W) | (k3[2] << (2 * W)) | (k3[3] << (3 * W))
    return p1, p3, e1, e3


def verify_t(world, rng, trials):
    """Full-compression check with counter t. W=32: pins, inputs, half match, residual.
    Toy W: pins and inputs (as coupling.verify does)."""
    W, M = world.W, world.MASK
    half_ok = 0
    for _ in range(trials):
        free = rand_free(rng, W, world.nf)
        e1, e3, st = world.e_inputs_t(free)
        words, t0, t1 = st["words"], st["T0"], st["T1"]
        n_a = 55 if W == 32 else world.N55
        snap = world.compress_t(words, n_a, t0, t1)
        X, Y = snap["X"], snap["Y"]
        if (X[3], X[7], X[11], X[15]) != (world.X3, world.X7, world.X11, world.X15):
            return False, "X pins mismatch"
        got = (Y[1], Y[6], Y[12], words[12], words[5], Y[4], Y[9], Y[14], words[8])
        if got != e1 + e3:
            return False, "Y/message inputs mismatch"
        if world.mode == 'E1d1':
            a1 = (e1[0] + e1[1] + e1[3]) & M
            if world.ror(e1[2] ^ a1, world.R16) != free[8]:
                return False, "prescribed E1.d1 not met"
        if world.mode == 'E3h1':
            ea1 = (world.Y3 + e3[0]) & M
            if world.ror(e3[2] ^ ea1, world.R16) != free[8]:
                return False, "prescribed E3.h1 not met"
        if W == 32:
            wb = words[:]
            wb[4] = world.W4p
            wb[5] = (words[5] + world.delta) & M
            snap_b = world.compress_t(wb, 63, t0, t1)
            if snap["X"] != snap_b["X"]:
                return False, "round-0 state differs A/B"
            oa, ob = snap["o"], snap_b["o"]
            if (oa[0], oa[2], oa[5], oa[7]) == (ob[0], ob[2], ob[5], ob[7]):
                half_ok += 1
            r_dig = world.residual_from_digest(oa, ob)
            k1, k3, _, _ = world.diffs(e1, e3)
            if r_dig != tuple(k1[i] ^ k3[i] for i in range(4)):
                return False, "residual != key1 XOR key3"
    return True, "trials %d half %d" % (trials, half_ok)


def word_influence(world, rng, bases, draws):
    """Per free word: fraction of resamples that move each E1 / E3 input, key1, key3."""
    nf, W = world.nf, world.W
    rows = []
    for wi in range(nf):
        mv1 = mv3 = mk1 = mk3 = tot = 0
        in_hits = [0] * 9
        for _ in range(bases):
            base = rand_free(rng, W, nf)
            p1, p3, e1, e3 = keys(world, base)
            for _ in range(draws):
                alt = base[:]
                alt[wi] = rng.getrandbits(W)
                q1, q3, f1, f3 = keys(world, alt)
                tot += 1
                old, new = e1 + e3, f1 + f3
                for j in range(9):
                    if old[j] != new[j]:
                        in_hits[j] += 1
                mv1 += (e1 != f1)
                mv3 += (e3 != f3)
                mk1 += (p1 != q1)
                mk3 += (p3 != q3)
        rows.append((world.names[wi], tot, in_hits, mk1, mk3))
    return rows


def axis_split_n(world, rng, bases, draws, keep=12):
    """coupling.axis_split generalized to nf free words (3^nf role codes)."""
    nf, W = world.nf, world.W
    best = []
    for code in range(3 ** nf):
        c = code
        u_idx, v_idx = [], []
        for i in range(nf):
            r = c % 3
            c //= 3
            if r == 1:
                u_idx.append(i)
            elif r == 2:
                v_idx.append(i)
        if not u_idx or not v_idx:
            continue
        survive = (1 << (4 * W)) - 1
        for _b in range(bases):
            base = rand_free(rng, W, nf)
            p1, p3, _, _ = keys(world, base)
            mu1 = mu3 = mv1 = mv3 = 0
            for _d in range(draws):
                alt = base[:]
                for i in u_idx:
                    alt[i] = rng.getrandbits(W)
                q1, q3, _, _ = keys(world, alt)
                mu1 |= p1 ^ q1
                mu3 |= p3 ^ q3
                alt = base[:]
                for i in v_idx:
                    alt[i] = rng.getrandbits(W)
                q1, q3, _, _ = keys(world, alt)
                mv1 |= p1 ^ q1
                mv3 |= p3 ^ q3
            survive &= mu1 & ~mu3 & mv3 & ~mv1
            if survive == 0:
                break
        k = bin(survive).count("1")
        if k:
            best.append((k, u_idx, v_idx, survive))
    best.sort(key=lambda z: -z[0])
    return best[:keep], len(best)


def confirm_n(world, rng, parts, bases, draws):
    W, nf = world.W, world.nf
    out = []
    for u_idx, v_idx in parts:
        survive = (1 << (4 * W)) - 1
        for _b in range(bases):
            base = rand_free(rng, W, nf)
            p1, p3, _, _ = keys(world, base)
            mu1 = mu3 = mv1 = mv3 = 0
            for _d in range(draws):
                for grp, isu in ((u_idx, True), (v_idx, False)):
                    alt = base[:]
                    for i in grp:
                        alt[i] = rng.getrandbits(W)
                    q1, q3, _, _ = keys(world, alt)
                    if isu:
                        mu1 |= p1 ^ q1
                        mu3 |= p3 ^ q3
                    else:
                        mv1 |= p1 ^ q1
                        mv3 |= p3 ^ q3
            survive &= mu1 & ~mu3 & mv3 & ~mv1
            if survive == 0:
                break
        out.append((bin(survive).count("1"), u_idx, v_idx))
    return out


def bitflip_report(world, rng, bases):
    """coupling.bit_influence + per_bit_split_report, nf words: for each of the 4W match bits,
    which free words move key1's bit and which move key3's bit (single-bit flips)."""
    nf, W = world.nf, world.W
    m1 = [0] * nf
    m3 = [0] * nf
    for _ in range(bases):
        base = rand_free(rng, W, nf)
        p1, p3, _, _ = keys(world, base)
        for wi in range(nf):
            for b in range(W):
                alt = base[:]
                alt[wi] ^= 1 << b
                q1, q3, _, _ = keys(world, alt)
                m1[wi] |= p1 ^ q1
                m3[wi] |= p3 ^ q3
    nb = 4 * W
    split = coupled = neither = one_sided = 0
    for bit in range(nb):
        a = sum(1 << wi for wi in range(nf) if (m1[wi] >> bit) & 1)
        c = sum(1 << wi for wi in range(nf) if (m3[wi] >> bit) & 1)
        if a == 0 and c == 0:
            neither += 1
        elif a and c and (a & ~c) and (c & ~a):
            split += 1      # some word moves only key1's bit, another only key3's
        elif a and c:
            coupled += 1
        else:
            one_sided += 1
    per_word = []
    for wi in range(nf):
        per_word.append((world.names[wi], bin(m1[wi]).count("1"), bin(m3[wi]).count("1")))
    return {"bits": nb, "split_candidates": split, "coupled": coupled,
            "neither": neither, "one_sided": one_sided, "per_word": per_word}


def main():
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    modes = sys.argv[2].split(',') if len(sys.argv) > 2 else ['C0', 'T0', 'T0T1', 'E1d1', 'E3h1']
    sb, sd = (1, 2) if W == 32 else (2, 6)          # screen as in coupling.py
    sb2, sd2 = (2, 6) if W == 32 else (4, 24)       # stronger screen
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    log("W %d modes %s seed 4040; screen1 bases=%d draws=%d; screen2 bases=%d draws=%d; confirm bases=3 draws=16"
        % (W, modes, sb, sd, sb2, sd2))
    for mode in modes:
        rng = random.Random(4040)
        w = WorldT(W, mode)
        t0 = time.time()
        ok, info = verify_t(w, rng, 40)
        log("=== mode %s free %s" % (mode, ",".join(w.names)))
        log("verify %s %s" % (ok, info))
        if not ok:
            log("STOP mode %s: verification failed" % mode)
            continue
        log("word influence (resample one word; hits on Y1 Y6 Y12 w12 w5 | Y4 Y9 Y14 w8; key1 moved; key3 moved):")
        for name, tot, hits, k1, k3 in word_influence(w, rng, 6, 4):
            log("  %-5s n=%d  E1in %s | E3in %s  key1 %d key3 %d" % (
                name, tot, hits[:5], hits[5:], k1, k3))
        rep = bitflip_report(w, rng, 2)
        log("bitflip per-bit: bits %d split_candidates %d coupled %d one_sided %d neither %d" % (
            rep["bits"], rep["split_candidates"], rep["coupled"], rep["one_sided"], rep["neither"]))
        log("  per word (#key1 bits moved, #key3 bits moved): " + " ".join(
            "%s:%d/%d" % r for r in rep["per_word"]))
        best, nk = axis_split_n(w, rng, sb, sd)
        log("axis screen1 (%d codes) partitions with k>0: %d" % (3 ** w.nf, nk))
        best2, nk2 = axis_split_n(w, rng, sb2, sd2)
        log("axis screen2 partitions with k>0: %d" % nk2)
        cand = []
        for k, u, v, _ in best + best2:
            if (u, v) not in cand:
                cand.append((u, v))
        for k, u, v, _ in (best + best2)[:8]:
            log("  cand k=%d U=%s V=%s" % (k, ",".join(w.names[i] for i in u), ",".join(w.names[i] for i in v)))
        conf = confirm_n(w, random.Random(4141), cand[:24], 3, 16)
        kmax = max([k for k, _, _ in conf], default=0)
        for k, u, v in conf[:24]:
            if k:
                log("  CONFIRMED k=%d U=%s V=%s" % (k, ",".join(w.names[i] for i in u),
                                                   ",".join(w.names[i] for i in v)))
        log("mode %s: candidates %d, confirmed max k = %d  (%.0fs)" % (mode, len(cand), kmax, time.time() - t0))
    name = "numeric_W%d_%s.txt" % (W, "_".join(modes))
    open(name, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    log("WROTE " + name)


if __name__ == "__main__":
    main()
