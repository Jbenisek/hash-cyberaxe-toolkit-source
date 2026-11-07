# SHA3-256 tried/untried grids (r5 and r6), same cell format as negative_space/cells.csv. Writes sha3_cells.csv here;
# make_endgame.py draws it next to the BLAKE3 grids. Run: python -B sha3_grid.py
# Sources: research/SHA3R6_MAP.md, research/sha3r6/*, research/rivals/sha3_others_tried.md, FILINGS.md (pkgS5).
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))

FREE = ['msg', 'blk1', 'field', 'pad', 'cap', 'none']          # where the freedom comes from
LAYER = ['r1-2', 'r3', 'r4', 'r5', 'r6', 'all']                 # which rounds the method attacks
TRACK = ['r5', 'r6']
TECH = ['trail', 'conn', 'idiff', 'lin', 'deg', 'bday', 'tda', 'sat', 'cost']

# id  track free layer tech status(alive/dead/open)   -- ids are short descriptions (shown on hover)
REC = """
r5:connector+trail-route(GLL20-line,board-best-32.93,others) r5 msg r1-2 conn alive
r5:3round-trail-after-connector(others) r5 msg r3 trail alive
r5:pkgS5-internal-diff-99.57(ours,passed) r5 blk1 all idiff alive
r5:pkgS5-short-final-key(Astra) r5 blk1 r5 idiff alive
r5:rivals-internal-diff(11-refuted) r5 blk1 all idiff dead
r5:cadamcat-generalized-idiff(not-evaluable) r5 blk1 r1-2 idiff open
r6:leader-bitsliced-Gray-birthday-124.05(others) r6 msg all bday alive
r6:leader-linear-prefix-chi1-conditions(others) r6 msg r1-2 lin alive
r6:leader-round4-6-key-cones(others) r6 msg r4 cost alive
r6:idiff-plus-1-round-2^172(Grok55) r6 blk1 r6 idiff dead
r6:native-5r-family-to-6r->=130.15(Astra20) r6 blk1 all idiff dead
r6:first-block-break-at-r6(Astra20) r6 blk1 r1-2 idiff dead
r6:SHAKE128-3r-connector-transfer-2^206 r6 msg r1-2 conn dead
r6:3r-connector-exact-rank(unknown) r6 msg r1-2 conn open
r6:2r-linear-structure-35/40dim(+0.08max) r6 field r1-2 lin dead
r6:3r-structure-rank<=2(linstruct3,Astra22) r6 field r3 lin dead
r6:double-kernel-ISD-186dim-wt>=262 r6 field r3 lin dead
r6:fix-delta-in-35space-34cond(D17) r6 field r3 trail dead
r6:non-identity-chi-transitions-rank<=2(exhaustive-6bit,certified) r6 field r3 trail dead
r6:2-block-capacity-reshapes-r2-affinity(3r-field-dim1-at-random-caps) r6 blk1 r3 lin open
r6:idiff-x-lowdegree(deg-delta6>=15,symmetric-birthday>=2^187) r6 field all idiff dead
r6:per-plane-degrees-all-exactly-8(0-bit) r6 field r5 deg dead
r5:LOW-DEGREE-route-122.9881(D23,unfiled,premise-open) r5 field r5 deg alive
r6:cost-levers-packing/tables/abort/Hellman r6 none all cost dead
r6:Grok56-123.x-count-artefact r6 field all cost dead
r6:LOW-DEGREE-FES-pkgS6-FILED-e641788b-122.98920 r6 field r5 deg alive
r6:low-degree-deg16-rounds3-6-together-123.6 r6 field all deg alive
r6:low-degree-deg4-rounds3-4-hybrid-123.9/124.7 r6 field r4 deg dead
r6:low-degree-deg2-round3-only-125.05 r6 field r3 deg dead
r6:H_coset-prereg-2^30-digests-PASS r6 field all bday alive
r6:SAT-tail-search-after-2r-connector(weeks) r6 msg all sat open
r6:rounds4-5-kernel(SolCloud17) r6 field r4 lin open
r6:DDS-target-difference-alg+3r-trail(s3-tda-sat) r6 msg r1-2 tda dead
"""

IMP = {  # (grid, row, col) -> reason; rows/cols as in the axis lists
    'cap': 'capacity bits are 0 in a single block; they move only through a chosen first block (row blk1)',
    'pad': 'padding is fixed by the length; a length change is a last-block byte difference, already row msg',
    'none-tech': 'no freedom added: trails, connectors, structures and searches need free bits; only cost changes',
    'r1-2-deg': 'rounds 1-2 are already affine on the field (degree 1): nothing to lower',
    'field-conn': 'a connector solves for message bits; the field already fixes rounds 1-2 as affine (row msg)',
}

def build():
    recs = [l.split() for l in REC.strip().splitlines()]
    grids = [('SHA3 freextech', FREE, 2), ('SHA3 layerxtech', LAYER, 3), ('SHA3 trackxtech', TRACK, 1)]
    rows = []
    for gname, axis, col in grids:
        for r in axis:
            for t in TECH:
                hit = [x for x in recs if x[col] == r and x[4] == t]
                al = [x[0] for x in hit if x[5] == 'alive']; de = [x[0] for x in hit if x[5] == 'dead']
                op = [x[0] for x in hit if x[5] == 'open']
                why = ''
                if not hit:
                    if gname.endswith('freextech'):
                        if r in ('cap', 'pad'): why = IMP[r]
                        elif r == 'none' and t != 'cost' and t != 'bday': why = IMP['none-tech']
                        elif r == 'field' and t == 'conn': why = IMP['field-conn']
                    elif gname.endswith('layerxtech') and r == 'r1-2' and t == 'deg':
                        why = IMP['r1-2-deg']
                mark = ('tried-alive' if al else 'tried-dead' if de else 'untried' if not why else 'impossible')
                rows.append(dict(grid=gname, row=r, col=t, mark=mark, alive=' '.join(al), dead=' '.join(de),
                                 open_logged=' '.join(op), reason=why))
    with open(os.path.join(HERE, 'sha3_cells.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    n = {m: sum(r['mark'] == m for r in rows) for m in ('tried-alive', 'tried-dead', 'untried', 'impossible')}
    print('sha3_cells.csv:', len(recs), 'records,', n)

if __name__ == '__main__':
    build()
