"""Independent BLAKE3 (hash mode, 32-byte output) with a round-count knob.

Written from the BLAKE3 paper's structure (streaming hasher with a pending
chunk and a CV stack, as in the reference implementation), not from the
organizers' file. `rounds` keeps the first `rounds` rounds of the 7.
The compression function is pluggable so the tree logic can be tested with
a fast stand-in at very large chunk counts.
"""

IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
MSG_PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
F_CHUNK_START, F_CHUNK_END, F_PARENT, F_ROOT = 1 << 0, 1 << 1, 1 << 2, 1 << 3
CHUNK_LEN, BLOCK_LEN = 1024, 64
M32 = (1 << 32) - 1


def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & M32


def quarter(s, a, b, c, d, mx, my):
    s[a] = (s[a] + s[b] + mx) & M32
    s[d] = rotr(s[d] ^ s[a], 16)
    s[c] = (s[c] + s[d]) & M32
    s[b] = rotr(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b] + my) & M32
    s[d] = rotr(s[d] ^ s[a], 8)
    s[c] = (s[c] + s[d]) & M32
    s[b] = rotr(s[b] ^ s[c], 7)


def one_round(s, m):
    # columns
    quarter(s, 0, 4, 8, 12, m[0], m[1])
    quarter(s, 1, 5, 9, 13, m[2], m[3])
    quarter(s, 2, 6, 10, 14, m[4], m[5])
    quarter(s, 3, 7, 11, 15, m[6], m[7])
    # diagonals
    quarter(s, 0, 5, 10, 15, m[8], m[9])
    quarter(s, 1, 6, 11, 12, m[10], m[11])
    quarter(s, 2, 7, 8, 13, m[12], m[13])
    quarter(s, 3, 4, 9, 14, m[14], m[15])


def real_compress(cv, block_words, counter, block_len, flags, rounds):
    assert 0 <= counter < (1 << 64)
    s = [cv[0], cv[1], cv[2], cv[3], cv[4], cv[5], cv[6], cv[7],
         IV[0], IV[1], IV[2], IV[3],
         counter & M32, (counter >> 32) & M32, block_len, flags]
    m = list(block_words)
    for r in range(rounds):
        one_round(s, m)
        if r != rounds - 1:
            m = [m[MSG_PERM[i]] for i in range(16)]
    out = [0] * 16
    for i in range(8):
        out[i] = s[i] ^ s[i + 8]
        out[i + 8] = s[i + 8] ^ cv[i]
    return out


def words_le(block):
    block = block + bytes(BLOCK_LEN - len(block))
    return [int.from_bytes(block[4 * i:4 * i + 4], "little") for i in range(16)]


class Out:
    def __init__(self, cv, words, counter, block_len, flags):
        self.cv, self.words, self.counter = cv, words, counter
        self.block_len, self.flags = block_len, flags

    def chaining_value(self, C):
        return C(self.cv, self.words, self.counter, self.block_len, self.flags)[:8]

    def root32(self, C):
        w = C(self.cv, self.words, 0, self.block_len, self.flags | F_ROOT)
        return b"".join(x.to_bytes(4, "little") for x in w[:8])


class ChunkState:
    def __init__(self, counter, C):
        self.cv = list(IV)
        self.counter = counter
        self.buf = b""
        self.blocks_done = 0
        self.C = C

    def length(self):
        return BLOCK_LEN * self.blocks_done + len(self.buf)

    def start_flag(self):
        return F_CHUNK_START if self.blocks_done == 0 else 0

    def update(self, data):
        data = bytes(data)
        while data:
            if len(self.buf) == BLOCK_LEN:
                self.cv = self.C(self.cv, words_le(self.buf), self.counter,
                                 BLOCK_LEN, self.start_flag())[:8]
                self.blocks_done += 1
                self.buf = b""
            take = min(BLOCK_LEN - len(self.buf), len(data))
            self.buf += data[:take]
            data = data[take:]

    def output(self):
        return Out(self.cv, words_le(self.buf), self.counter, len(self.buf),
                   self.start_flag() | F_CHUNK_END)


def parent_out(l, r):
    return Out(list(IV), list(l) + list(r), 0, BLOCK_LEN, F_PARENT)


class Hasher:
    def __init__(self, rounds=7, compress=None):
        if compress is None:
            compress = lambda cv, w, c, bl, f: real_compress(cv, w, c, bl, f, rounds)
        self.C = compress
        self.chunk = ChunkState(0, self.C)
        self.stack = []

    def _push(self, cv, total):
        while total & 1 == 0:
            cv = parent_out(self.stack.pop(), cv).chaining_value(self.C)
            total >>= 1
        self.stack.append(cv)

    def update(self, data):
        data = memoryview(bytes(data))
        while len(data):
            if self.chunk.length() == CHUNK_LEN:
                cv = self.chunk.output().chaining_value(self.C)
                total = self.chunk.counter + 1
                self._push(cv, total)
                self.chunk = ChunkState(total, self.C)
            take = min(CHUNK_LEN - self.chunk.length(), len(data))
            self.chunk.update(data[:take])
            data = data[take:]
        return self

    def digest(self):
        out = self.chunk.output()
        for left in reversed(self.stack):
            out = parent_out(left, out.chaining_value(self.C))
        return out.root32(self.C)


def blake3(data, rounds=7):
    return Hasher(rounds).update(bytes(data)).digest()
