"""ctr x join, part K: why screen-2 candidates die.

For every screen-2 candidate (U, V, surviving bits) of ctr_split_numeric.py, test each surviving
match bit b with 8 bases x 32 draws per side and record CROSS moves:
  V resample changes key1 bit b  or  U resample changes key3 bit b.
One cross move proves bit b is not split for that (U, V) (key1_b depends on V or key3_b on U).
Bits with no cross move are 'unrefuted'; for those, report how often key1_b and key3_b move at
all and P(key1_b == key3_b) over random trials (the most a join on that bit could save is
-log2 of that probability).
"""
import random
import sys
import time

import ctr_split_numeric as m


def main():
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    modes = sys.argv[2].split(',') if len(sys.argv) > 2 else ['C0', 'T0', 'T0T1', 'E1d1', 'E3h1']
    replay = len(sys.argv) > 3 and sys.argv[3] == 'replay'
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    log("W %d; screen2 bases=2 draws=6 (%s); cross test 8 bases x 32 draws (seed 5151)"
        % (W, "replay of ctr_split_numeric main stream: same screen-2 candidates" if replay
           else "independent replicate, seed 4040 straight after verify"))
    for mode in modes:
        t0 = time.time()
        w = m.WorldT(W, mode)
        rng = random.Random(4040)
        m.verify_t(w, rng, 40)
        if replay:   # consume the stream exactly as ctr_split_numeric.main() does before screen 2
            m.word_influence(w, rng, 6, 4)
            m.bitflip_report(w, rng, 2)
            m.axis_split_n(w, rng, 1, 2) if W == 32 else m.axis_split_n(w, rng, 2, 6)
        cands, ncand = m.axis_split_n(w, rng, 2, 6, keep=10 ** 6) if W == 32 else \
            m.axis_split_n(w, rng, 4, 24, keep=10 ** 6)
        rng2 = random.Random(5151)
        tot_bits = killed = 0
        unref = []
        for k, u_idx, v_idx, surv in cands:
            bits = [b for b in range(4 * W) if (surv >> b) & 1]
            cross = 0
            own1 = own3 = 0
            for _b in range(8):
                base = m.rand_free(rng2, W, w.nf)
                p1, p3, _, _ = m.keys(w, base)
                for _d in range(32):
                    alt = base[:]
                    for i in u_idx:
                        alt[i] = rng2.getrandbits(W)
                    q1, q3, _, _ = m.keys(w, alt)
                    cross |= p3 ^ q3          # U moving key3
                    own1 |= p1 ^ q1
                    alt = base[:]
                    for i in v_idx:
                        alt[i] = rng2.getrandbits(W)
                    q1, q3, _, _ = m.keys(w, alt)
                    cross |= p1 ^ q1          # V moving key1
                    own3 |= p3 ^ q3
            for b in bits:
                tot_bits += 1
                if (cross >> b) & 1:
                    killed += 1
                else:
                    unref.append((b, u_idx, v_idx, (own1 >> b) & 1, (own3 >> b) & 1))
        log("mode %s: screen2 candidates %d, candidate bits %d, refuted by a cross move %d, unrefuted %d (%.0fs)"
            % (mode, ncand, tot_bits, killed, len(unref), time.time() - t0))
        if unref:
            # match probability of each unrefuted bit over random trials
            rng3 = random.Random(6262)
            for b, u_idx, v_idx, o1, o3 in unref[:20]:
                same = 0
                n = 4000
                for _ in range(n):
                    p1, p3, _, _ = m.keys(w, m.rand_free(rng3, W, w.nf))
                    same += ((p1 ^ p3) >> b) & 1 == 0
                log("  unrefuted bit %d U=%s V=%s own-moves key1 %d key3 %d  P(key1_b==key3_b)=%.4f"
                    % (b, ",".join(w.names[i] for i in u_idx), ",".join(w.names[i] for i in v_idx),
                       o1, o3, same / n))
    name = "bit_kill_W%d%s.txt" % (W, "_replay" if replay else "")
    open(name, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    log("WROTE " + name)


if __name__ == "__main__":
    main()
