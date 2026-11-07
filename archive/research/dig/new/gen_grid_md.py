#!/usr/bin/env python3
"""gen_grid_md.py - writes the Pareto-row question template + per-row status grid into GRID_POSEIDON.md (new) and appends a delimited section to
GRID_BLAKE3.md / GRID_SHA256.md / GRID_SHA3.md.  Reads new/*.jsonl (made by gen_new_cells.py).  Re-runnable: the appended section sits between
the markers <!-- PARETO-ROWS BEGIN --> and <!-- PARETO-ROWS END -->; on a re-run the old section is replaced.
NOTE: build_blake3_grid.py / build_sha_grid.py / build_sha3_grid.py regenerate their GRID file from scratch and would drop this section; re-run this script after them.
"""
import json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_new_cells as G

HERE = G.HERE
DIG = G.DIG
SYM = {'BEDROCK': 'B', 'COMPUTED': 'C', 'SAMPLED': 'S', 'LOCAL_ONLY': 'L', 'CLAIMED-UNTESTED': 'U', 'KILLED': 'K', 'OPEN': 'O'}
BEG, END = '<!-- PARETO-ROWS BEGIN -->', '<!-- PARETO-ROWS END -->'

INTRO = {
    'blake3': 'BLAKE3 Pareto rows r3..r7 (rolled r5/r6/r7 lines and the 5-byte compact lines; r3/r4 straight). The older two-round quarter-step grid above (D172) covers blake3-r2 only.',
    'sha256': 'SHA-256 Pareto rows r39..r64 (straight bit-sliced S256Rn, rolled roll2/roll3/roll4, 5-byte u5 line). The older grids above cover the exploratory characteristic rows r37/r38 only; r39 and r64 had a handful of door cells in CELLS.jsonl (hash sha256-39, sha256-64).',
    'sha3': 'SHA3-256 Pareto rows r6..r24 (LS1 v3/v4 linear-structure line r7..r22, generic v3/v4b rows r9..r24). The older grids above cover the exploratory sha3-r5 / sha3-r6 characteristic tracks; Pareto r7 had door cells (hash sha3-r7). Pareto r6 has no filing yet.',
    'poseidon-generic': 'Poseidon generic collision rows r3..r56 (rho route2c/2d2 template, factory research/rows_1016/factory/posgen_route*). Orchard P128Pow5T3, r = number of partial rounds; 8 full rounds (0..3 and 60..63 in the filed numbering) around r partial rounds.',
    'poseidon-algebraic': 'Poseidon algebraic rows r3..r21: two free rounds on a line, odd part g of degree m=(5^(6+r)-1)/2, Euler-exponent powering by Barrett squarings on NTTs, half-gcd root certificate (research/poseidon/algebraic_paper/ledger.py).',
}


def load(fam):
    p = os.path.join(HERE, fam + '.dug.jsonl')
    if not os.path.exists(p):
        p = os.path.join(HERE, fam + '.jsonl')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def qs(fam):
    return G.QCORE + G.QFAM[fam]


def section(fam):
    cells = load(fam)
    spec = G.FAMS[fam]
    Q = qs(fam)
    out = []
    out.append('## Pareto-row questions: %s' % spec['title'])
    out.append('')
    out.append('Generated 2026-10-17 by `research/dig/new/gen_new_cells.py` + `gen_grid_md.py` (cells in `research/dig/new/%s.jsonl`, merged into CELLS.jsonl 2026-10-17). %s' % (fam, INTRO[fam]))
    out.append('')
    out.append('Each row is its own dig site with the same needs as the older sites: ledger, memory, packing, success slack, premise, preprocessing, rival, levers, judge findings, neighbour transfer, structure. Fourteen questions per row (Q1..Q12 shared by all families, Q13/Q14 family specific). Cell ids are `PR-%s-r<R>-<Qn>`; hash field is `%s-r<R>`.' % (fam, spec['hash']))
    out.append('')
    out.append('### The question template')
    out.append('')
    out.append('| Q | name | question (R = round count) |')
    out.append('|---|---|---|')
    for qk, name, text in Q:
        out.append('| %s | %s | %s |' % (qk, name, text.replace('{R_minus}', 'R-1').replace('{R_plus}', 'R+1').replace('{R}', 'R').replace('{HASH}', fam).replace('|', '/')))
    out.append('')
    out.append('Status rule (SCHEMA.md): a cell is filled (BEDROCK / COMPUTED / LOCAL_ONLY / KILLED) only where one of OUR files records the number, with its evidence path; everything else is OPEN. LOCAL_ONLY = the file answers a neighbouring or sampled row, or an extrapolation the author did not run on this row. Q8 and Q10 are filled from the board snapshot and FILINGS.md for every row (an empty square is recorded as a fact: no rival entry, no filing). Every new cell carries `peak_mem` (UNKNOWN unless a file states it).')
    out.append('')
    out.append('### Row x question grid (B bedrock, C computed, L local-only, O open)')
    out.append('')
    out.append('| row | ' + ' | '.join(q[0] for q in Q) + ' | filings | best rival on board | our best on board |')
    out.append('|---|' + '---|' * len(Q) + '---|---|---|')
    byrow = collections.defaultdict(dict)
    for c in cells:
        byrow[c['row_i']][c['id'].rsplit('-', 1)[1]] = c['status']
    for R in spec['rows']:
        ours, riv = G.rival_line(fam, R)
        mine = G.MY[fam].get(R, [])
        out.append('| r%d | ' % R + ' | '.join(SYM[byrow[R][q[0]]] for q in Q) + ' | %d | %s | %s |' % (
            len(mine), ('%s %s %s' % (riv[0]['user'], riv[0]['id'], riv[0]['score'])) if riv else 'none', ('%s %s' % (ours[0]['id'], ours[0]['score'])) if ours else 'none'))
    out.append('')
    cnt = collections.Counter(c['status'] for c in cells)
    out.append('Totals: %d rows, %d cells; %s.' % (len(spec['rows']), len(cells), ', '.join('%s %d' % (k, cnt[k]) for k in ['BEDROCK', 'COMPUTED', 'SAMPLED', 'LOCAL_ONLY', 'CLAIMED-UNTESTED', 'KILLED', 'OPEN'] if cnt[k])))
    out.append('')
    return '\n'.join(out)


