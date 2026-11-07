
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

import json, os
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U08')
W = D + r'\work'


def rd(f):
    try:
        return open(os.path.join(W, f)).read().strip()
    except Exception:
        return ''


e5 = rd('e5.out')
e6 = rd('e6.out')
e5t = e5.replace('\n', ' | ') if e5 else 'e5 (exhaustive 2^32 w4 sweep of the filed pin) did not finish in the time limit: NOT RUN TO COMPLETION'
e6t = e6.replace('\n', ' | ') if e6 else 'e6 (random pin density) did not finish: not run to completion'
EV = 'research/dig/incoming2/blake3-r2-G05-U08/work/ (b3m.py, e0_validate.py, e1_params.py, e2_channels.py, e3_lemmaH.py, e4_construct.py, e5_pinset.py, e6_density.py, e7_reads.py)'
COMMON = dict(hash='blake3-r2', row_i=None, row_j=None, source='our workflow: scan-once-wave2', own_test=True,
              evidence=EV, date='2026-10-12', lever=False, gain_bits=None)
V = 'Reference b3m.py validated first: 0 mismatches vs organizer verifier in 432 hashes (r=2 and r=7, lengths 0..199 plus chunk/tree boundaries) and empty r7 vector af1349b9. '
recs = {}


def add(cell, obj, q, labels, status, number, notes, **kw):
    r = dict(COMMON)
    r.update(object=obj, question=q, labels=labels, status=status, number=number,
             notes='universe cell %s. %s%s' % (cell, V, notes))
    r.update(kw)
    recs[cell] = r


MID = 'middle block of a multi-block chunk (flags 0, b 64, h = previous block CV)'
LAST = 'last block of a multi-block chunk (CHUNK_END, flags 2 or 10, h = previous block CV)'

add('blake3-r2|MODE.mid|MODE|Q1', MID, 'Value / difference / condition count at a middle block as used?', ['N', 'C'], 'COMPUTED',
    'Exhaustive over 3199 message lengths (85,003 organizer-verifier compressions at r=2): a mid block has exactly 1 value of b (64) and 1 of flags (0); t is the chunk index, h the previous CV. So the b (K2) and flags (K3) cancellation channels have 0 values at a mid block. Channels that exist: t_lo (K0), t_hi (K1), h a-slot words h0..h3 (K0..K3): each cancels to an IDENTICAL post-round-0 state X in 2000/2000 random pairs (exact), with 2 (t) or 1 (h) differing message words. Pin-compatible one: h2 additive -8 with w4 +8 (read only at C3.x): 3000/3000 same X; with the filed pins digest words 0,2,5,7 equal in 3000/3000 and 1,3,4,6 equal in 0/3000: 4 words forced, 128-bit residual, same as the length line. Cost of the host: previous-block CV pair differing only in h2 by exactly -8 (a 256-bit specified difference).',
    'Role of the word at this use: w4 pinned at W4, w13 pinned at W13, as in the single-block root. The mid block is a host for the h2 channel only if the previous block pair differs in CV by exactly (0,0,-8,0,0,0,0,0); generic birthday on that difference is about 2^128 compressions (DERIVED, not run); the 2^64 for a 224-bit near-collision quoted in door 45 is CLAIMED, not tested here. Not tested: pins for the t_lo/t_hi channels (none known).',
    topic='blake3.mode.mid.q1')
add('blake3-r2|MODE.mid|MODE|Q2', MID, 'Is the b-pair necessary at a mid block? Relax or replace it and recount the outcome mass.', ['K', 'N'], 'COMPUTED',
    'Replace: the length pair (55/63) cannot exist at a mid block (b=64 always, exhaustive over 3199 lengths); the h2 additive -8 pair replaces it. Generalized pin constructor (own transcription of pkgB3V steps O,M,Y,T with h, t, b, flags as host constants) built 3000/3000 mid hosts at random h,t,flags (forward round 0 hits X3,X7,X11,X15 exactly, w4=W4, w13=W13), and the pair (h2-8, w4+8) shares X and digest words 0,2,5,7 in 3000/3000. No bit-3 condition at the mid host (the h2 pair always gives w4 difference exactly +8). Outcome mass per host: constructed family 2^256 messages (8 free words, w14=w15=0); with w14,w15 free at a mid block at most 2^320 (DERIVED: 512 - 128 pins - 64 for w4,w13; not constructed).',
    'The replacement moves the price from the pin (free) to producing the previous-CV pair with the exact difference; no priced win.',
    topic='blake3.mode.mid.q2')
add('blake3-r2|MODE.mid|MODE|Q3', MID, 'Degrees of freedom at a middle block, exact count over carries.', ['C'], 'COMPUTED',
    'Constructed pinned family at a mid host: 8 free words = 2^256 messages per host (3000/3000 hosts built, w14=w15=0 as in the filed family); upper count 2^320 with all 16 words free (DERIVED). Carry count of the pin, exact sweep over all 2^32 values of w4 for the filed X pins (shifts +8, -8): ' + e5t,
    'Sweep output is verbatim from e5.out. The mid host uses shift +8 only.',
    topic='blake3.mode.mid.q3')
