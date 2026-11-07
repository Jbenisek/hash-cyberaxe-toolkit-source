"""verify_separable_1/cost.py - literal cost accounting for the separable claim (fixed variant, F = 4).

Contest model: 1 unit per 2-round compression, 1/430 unit per other 32-bit word op, memory free.
Word-op counts per primitive solve (DERIVED from the equation forms): t=u+v+w -> 2 ops (either direction);
t=u+v -> 1; t=(u^v)>>>r -> 2 (forward xor+rot, backward rotl+xor); out xor -> 1.
Inputs COMPUTED elsewhere: max closure of 4 guesses = 25 words (vs.c stats, matches separable R1).
"""
from math import log2, exp

OPS = 430.0


def lg(x):
    return log2(x)


def side_entry_ops(guesses=4, closure=25, keys=3):
    derived = closure - guesses          # words solved by propagation
    return guesses * 1 + 2 * derived + 2 * keys + 4   # generate guesses, solve, keys, hash insert/probe


def member_units():
    # propagate the remaining words (<= 96 solves * 2 ops), then E1,E3 (2 G calls = 28 ops) + 4 xors, birthday insert;
    # charged conservatively as one full compression on top of the propagation
    return (2 * 96 + 4) / OPS + 1.0


def two_list(kX, members_log=64.0, entry_ops=None, unit_per_entry=False):
    # balanced lists: x + y - 32 kX = members_log  ->  x = y = (members_log + 32 kX) / 2
    x = (members_log + 32 * kX) / 2
    c = 1.0 if unit_per_entry else (entry_ops or side_entry_ops(keys=kX)) / OPS
    total = 2 * 2 ** x * c + 2 ** members_log * member_units()
    return x, lg(total)


def main():
    print("COLLISION PROBABILITY with 2^m members on 128 bits (DERIVED, 1-exp(-N^2/2^129)):")
    for m in (64.0, 64.5, 65.0):
        print(f"  m={m}: P={1 - exp(-2 ** (2 * m) / 2 ** 129):.3f}")
    e = side_entry_ops()
    print(f"\nLIST ENTRY (4 guesses, closure <= 25 words, 3 keys): {e} word ops = {e / OPS:.3f} unit = 2^{lg(e / OPS):.2f}")
    print(f"MEMBER: {member_units():.3f} units (propagation + one compression, conservative)\n")
    print("TWO-LIST, p=0, iA=iB=0 (claim's structure):")
    for kX in (2, 3):
        for m in (64.0, 64.5):
            x, t_unit = two_list(kX, m, unit_per_entry=True)
            x, t_lit = two_list(kX, m)
            print(f"  kX={kX} members 2^{m}: lists 2^{x:.2f} each; total 2^{t_unit:.2f} at 1 unit/entry "
                  f"(claim's convention), 2^{t_lit:.2f} literal word-op count")
    print("\nUNBALANCED CHECK (kX=3, literal): cost vs x (y = 160 - x):")
    for x in (72, 76, 80, 84):
        y = 160 - x
        c = side_entry_ops() / OPS
        print(f"  x={x} y={y}: 2^{lg(2 ** x * c + 2 ** y * c + 2 ** 64 * member_units()):.2f}")
    print("\nMULTI-LEVEL TREES ON AN 8-WORD BASIS (4 checks), literal, DERIVED counting:")
    c = side_entry_ops(guesses=2, closure=14, keys=2) / OPS     # 2-guess closure <= 14 words (separable R1)
    mid = side_entry_ops(guesses=4, closure=50, keys=2) / OPS
    # 3 lists, keys (2,2): L1=L2=L3=2^64, L12 = 2^(128-64) = 2^64, members 2^(128-64) = 2^64
    t = 3 * 2 ** 64 * c + 2 ** 64 * mid + 2 ** 64 * member_units()
    print(f"  3 lists, keys 2 then 2: lists 2^64, mid 2^64, members 2^64 -> 2^{lg(t):.2f}")
    # 4 lists, keys (1,1,2): leaves 2^48, mids 2^64 each, members 2^64
    t = 4 * 2 ** 48 * c + 2 * 2 ** 64 * mid + 2 ** 64 * member_units()
    print(f"  4 lists, keys 1,1 then 2: leaves 2^48, mids 2^64, members 2^64 -> 2^{lg(t):.2f}")
    # two-list with 4 keys (separable's |S|=8 bound)
    x, t = two_list(4, 64.0, unit_per_entry=True)
    print(f"  2 lists, 4 keys: lists 2^{x:.0f} -> 2^{t:.2f} (separable's >= 2^97 bound holds only for two lists)")


if __name__ == "__main__":
    main()
