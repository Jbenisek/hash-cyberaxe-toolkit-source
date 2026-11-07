"""2-round BLAKE3 compression: which round-1 G calls carry a difference after the round-0
cancellation of each legitimate structural difference (block length, flags, counter)."""
import random

M32 = 0xffffffff
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
CALLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
NAMES = ["col0", "col1", "col2", "col3", "E0", "E1", "E2", "E3"]

def rotr(x, n): return ((x >> n) | (x << (32 - n))) & M32

def G(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & M32; v[d] = rotr(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & M32;     v[b] = rotr(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & M32; v[d] = rotr(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & M32;     v[b] = rotr(v[b] ^ v[c], 7)

def compress(cv, m, t, blen, flags, rounds, trace=None):
    v = list(cv) + IV[:4] + [t & M32, (t >> 32) & M32, blen, flags]
    m = list(m)
    for r in range(rounds):
        for k, (a, b, c, d) in enumerate(CALLS):
            if trace is not None:
                trace.append((r, k, tuple(v[i] for i in (a, b, c, d)), (m[2 * k], m[2 * k + 1])))
            G(v, a, b, c, d, m[2 * k], m[2 * k + 1])
        if trace is not None:
            trace.append((r, "state", tuple(v)))
        m = [m[PERM[i]] for i in range(16)]
    return [v[i] ^ v[i + 8] for i in range(8)]

def selftest():
    # BLAKE3("") = af1349b9...; single chunk, flags CHUNK_START|CHUNK_END|ROOT = 11, 7 rounds
    out = compress(IV, [0] * 16, 0, 0, 11, 7)
    h = b"".join(w.to_bytes(4, "little") for w in out).hex()
    assert h.startswith("af1349b9f5f9a1a6a0404dea36dcc949"), h
    print("selftest ok:", h[:32])

def cancel(cv, m, t, blen, flags, col, dstate):
    """Cancel a XOR difference dstate in v[12+col] with words m[2col], m[2col+1] (round 0)."""
    a, b, c, d = CALLS[col]
    v = list(cv) + IV[:4] + [t & M32, (t >> 32) & M32, blen, flags]
    a1 = (v[a] + v[b] + m[2 * col]) & M32
    a1n = a1 ^ dstate
    delta = (a1n - a1) & M32
    m2 = list(m)
    m2[2 * col] = (m[2 * col] + delta) & M32
    m2[2 * col + 1] = (m[2 * col + 1] - delta) & M32
    return m2

def r1_footprint(m, m2):
    """Round-1 G calls receiving a message-word difference, with the input slot."""
    mp = [m[PERM[i]] for i in range(16)]; mp2 = [m2[PERM[i]] for i in range(16)]
    out = []
    for k in range(8):
        for slot, idx in (("x", 2 * k), ("y", 2 * k + 1)):
            if mp[idx] != mp2[idx]:
                out.append(f"{NAMES[k]}.{slot}(old m{PERM[idx]})")
    return out

def experiment(name, setup, trials=2000, seed=1):
    rng = random.Random(seed)
    words_after_cols, out_words, r0_ok = [], [], 0
    foot = None
    for _ in range(trials):
        m = [rng.getrandbits(32) for _ in range(16)]
        (cvA, tA, bA, fA), (cvB, tB, bB, fB), comps = setup(rng, m)
        m2 = list(m)
        for col, ds in comps:
            m2 = cancel(cvB, m2, tB, bB, fB, col, ds)
        trA, trB = [], []
        oA = compress(cvA, m, tA, bA, fA, 2, trA)
        oB = compress(cvB, m2, tB, bB, fB, 2, trB)
        sA = [x for x in trA if x[1] == "state"]; sB = [x for x in trB if x[1] == "state"]
        r0_ok += sA[0][2] == sB[0][2]
        # state after round-1 columns: recompute from round-0 state
        def after_cols(tr):
            calls = [x for x in tr if x[0] == 1 and x[1] != "state"]
            v = list([x for x in tr if x[1] == "state"][0][2])
            for k in range(4):
                a, b, c, d = CALLS[k]; G(v, a, b, c, d, *calls[k][3])
            return v
        vA, vB = after_cols(trA), after_cols(trB)
        words_after_cols.append(sum(x != y for x, y in zip(vA, vB)))
        out_words.append(sum(x != y for x, y in zip(oA, oB)))
        foot = r1_footprint(m, m2)
    words_after_cols.sort(); out_words.sort()
    print(f"\n{name}")
    print(f"  round-0 state identical: {r0_ok}/{trials}")
    print(f"  round-1 message-difference footprint: {', '.join(foot)}")
    print(f"  differing state words after round-1 columns: min {words_after_cols[0]}, median {words_after_cols[len(words_after_cols)//2]}")
    print(f"  differing output words (of 8): min {out_words[0]}, median {out_words[len(out_words)//2]}")

if __name__ == "__main__":
    selftest()
    # current: final single-block chunk, lengths 55 vs 63, flags CHUNK_START|CHUNK_END = 3, same counter
    def length(rng, m):
        m[13] &= 0x00ffffff; m[14] = m[15] = 0
        t = rng.getrandbits(40) | 1
        return (IV, t, 55, 3), (IV, t, 63, 3), [(2, 55 ^ 63)]
    experiment("length 55 vs 63 (current), cancel with m4,m5", length)
    # root single chunk (flags 11) vs root parent (flags 12), both b=64, counter 0
    def flags_both(rng, m):
        return (IV, 0, 64, 12), (IV, 0, 64, 11), [(3, 12 ^ 11)]
    experiment("flags root-parent(12) vs root-chunk(11), cancel with m6,m7", flags_both)
    def flags_m6only(rng, m):
        return (IV, 0, 64, 12), (IV, 0, 64, 11), [("m6only", 12 ^ 11)]
    # one-word cancellation attempt for flags: only m6 changed
    rng = random.Random(5); ok = 0
    for _ in range(2000):
        m = [rng.getrandbits(32) for _ in range(16)]
        m2 = cancel(IV, m, 0, 64, 11, 3, 12 ^ 11); m2[7] = m[7]   # undo the m7 part
        trA, trB = [], []
        compress(IV, m, 0, 64, 12, 2, trA); compress(IV, m2, 0, 64, 11, 2, trB)
        ok += [x for x in trA if x[1] == "state"][0][2] == [x for x in trB if x[1] == "state"][0][2]
    print(f"\nflags cancelled with m6 alone (m7 unchanged): round-0 state identical {ok}/2000")
    # rightmost-node parent (counter 0, flags 4, b 64) vs chunk at index t (flags 3, b 64)
    def parent_vs_chunk(rng, m):
        t = 2 * (rng.getrandbits(20) | 1)
        return (IV, 0, 64, 4), (IV, t, 64, 3), [(0, t & M32), (3, 4 ^ 3)]
    experiment("parent(ctr 0, flags 4) vs chunk(ctr t, flags 3): cancel m0,m1 + m6,m7", parent_vs_chunk)
    # idea 1 as stated: counter-high + flags (needs t >= 2^32)
    def ctrhi_flags(rng, m):
        t = (rng.getrandbits(19) | 1) << 32
        return (IV, 0, 64, 4), (IV, t, 64, 3), [(1, (t >> 32) & M32), (3, 4 ^ 3)]
    experiment("counter-high + flags (idea 1): cancel m2,m3 + m6,m7", ctrhi_flags)