add('blake3-r2|MODE.mid|MODE|Q4', MID, 'Alternatives at a middle block (other channels, other hosts).', ['S', 'E'], 'COMPUTED',
    'Exact read table (PERM): t_lo -> C2.y,E0.x; t_hi -> C0.x,C1.x; b -> C3.x,E1.y; flags -> C0.y,C2.x; h0 -> C2.y; h1 -> C0.x; h2 -> C3.x; h3 -> C0.y. A Fact-P-type pin needs an x-difference only (a y-difference changes d in the same G). Single x-only channels: h1 (C0.x) and h2 (C3.x). h2 built and verified (3000/3000). h1 would leave Y0,Y8 dirty and clean words 1,3,4,6, residual 0,2,5,7: same size, DERIVED, not built. Random-pin density: ' + e6t,
    'Door 37 (fresh CV per context): the constructor builds hosts for ANY h, t, flags (3000/3000), so the filed pin transfers with no h7 or IV condition; a free h at a last block needs only bit3(h2+h6+W4)=0. That supports the claim that the frame is cheap. Door 37 RELABEL (ledger stack of all measured levers) NOT run here; it is not among this unit cells.',
    topic='blake3.mode.mid.q4')
add('blake3-r2|MODE.last|MODE|Q1', LAST, 'Value / difference / condition count at a last block as used?', ['N', 'C'], 'COMPUTED',
    'Exhaustive over 3199 lengths (organizer verifier, r=2): last block has 64 values of b (1..64), flags in {2,10}, t in {0,>=1}, h always a CV (129 classes). Channels K2 (b), K3 (flags 2<->10), K0/K1 (t) each cancel to identical X in 2000/2000. End to end through the verifier: 900 real pairs (P||A55 vs P||B63, P of 1 or 3 blocks; single chunk flags 10, or last chunk of a 2-chunk message t=1 flags 2): same X after round 0 in 900/900, honest bytes 900/900, own hash = verifier hash for all 1800 messages. Pin constructor on 3000 random hosts (h,t,flags in {0,2,10,3}): digest words 0,2,5,7 equal in 1509/1509 hosts with bit3(h2+h6+W4)=0 and in 0/1491 with bit3=1 (W4\' = W4-8, Fact P does not apply). Condition count = the filed 4 forced words, residual 128 bits, on half of the hosts.',
    'The two uses of w4 and w13 agree with the single-block root (pinned W4, W13). Fraction of random h with the filed pin valid: 499,739/1,000,000 (bit 3 of K+W4, K=h2+h6).',
    topic='blake3.mode.last.q1')
add('blake3-r2|MODE.last|MODE|Q2', LAST, 'Are IV, flags 11, t=0, CHUNK_START necessary for the length-pair construction? Relax and recount.', ['K', 'N'], 'COMPUTED',
    'None is necessary: the construction transfers to any h, t, flags (3000/3000 hosts built, forward pins exact). Only host condition found: bit 3 of K+W4 = 0 (K=h2+h6), exactly 1/2 of hosts (measured 0.4997). Hosts with bit 3 = 1 fail the filed pin (0/1491) and need a shift -8 pin or a new W4. Outcome mass per admissible host: 2^256 messages (8 free words), same as the single-block root family; a free h gives a new host per prior-block compression (random draw, not chosen). Sweep for the pins: ' + e5t,
    'Not tested: whether the class rate 2^-91.126 depends on h (door 37 note says rate independent of cv, R18, not retested).',
    topic='blake3.mode.last.q2')
add('blake3-r2|MODE.last|MODE|Q3', LAST, 'Degrees of freedom at a last block, exact count over carries.', ['C'], 'COMPUTED',
    'Per admissible host 2^256 constructed messages (3000/3000 built; honest-byte constraints w14=w15=0, top byte of w13 = 0 hold for A and B). Carry facts: w4 -> w4\' = ((K+w4) XOR 8) - K is an involution in K+w4, a bijection of the 2^32 w4 values, +8 for exactly 2^31 of them; w5\' = w5 + w4 - w4\' is a second bijection. Pin sweep over all 2^32 w4: ' + e5t,
    'The family count is the constructor dimension (injective by construction), not an independent enumeration.',
    topic='blake3.mode.last.q3')
add('blake3-r2|MODE.last|MODE|Q4', LAST, 'Alternatives at a last block.', ['S', 'E'], 'COMPUTED',
    'Channels at a last block: b (K2, pin built), flags 2<->10 (K3 -> C0.y,C2.x, contains a y-difference so no Fact-P-type pin), t_lo, t_hi, h2 (C3.x). Other length pairs cancel exactly (b XOR 1,2,4,6,7,8: 2000/2000 each) but only the +/-8 pin was swept. Random-pin density: ' + e6t,
    'Prior records, not retested: other length pairs dead at +1.9 bits at best (Daydream 11); 56/64 ties 55/63. A multi-block prefix gives no structural advantage over a single block: hosts are equivalent.',
    topic='blake3.mode.last.q4')

for cell, r in recs.items():
    fn = cell.replace('|', '_') + '.json'
    json.dump(r, open(os.path.join(D, fn), 'w', encoding='utf-8'), indent=1)
    print(fn)
