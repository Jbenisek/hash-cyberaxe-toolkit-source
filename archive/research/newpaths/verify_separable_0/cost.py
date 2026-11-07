"""verify_separable_0: literal cost ledger (1 unit per 2-round compression, 1/430 unit per other word op) for the
two-list join of the 'separable' claim.  Op counts per list entry are GUESSES stated below; everything else is
arithmetic.  members needed: 2^64 (128-bit birthday, ~39% success) or 2^64.5 (~63%).
"""
from math import log2


def ledger(kX, members_log2, ops_entry, ops_member_units=1.0, ops_birthday=8):
    # balanced lists, one core value (nu = 0), p = 0: x = y, 2x - 32 kX = members
    x = (members_log2 + 32 * kX) / 2
    lists = 2 * 2 ** x * ops_entry / 430          # build A, build B (+probe), per-entry word ops incl. memory
    mem = 2 ** members_log2 * ops_member_units      # finish each joined pair and compress it (<= 1 unit)
    bday = 2 ** members_log2 * ops_birthday / 430   # birthday table insert / compare
    tot = lists + mem + bday
    return x, log2(lists), log2(mem), log2(tot), log2(2 * 2 ** x)


print("claim's unit (one list entry = 1 unit): kX=3 ->", 33 + 16 * 3, " kX=2 ->", 33 + 16 * 2)
for kX in (2, 3, 4):
    for ops in (30, 55, 112, 430):
        for mem in (64, 64.5):
            x, L, M, T, E = ledger(kX, mem, ops)
            print(f"kX={kX} members=2^{mem} ops/entry={ops:3d}: lists 2^{x:.2f} each, entries 2^{E:.2f}, "
                  f"list cost 2^{L:.2f}, members 2^{M:.2f}, TOTAL 2^{T:.2f} units")