POS_HEAD = """# GRID_POSEIDON - Poseidon Pareto row dig (generic part and algebraic part)

Created 2026-10-17. Before this file the dig held Poseidon only as the exploratory rows r1/r2 (hash poseidon-r1, poseidon-r2: round x lane x layer x Q1..Q4, universe group PO in coverage.py) and a few door cells for r3/r4/r5. The Pareto rows r3..r56 had no grid. Each Pareto row is its own dig site: a row r is a Poseidon with r partial rounds (Orchard P128Pow5T3: 3 lanes, x^5 S-box, 8 full rounds); the generic collision line and the algebraic line are two different attacks on the same row and are dug separately here.

Status letters follow SCHEMA.md (B BEDROCK, C COMPUTED, L LOCAL_ONLY, O OPEN). Evidence is by path. Rival rows are read as data from the board snapshot only.

## Part 0 - the two attack structures (what a row is made of)

| item | generic line (rho / route2c, route2d2) | algebraic line (line restriction) |
|---|---|---|
| idea | birthday-type collision search over the partial-round state form with two free rounds spent on making lanes 1,2 offset-free; distinguished points, table in 2^20 bytes | restrict the input to a line, the digest becomes a polynomial of degree m=(5^(6+r)-1)/2 in the line parameter; find collisions via S^((p-1)/2) mod g (Euler-exponent powering), then half-gcd for roots |
| unit of cost | field ADD+MUL ops in the step; step = 140 + 12r ops (partial round 12 = 3 + 4M + 5A; four full-round layers 6M+6A+3; entry 12 / exit 7 of the partial form; hidden-basis cut saves 4) | stages A..I in ledger.py: NTT (2^a or 3*2^a), Barrett squarings, half-gcd; K trials charged |
| score shape | S*(N+3.75), S = 1.393*2^127; about 126.2-126.8 for rows 7..56 (route2d2 staged ~126.23-126.30; filed route2 126.71-126.81) | r3 38.6, r4 42.9, r5 47.1, r6 52.8, r7 58.07, r8 62.36 (ledger K=1/K=2); modelled r9..r21 up to ~124; cross-over with generic at r21/r22 |
| memory | 2^20 bytes table + code (memory term 0) | tens of GB to 2^70 B: memory term max(0, mem_log2 - 20) dominates from r5 |
| binding risk | premise H1 (average over rho0), finite preprocessing statement (H2), 10-bit walk statement | per-trial success bound (plane genus bound r<=7; complete-intersection bound of Grok 134 for 8..11), coin draws vs probability space, lane_experiments evidence |
| sources | research/levers_1016/dig_posgen, research/rows_1016/factory/posgen_route* | research/poseidon/algebraic_paper/ledger.py, levers_1016/pos_alg_rows, r7alg_refile, posledger, pos_memcut, pos_far_rows |

"""


def pos_file():
    out = [POS_HEAD]
    out.append('## Part 1 - generic Poseidon rows (route2c / route2d2)\n')
    out.append(section('poseidon-generic').split('\n', 1)[1])
    out.append('\n## Part 2 - algebraic Poseidon rows (line restriction + powering + half-gcd)\n')
    out.append(section('poseidon-algebraic').split('\n', 1)[1])
    out.append('\n## Part 3 - empty squares recorded at creation\n')
    out.append('- Generic r3..r6: no row built (algebraic is 80+ bits better); recorded in the Q12 cells.')
    out.append('- Generic r7..r56 rival column: the board holds no rival entry on most of these rows (see the grid column "best rival on board"); a rival may appear any time.')
    out.append('- Algebraic r9..r21: modelled only (Grok 129 abstract model with our unit mapping), no C program and no filing; LOCAL_ONLY cells say so.')
    out.append('- Algebraic r8 is staged (pos_posalg_r8b) and not filed; r3..r7 are filed (POSR3E/F/G/H, POSR4M, POSR5M/T/U, POSR7ALG*).')
    out.append('')
    return '\n'.join(out)


def append_section(path, fam):
    txt = open(path, encoding='utf-8', errors='replace').read()
    if BEG in txt:
        txt = txt.split(BEG)[0].rstrip('\n') + '\n'
    block = '\n' + BEG + '\n' + section(fam) + '\n' + END + '\n'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt + block)


if __name__ == '__main__':
    with open(os.path.join(DIG, 'GRID_POSEIDON.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(pos_file())
    append_section(os.path.join(DIG, 'GRID_BLAKE3.md'), 'blake3')
    append_section(os.path.join(DIG, 'GRID_SHA256.md'), 'sha256')
    append_section(os.path.join(DIG, 'GRID_SHA3.md'), 'sha3')
    print('ok')
