
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
D = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G05-U07')
EV = 'research/dig/incoming2/blake3-r2-G05-U07/work/'
VAL = (' Own reference b3.py validated first: BLAKE3("") at 7 rounds = af1349b9...3262 (match), 200/200 random compressions equal to the '
       'organizer verifier _compress at rounds 1, 2, 7; record C3 pin numbers (BLAKE3_2ROUND_MAP 2.2) replayed exactly.')


def rec(cell, obj, q, labels, status, number, ev, notes):
    r = dict(hash='blake3-r2', row_i=None, row_j=None, object=obj, question=q, labels=labels, status=status,
             number=number, source='our workflow: scan-once-wave2', own_test=True, evidence=ev, date='2026-10-12',
             lever=False, gain_bits=None, notes=notes + ' universe cell ' + cell + '.' + VAL)
    r['topic'] = cell
    fn = os.path.join(D, cell.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w', encoding='utf-8'), indent=1)
    return fn


CAV = ('MODEL CAVEAT: k = 4 assumes each dirty round-1 column call can have its two outputs going to one E group cleaned for free '
       'by the X pins (demonstrated only for the length line by the record numbers, replayed exactly); the other lines are NOT constructed.')

rec('blake3-r2|MODE.single|MODE|Q2',
    'single-block root host (IV, t=0, flags 11, b<=64): is it needed for the length cancellation',
    'Is the single-block root host necessary for Lemma L (round-0 length cancellation), or does the cancellation hold at any host? Relax IV / t=0 / flags / root and recount.',
    ['I', 'Z'], 'COMPUTED',
    'Lemma L state-after-round-0 identical in 83,200 of 83,200 trials (all 65*64 = 4,160 ordered pairs b != b2 in 0..64, 20 random hosts each: random non-IV h, random t_lo/t_hi, random flags); changed message words always within {w4,w5}. Algebraic identity checked; the honest-byte padding rule is NOT part of this test.',
    EV + 'lines.py, lines_out.txt, check2.py, check2_out.txt, validate_out.txt',
    'Result: single-block root, IV, counter 0 and flags 11 are NOT necessary for the K2 cancellation; it works at any h, t, flags (the only requirement is a v14 difference, i.e. a LAST block with b<64 on one side). What the root host adds is only that the digest equals the CV directly (a non-root last block gives the same 8 words v[i]^v[i+8]; the other 8 output words are not in the 32-byte digest). No gain: the relaxed hosts are the counter/CV hosts already priced (door 37, 0.007-0.1 bit). Honest zero-pad byte count was not recounted. Pin necessity (X3,X7,X11,X15,w4,w13) not re-derived; only the record values were replayed (Y3 8127c181/7edf3e7e, Y11 7af77f38/850000c3, d bbfbdffe, b 76f7aefd all equal).')

rec('blake3-r2|MODE.single|MODE|Q4',
    'single-block root host: alternatives (other cancellable host lines)',
    'Which other round-0-cancellable difference lines exist (t_lo, t_hi, b, flags, CV row a h0..h3), alone and combined, and what do they leave after round 1?',
    ['I', 'Z'], 'COMPUTED',
    'Over all 255 nonempty subsets of the 8 lines {t_lo,t_hi,b,flags,h0,h1,h2,h3}: model residual k = 4 digest words in 191 subsets, k = 8 in 64, none below 4 (0 of 255). Dirty-round-1-call prediction held in 8,160 of 8,160 call checks (0 violations). Length line b alone: changed {w4,w5}, leaves words {1,3,4,6}, 1 dirty column call. Mirror lines: t_lo alone leaves {0,2,5,7} (1 call); flags alone leaves {0,2,5,7} with 2 dirty calls; t_hi alone 2 calls; b+flags leaves {1,3,4,6} with 3 dirty calls; t_lo with b gives k = 8.',
    EV + 'lines.py, lines_out.txt, lines_table.json, check2.py, check2_out.txt, pc.c, pc_single.txt',
    CAV + ' Dirty sets themselves are exact. At a single-block root only b (and flags only against a parent root, whose words are CVs, not free) is available since t = 0 and h = IV, so the alternatives need other tree shapes (doors 5, 23). Matches the four-checks theorem (k >= 4); none beats it. Side measurement: 40-bit partial-collision counts on 2^26 single-block-root-style blocks (b 55, flags 11, 2 rounds), four digest-word subsets: ratio to expected 0.989 to 1.029 (z -0.5 to 1.3), control 0.991; no structure.')

rec('blake3-r2|MODE.first|MODE|Q1',
    'first block of multi-block chunk (h=IV, flags 1, b=64): condition count / door 45 224-bit near-collision',
    'As used by door 45 (a 224-bit near-collision on the first block, claimed ~2^64): what is the condition count at this host, and does the 2-round first-block map show partial-collision structure that makes 224 bits cheaper than birthday?',
    ['Z'], 'SAMPLED',
    '2^26 random first blocks (h=IV, t=0, b=64, flags=1, 2 rounds), 40-bit digest-word keys: expected 2048 +- 45 colliding pairs; observed ratios {w0,w2,w5.lo8} 1.0195, {w1,w3,w4.lo8} 0.9907, {w0,w1,w2.lo8} 1.0195, {w6,w7,w5.lo8} 0.9775, uniform control 1.0156 (z -1.0 to 0.9). Excess below about 4.4 percent (2 sd) at 40 bits = under 0.07 bit; no bias. 224 bits = 7 words: generic birthday 2^112.',
    EV + 'pc.c, pc_first.txt, validate_out.txt',
    'At a first block of a same-position pair every v-line (t, b, flags, h) is identical, so the difference is message-only and no round-0 cancellation line exists; the 224-bit condition (7 of 8 CV words equal) has no cheap source found. The 2^64 figure of door 45 is DERIVED and we did not find or test its derivation; from 2^112 it would need a 2^48 advantage and a 40-bit partial-collision count shows none (it cannot rule out structure that appears only at wider widths). Door 45 stays CLAIMED-UNTESTED for its number; this record is a sampled null on the structure. Not closed.')

rec('blake3-r2|MODE.first|MODE|Q2',
    'first block host h = IV: is the fixed IV needed',
    'Is h = IV (first block) necessary, or does relaxing it (later blocks, free h) open round-0-cancellable lines, and which?',
    ['I'], 'COMPUTED',
    'Free h opens exactly the CV row a (h0..h3): each is cancelled in round 0 by one message word (h0 by w0, h1 by w2, h2 by w4, h3 by w6; a pure row-a line changes only that word). All 15 nonempty subsets of {h0..h3}: identical state after round 0, residual k = 4, words {0,2,5,7}. Row b (h4..h7): NOT cancellable by the same step, 20,000 of 20,000 trials the b output of the column call still differs after fixing a1.',
    EV + 'lines.py, lines_out.txt, lines_table.json, t3.py, t3_out.txt',
    'So h = IV removes four cancellation lines (row a) that a later block or a chosen CV would offer; that is the CV route (R1V family) whose price is the prefix near-collision (doors 45, 37). The row-b claim is one-step algebra only (no other cancellation method tried). ' + CAV)

rec('blake3-r2|MODE.first|MODE|Q3',
    'first block of multi-block chunk: degrees of freedom of a cancelling pair (exact count over carries)',
    'How many message pairs does a round-0-cancelling first-block pair have, counted exactly over the carries of the cancellation formula?',
    ['I'], 'COMPUTED',
    'The map m -> m2 (partner words mx2 = (a1 ^ dxor) - a2 - b, my2 = my + a1 - a1p, all mod 2^32) is a bijection for each (host, alt host): involution check back(m2) = m failed 0 of 100,000 random line subsets/hosts. So exactly 2^512 pairs per alt host at compression level, no carry loss. With the zero-pad rule for a b2-byte single-chunk partner (bytes b2..63 of m2 zero) the count is 2^(8*b2) pairs per alt host, b2 in 0..63, summed over b2 = 2^504.0056.',
    EV + 'lines.py, t3.py, t3_out.txt',
    'Compression-level count only: it does not assert a tree-consistent full-message collision (the first block output feeds block 2, so a first-block vs single-chunk pair is not a hash collision by itself). The pad-rule count is arithmetic from the bijection, not a separate enumeration.')

rec('blake3-r2|MODE.first|MODE|Q4',
    'first block of multi-block chunk: alternative hosts to pair it with',
    'Which pairing hosts for a first block (flags 1, b 64, t = chunk index) offer round-0 lines, and what do they leave?',
    ['I', 'Z'], 'COMPUTED',
    'Pairing a first block with a host differing in: t_lo alone k=4 {0,2,5,7} (1 dirty column call); t_hi alone k=4 (2 calls); t_lo+t_hi k=4; b+flags (single-block chunk flags 3 vs 1, b2<64) k=4 {1,3,4,6} (3 dirty calls); t_lo+b k=8; all four of t_lo,t_hi,b,flags k=8. No pairing gives k below 4 (0 of 255 subsets). Same-position pairs (same t, b=64, flags 1, h=IV): no line at all.',
    EV + 'lines.py, lines_out.txt, lines_table.json, t3.py, t3_out.txt, pc_first.txt',
    CAV + ' A pairing with a different chunk index or chunk shape is a different tree shape, so the whole-hash collision then needs the later blocks to agree (the 2^128 generic match of doors 5 and 23); not tested here. Door 45 sits here: its prefix pair would have to provide a row-a CV difference; see MODE.first Q1 and Q2.')
print('written')
