"""blake3_toy.py: the organizer's verifier/blake3.py (copied here as blake3_ref.py) ported line by line to a
word size W, so that the organizer's own tree logic can referee toy-size collisions.

Changes against blake3_ref.py, and nothing else:
  - MASK = 2^W - 1; rotations (16, 12, 8, 7) at W = 32, (4, 3, 2, 1) at W = 8 (the toy of counter\\toy\\toy.h);
  - IV = the top W bits of the real IV words;
  - a "byte" has BB bits (8 at W = 32, 2 at W = 8 as in toy.h), W / BB bytes per word, little-endian;
    a block is 16 words = 64 bytes and a chunk 1024 bytes at both sizes;
  - the counter is split as (counter mod 2^W, counter >> W).
Messages are lists of byte values (0 .. 2^BB - 1). At W = 32 selftest() checks equality with blake3_ref.blake3
(rounds = 2) on random multi-chunk byte strings.
"""
import random
import sys

sys.dont_write_bytecode = True

IV32 = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERMUTATION = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CHUNK_START, CHUNK_END, PARENT, ROOT = 1, 2, 4, 8


class B3:
    def __init__(self, W=32, BB=8, rots=(16, 12, 8, 7), rounds=2):
        self.W, self.BB, self.rots, self.rounds = W, BB, rots, rounds
        self.MASK = (1 << W) - 1
        self.IV = tuple(x >> (32 - W) for x in IV32)
        self.BPW = W // BB
        assert 16 * self.BPW == 64

    def _ror(self, value, count):
        return ((value >> count) | (value << (self.W - count))) & self.MASK

    def _g(self, v, a, b, c, d, x, y):
        M, r = self.MASK, self.rots
        v[a] = (v[a] + v[b] + x) & M
        v[d] = self._ror(v[d] ^ v[a], r[0])
        v[c] = (v[c] + v[d]) & M
        v[b] = self._ror(v[b] ^ v[c], r[1])
        v[a] = (v[a] + v[b] + y) & M
        v[d] = self._ror(v[d] ^ v[a], r[2])
        v[c] = (v[c] + v[d]) & M
        v[b] = self._ror(v[b] ^ v[c], r[3])

    def _compress(self, cv, words, counter, block_len, flags, rounds=None):
        rounds = self.rounds if rounds is None else rounds
        M = self.MASK
        v = list(cv) + list(self.IV[:4]) + [counter & M, counter >> self.W, block_len & M, flags & M]
        m = list(words)
        for _ in range(rounds):
            self._g(v, 0, 4, 8, 12, m[0], m[1])
            self._g(v, 1, 5, 9, 13, m[2], m[3])
            self._g(v, 2, 6, 10, 14, m[4], m[5])
            self._g(v, 3, 7, 11, 15, m[6], m[7])
            self._g(v, 0, 5, 10, 15, m[8], m[9])
            self._g(v, 1, 6, 11, 12, m[10], m[11])
            self._g(v, 2, 7, 8, 13, m[12], m[13])
            self._g(v, 3, 4, 9, 14, m[14], m[15])
            m = [m[i] for i in PERMUTATION]
        return tuple(v[i] ^ v[i + 8] for i in range(8)) + tuple(v[i + 8] ^ cv[i] for i in range(8))

    def _words(self, block):
        blk = list(block) + [0] * (64 - len(block))          # zero filled only for word loading
        return tuple(sum(blk[i * self.BPW + j] << (self.BB * j) for j in range(self.BPW)) for i in range(16))

    def _chunk_output(self, chunk, counter):
        cv = self.IV
        last_offset = max(0, (len(chunk) - 1) // 64 * 64)
        for offset in range(0, last_offset + 1, 64):
            block = chunk[offset:offset + 64]
            flags = CHUNK_START if offset == 0 else 0
            words = self._words(block)
            if offset == last_offset:
                return cv, words, counter, len(block), flags | CHUNK_END
            cv = self._compress(cv, words, counter, 64, flags)[:8]

    def _parent_output(self, left, right):
        return self.IV, left + right, 0, 64, PARENT

    def blake3(self, data):
        """Root output words 0..7 (the digest), for a list of byte values."""
        chunk_count = max(1, (len(data) + 1023) // 1024)
        stack = []
        for counter in range(chunk_count - 1):
            output = self._chunk_output(data[counter * 1024:(counter + 1) * 1024], counter)
            cv = self._compress(*output)[:8]
            total = counter + 1
            while total & 1 == 0:
                cv = self._compress(*self._parent_output(stack.pop(), cv))[:8]
                total >>= 1
            stack.append(cv)
        output = self._chunk_output(data[(chunk_count - 1) * 1024:], chunk_count - 1)
        while stack:
            output = self._parent_output(stack.pop(), self._compress(*output)[:8])
        cv, words, _, block_len, flags = output
        root_words = self._compress(cv, words, 0, block_len, flags | ROOT)
        return tuple(root_words[:8])

    def last_chunk_cv(self, data):
        """CV of the last chunk of data (non-root), as the organizer's code computes it inside blake3()."""
        chunk_count = max(1, (len(data) + 1023) // 1024)
        output = self._chunk_output(data[(chunk_count - 1) * 1024:], chunk_count - 1)
        return tuple(self._compress(*output)[:8])


def toy8():
    return B3(W=8, BB=2, rots=(4, 3, 2, 1))


def selftest(n=24, seed=5):
    import blake3_ref as ref
    import struct
    T = B3()
    rng = random.Random(seed)
    lens = [0, 1, 55, 63, 64, 65, 1023, 1024, 1025, 1079, 1087, 2048, 2103, 3127, 4096, 5000] + \
           [rng.randrange(0, 9000) for _ in range(n - 16)]
    ok = 0
    for L in lens:
        d = bytes(rng.randrange(256) for _ in range(L))
        mine = struct.pack('<8I', *T.blake3(list(d)))
        ok += mine == ref.blake3(d, rounds=2)
    return ok, len(lens), max(lens)


if __name__ == '__main__':
    ok, n, mx = selftest()
    print(f'selftest W=32: blake3_toy == blake3_ref (organizer copy, rounds=2) on {ok}/{n} messages, lengths 0..{mx}')
