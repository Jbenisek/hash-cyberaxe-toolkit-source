import json
from eng import GCALLS, PERM
def sim(state_diff, msg_diff, absorb_cols, rounds=3):
    """Conservative word-level activity: a G call is active if any of its 4 state inputs or 2 message inputs differs; then all 4 outputs differ.
    Exception: a call in absorb_cols whose only state-difference input is d (the structural word) and whose two message words both differ is exactly cancelled (Lemma L), outputs clean."""
    st = [0]*16
    for i in state_diff: st[i] = 1
    m = [0]*16
    for i in msg_diff: m[i] = 1
    calls_active = []
    for r in range(rounds):
        n = 0
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2*j], m[2*j+1]
            ins = [st[a], st[b], st[c], st[d]]
            if j in absorb_cols and r == 0 and ins == [0, 0, 0, 1] and x and y:
                for k in (a, b, c, d): st[k] = 0
                continue
            if any(ins) or x or y:
                n += 1
                for k in (a, b, c, d): st[k] = 1
        calls_active.append(n)
        m = [m[i] for i in PERM]
    dig = sum(1 for i in range(8) if st[i] or st[i+8])
    return calls_active, dig
R = {}
R["d21_flags_no_absorb"] = sim([15], [], set())
R["d21_flags_absorb_m6m7"] = sim([15], [6, 7], {3})
R["d22_len_absorb_m4m5"] = sim([14], [4, 5], {2})
R["d22_len_flags_absorb_m4to7"] = sim([14, 15], [4, 5, 6, 7], {2, 3})
R["d22_len_flags_no_absorb"] = sim([14, 15], [], set())
# rounds 1 and 2 for comparison
R["d21_absorb_r1"] = sim([15], [6, 7], {3}, 1); R["d21_absorb_r2"] = sim([15], [6, 7], {3}, 2)
print(json.dumps(R)); json.dump(R, open("exp_d1c_out.json", "w"), indent=1)
