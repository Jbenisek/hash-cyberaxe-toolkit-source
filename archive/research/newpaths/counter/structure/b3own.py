"""Own 2-round BLAKE3 pieces, written independently of verifier/blake3.py (only the spec constants
are shared).  Used to cross-check the organizer verifier and to model the last-chunk compression."""
import struct

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


def ror(x, n):
    return ((x >> n) | (x << (32 - n))) & M32


def rol(x, n):
    return ((x << n) | (x >> (32 - n))) & M32


def G(a, b, c, d, x, y, trace=None, tag=None):
    a1 = (a + b + x) & M32; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M32; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    if trace is not None:
        trace[tag] = dict(A=a, B=b, C=c, D=d, x=x, y=y, a1=a1, d1=d1, c1=c1, b1=b1,
                          a2=a2, d2=d2, c2=c2, b2=b2)
    return a2, b2, c2, d2


NAMES = (('K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3'),
         ('C0', 'C1', 'C2', 'C3', 'E0', 'E1', 'E2', 'E3'))


def compress_full(cv, w, counter, blen, flags, rounds=2, trace=None):
    """Returns (16 output words, states dict).  v12 = counter low word, v13 = counter high word."""
    v = list(cv) + list(IV[:4]) + [counter & M32, (counter >> 32) & M32, blen, flags]
    s = list(w)
    st = {}
    for r in range(rounds):
        for i, (a, b, c, d) in enumerate(CALLS):
            v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1],
                                       trace, NAMES[r][i] if r < 2 else None)
            if i == 3:
                st['SY'[r] if r < 2 else '?'] = list(v)
        st['XZ'[r] if r < 2 else '?'] = list(v)
        s = [s[p] for p in PERM]
    out = [v[i] ^ v[i + 8] for i in range(8)] + [v[i + 8] ^ cv[i] for i in range(8)]
    return out, st


def compress(cv, w, counter, blen, flags):
    return compress_full(cv, w, counter, blen, flags)[0]


def chunk_cv(chunk, counter):
    """CV of a NON-root chunk (any length 1..1024)."""
    cv = IV
    nblk = max(1, (len(chunk) + 63) // 64)
    for k in range(nblk):
        blk = chunk[64 * k:64 * k + 64]
        flags = (1 if k == 0 else 0) | (2 if k == nblk - 1 else 0)
        w = struct.unpack('<16I', blk.ljust(64, b'\0'))
        cv = compress(cv, w, counter, len(blk), flags)[:8]
    return tuple(cv)


def last_chunk_root_inputs(chunk, counter):
    """(cv_in, words, blen, flags) of the last block of a chunk (for a ROOT compression)."""
    cv = IV
    nblk = max(1, (len(chunk) + 63) // 64)
    for k in range(nblk):
        blk = chunk[64 * k:64 * k + 64]
        flags = (1 if k == 0 else 0) | (2 if k == nblk - 1 else 0)
        w = struct.unpack('<16I', blk.ljust(64, b'\0'))
        if k == nblk - 1:
            return cv, w, len(blk), flags
        cv = compress(cv, w, counter, len(blk), flags)[:8]


def parent_cv(l, r):
    return tuple(compress(IV, tuple(l) + tuple(r), 0, 64, 4)[:8])


def parent_root(l, r):
    return struct.pack('<8I', *compress(IV, tuple(l) + tuple(r), 0, 64, 4 | 8)[:8])


def stack_of_prefix(chunk_cvs):
    """Spec stack after pushing the given chunk CVs (merge whenever the count of chunks is even)."""
    stack = []
    for i, cv in enumerate(chunk_cvs):
        total = i + 1
        while total & 1 == 0:
            cv = parent_cv(stack.pop(), cv)
            total >>= 1
        stack.append(cv)
    return stack


def root_from_stack(stack, last_cv):
    """Digest of a message of >= 2 chunks: fold the last chunk's CV into the stack; the last merge is ROOT."""
    st = list(stack)
    cv = last_cv
    while len(st) > 1:
        cv = parent_cv(st.pop(), cv)
    return parent_root(st.pop(), cv)
