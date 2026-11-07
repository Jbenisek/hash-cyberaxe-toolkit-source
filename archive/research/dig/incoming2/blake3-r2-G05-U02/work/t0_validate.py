"""T0: validate own reference on known answers, then the parametrised inverse against the reference compress."""
import sys, random, struct
sys.path.insert(0, '.')
from b3init import *
import warnings
warnings.simplefilter('ignore')
if __name__ == '__main__':
    _, o = my_compress(list(IV), [0]*16, 0, 0, 11, 7)
    d = b''.join(struct.pack('<I', x) for x in o).hex()
    print('own BLAKE3("") 7 rounds:', d)
    assert d == 'af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'
    print('verifier blake3(b"") 7 :', VB.blake3(b'', 7).hex())
    rng = random.Random(5)
    for rounds in (2, 7):
        for _ in range(300):
            L = rng.randrange(1, 65); msg = bytes(rng.getrandbits(8) for _ in range(L))
            words = struct.unpack('<16I', msg.ljust(64, b'\0'))
            _, o = my_compress(list(IV), words, 0, L, 11, rounds)
            assert b''.join(struct.pack('<I', x) for x in o) == VB.blake3(msg, rounds)
    print('own compress == verifier on 600 single-block messages (2 and 7 rounds)')
    rn = np.random.default_rng(1)
    def check(h, n=400, t=0, flags=3, tag=''):
        fr = rand_free(rn, n)
        w, wb, X, S = derive(h, PIN, fr, t=t, flags=flags)
        bad_x = bad_half = bad_res = 0
        res = tail(h, PIN, X, w, wb)
        for k in range(n):
            wa = [int(a[k]) for a in w]; wbb = [int(a[k]) for a in wb]
            v0, _ = my_compress(h, wa, t, PIN['len_a'], flags, 1)
            _, oa = my_compress(h, wa, t, PIN['len_a'], flags, 2)
            _, ob = my_compress(h, wbb, t, PIN['len_b'], flags, 2)
            if [int(x[k]) for x in X] != v0: bad_x += 1
            if not all(oa[i] == ob[i] for i in (0, 2, 5, 7)): bad_half += 1
            if tuple(oa[i] ^ ob[i] for i in (1, 3, 4, 6)) != tuple(int(r[k]) for r in res): bad_res += 1
        print(tag, 'n=%d  X-mismatch=%d  half-collision(words 0,2,5,7)-fail=%d  residual-mismatch=%d' % (n, bad_x, bad_half, bad_res))
    check(list(IV), tag='h=IV t=0 flags=3     ')
    check(list(IV), t=12345, flags=3, tag='h=IV t=12345 flags=3')
    check(list(IV), t=0, flags=11, tag='h=IV flags=11       ')
