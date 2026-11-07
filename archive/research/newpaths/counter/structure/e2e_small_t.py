"""Complete messages for the arrangement with a SMALL counter: per outer step, run the inner chain backwards
from t = 1 .. TMAX (numpy), keep (outer step, t) whose c1 = Y11 + E1.d1 lies in the T1 cube, then build
P||A, P||B (P = t identical random chunks) and hash them with the organizer's blake3(.., 2).
Checks: the organizer digest equals the own root(stack, CV_t(last chunk)); the last chunks' CVs (counter t,
flags 3) agree on words 0,2,5,7; Y4, E1.d1, c1-in-cube, beta as in arrange_check.
usage: python -B e2e_small_t.py TMAX MAX_OUTER WANT SEED"""

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

import sys, struct, random, time
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import b3own as O
import arrange_check as AC

TMAX, MAXO, WANT, SEED = (int(a) for a in sys.argv[1:5])
rng = random.Random(SEED)
u = np.uint32
tt = np.arange(1, TMAX + 1, dtype=np.uint32)


def np_ror(x, n):
    return ((x >> u(n)) | (x << u(32 - n))).astype(np.uint32)


hits = []
t0 = time.time()
n_o = 0
for n_o in range(1, MAXO + 1):
    o = AC.outer(*[rng.getrandbits(32) for _ in range(7)], AC.sub_member(rng))
    K0a1 = u(AC.rol(o['K0d1'], 16)) ^ tt
    w0 = (K0a1 - u(AC.IV[0]) - u(AC.IV[4])).astype(np.uint32)
    Y2 = (u((o['C2a1'] + o['C2b1']) & AC.M) + w0).astype(np.uint32)
    Y14 = np_ror(u(o['C2d1']) ^ Y2, 8)
    Y10 = (u(o['C2c1']) + Y14).astype(np.uint32)
    Y6 = np_ror(u(o['C2b1']) ^ Y10, 7)
    a1 = (u((o['Y1'] + o['w12']) & AC.M) + Y6).astype(np.uint32)
    d1 = np_ror(u(o['Y12']) ^ a1, 16)
    c1 = (u(AC.Y11A) + d1).astype(np.uint32)
    idx = np.nonzero((c1 & u(AC.CUBE_MASK)) == u(AC.CUBE_VAL))[0]
    if len(idx):                      # one hit per outer step (diversity)
        j = idx[0]
        hits.append((o, int(d1[j]), int(tt[j])))
    if len(hits) >= WANT:
        break
print(f'outer steps scanned {n_o}, t range 1..{TMAX}: outer steps with a hit (t with c1 in the cube) {len(hits)}; '
      f'(hits per outer step expected {TMAX / 2048:.2f} on average); {time.time() - t0:.0f}s')
hits.sort(key=lambda h: h[2])
ok_all = 0
for o, d1, t in hits[:WANT]:
    ii, words = AC.inner(o, d1)
    assert ii['t'] == t
    chunk = bytes(rng.getrandbits(8) for _ in range(1024))
    P = chunk * t
    A = struct.pack('<16I', *words)[:55]
    wb = list(words); wb[4] = AC.W4B; wb[5] = (words[5] + AC.DELTA) & AC.M
    B = struct.pack('<16I', *wb)[:63]
    dA = V.blake3(P + A, 2); dB = V.blake3(P + B, 2)
    stack = O.stack_of_prefix([O.chunk_cv(chunk, i) for i in range(t)])
    trA, trB = {}, {}
    outA, stA = O.compress_full(O.IV, words, t, 55, 3, trace=trA)
    outB, stB = O.compress_full(O.IV, wb, t, 63, 3, trace=trB)
    cvA, cvB = tuple(outA[:8]), tuple(outB[:8])
    cvA_org = tuple(V._compress(*V._chunk_output(A, t, 2), 2)[:8])
    cvB_org = tuple(V._compress(*V._chunk_output(B, t, 2), 2)[:8])
    root_ok = dA == O.root_from_stack(stack, cvA) and dB == O.root_from_stack(stack, cvB)
    half = all(cvA[i] == cvB[i] for i in (0, 2, 5, 7))
    inner_ok = (stA['Y'][4] == o['y'] and trA['E1']['d1'] == d1 and (trA['E1']['c1'] & AC.CUBE_MASK) == AC.CUBE_VAL
                and (trA['E1']['b1'] ^ trB['E1']['b1']) == AC.BETA_T1 and stA['X'] == stB['X'])
    good = root_ok and half and inner_ok and cvA == cvA_org and cvB == cvB_org
    ok_all += good
    print(f't = {t}: |P||A| = {len(P + A)}, |P||B| = {len(P + B)}; organizer digest = root(stack, CV_t) {root_ok}; '
          f'CV words 0,2,5,7 equal {half}; Y4/E1.d1/cube/beta/X {inner_ok}; organizer CV = own {cvA == cvA_org and cvB == cvB_org}; '
          f'digests equal {dA == dB} (expected False)')
    print(f'   last chunk A: {A.hex()}')
    print(f'   last chunk B: {B.hex()}')
    print(f'   chunk (P = {t} copies): {chunk.hex()[:64]}...')
    print(f'   CV_t(A) = {" ".join(f"{w:08x}" for w in cvA)}')
    print(f'   CV_t(B) = {" ".join(f"{w:08x}" for w in cvB)}')
print(f'complete-message checks passed: {ok_all}/{min(WANT, len(hits))}')
