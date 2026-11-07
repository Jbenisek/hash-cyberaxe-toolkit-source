from fractions import Fraction
from math import log2

# Self-contained exact ledger: integers and Fractions only; it imports no
# experiment source and reads no file.  The base total is 4efa18a8's governing
# total, which already charges every inherited row (A, B1, B2, C, D,
# development item 26, E1, E2).  Rows (a)-(c) are 39ff21c4's and 6938d3fb's,
# unchanged; (d) is 6938d3fb's row at the shipped key-word layout; (e) and (f)
# are new.  All row values are primitives (1355 per target unit).
RATE = 1355
P = 100000
DEN = 271000000000
base = Fraction(2126951589301705708573, DEN)
ACC = [0, 0, 3, 5, 5, 8, 9, 10, 10, 13, 17, 18, 19, 20, 24, 25, 26, 27, 31, 32, 33, 35, 36, 37, 39, 40, 43, 43, 44, 50, 56, 56, 73, 78, 83, 309, 321, 363, 386]
A = sum(min(i, 23) + 1 for i in ACC)
assert len(ACC) == 39 and A == 751
ATT = (1 << 20)*96 + (1 << 15)*512 + (1 << 22)

# (a) online connector coin words (time only)
online = 4268*((1 << 15) - 22150)*512
# (b) replay test: 751 executed attempts repriced, 185 unexecuted slots removed
replay = A*(((1 << 20) - 197334)*96 + ((1 << 15) - 22150)*512)
replay_unexec = (39*24 - A)*ATT
# (c) coin words of G2's 2,176 and self-tests C, D's 96 + 91 attempts
dev_coins = (2176 + 96 + 91)*((1 << 15) - 22150)*512
# (d) per-level key words at the layout keywords() builds (KOFF, 9 keys per
#     word below level 64, 10 per word at level 64)
NBL7 = (1, 2, 4, 8, 16, 32, 64)
NBL10 = (1, 2, 4, 5, 8, 10, 16, 20, 32, 40)
def level_words(NBL):
    KOFF = {nb: sum(n for n in NBL if n < nb) for nb in NBL}
    return sum(len({(KOFF[nb] + t)//9 if nb < 64 else 7 + t//10 for t in range(nb)}) for nb in NBL)
W7, W10 = level_words(NBL7), level_words(NBL10)
assert (W7, W10) == (19, 25)
HV = 48592224
hv_keywords = HV*((7*14 - W7)*3 + (10*15 - W10)*3)
# (e) replay test's 39 B' attempts (CandSetup + b_attempt at R7's (c, j)):
#     (k, WK cost, true cost) per R7 success, Table I.3
BP = [
    (1, 10578305631, 1649053363), (2, 8374490850, 1544966255), (3, 10060215913, 1597925121),
    (4, 9154314168, 1577048271), (5, 8729111449, 1566913115), (7, 10526065738, 1627653596),
    (8, 9659632208, 1591936433), (9, 8502475189, 1574879089), (10, 8411924843, 1570773125),
    (11, 8359492673, 1555048821), (13, 8417635173, 1569207520), (14, 10750234274, 1630154772),
    (15, 8662614347, 1563073391), (16, 11016608581, 1661507041), (17, 11780642981, 1675708291),
    (18, 10789754297, 1641146351), (19, 8340407469, 1569273715), (20, 8824734452, 1563864317),
    (21, 8552322640, 1540406302), (22, 10091596255, 1590916529), (23, 9445731877, 1573200011),
    (24, 8661799595, 1566293845), (26, 11618572967, 1671197462), (32, 9208445552, 1571017498),
    (33, 8390019559, 1557769818), (34, 10032427120, 1586849618), (35, 8154222470, 1562003502),
    (36, 8672347587, 1564982115), (37, 11319984179, 1668994911), (38, 9055029008, 1577820799),
    (39, 9485055974, 1601916336), (40, 10459771895, 1640210225), (41, 9431220980, 1581041621),
    (42, 9099400181, 1597363687), (43, 8621946139, 1537118875), (44, 12156614326, 1696484063),
    (45, 11793800980, 1663321826), (46, 8504803127, 1590376221), (47, 11173811528, 1644066438)]
assert len(BP) == 39 and len({k for k, w, t in BP}) == 39
assert all(0 < t <= w for k, w, t in BP)
BP_WK = sum(w for k, w, t in BP)
BP_TRUE = sum(t for k, w, t in BP)
assert (BP_WK, BP_TRUE) == (374867584175, 62313484289)
bprime_true = BP_WK - BP_TRUE
# (f) the three processes that measured (e), charged at true cost:
#     each = r5.py module load (2^31, W.6's bound) + Base() and own_bits()
#     (67,293,184) + the 39 B' attempts at true cost; one of them also ran the
#     replay test's 751 connector attempts (107,089,798 work units, 3,144,113
#     coin words) at the algorithm's price per attempt
PROC = (1 << 31) + 67293184 + BP_TRUE
measure = 3*PROC + 107089798*96 + 3144113*512 + 751*(1 << 22)

dev_reduction = replay + replay_unexec + dev_coins + hv_keywords + bprime_true - measure
assert online == 23202623488
assert replay == 65453891648
assert replay_unexec == 22502440960
assert dev_coins == 12846251008
assert hv_keywords == 29738441088
assert bprime_true == 312554099886
assert measure == 208625112131
assert dev_reduction == 234470012459

def cert(n):
    NP, CP = n**P, RATE**P
    a = (NP // CP).bit_length() - 1
    while (1 << (a + 1))*CP <= NP:
        a += 1
    while (1 << a)*CP > NP:
        a -= 1
    return a

total = base - Fraction(200000000*(dev_reduction + online), DEN)
pt = total * RATE
N = -(-pt.numerator // pt.denominator)
a = cert(N)
assert N == 10377085310562 and a == 3283438

T = (1 << 3277275) * RATE**P
U = 9943060583712
assert U**P >= T and (U - 1)**P < T
V = U - dev_reduction
b = cert(V)
assert b == 3273832

for name, v in (("(a) online (time only)", online), ("(b) replay", replay), ("(b) replay_unexec", replay_unexec),
                ("(c) dev_coins", dev_coins), ("(d) hv_keywords", hv_keywords), ("(e) bprime_true", bprime_true),
                ("(f) measure (charged)", -measure), ("dev_reduction (b)-(f)", dev_reduction)):
    print(f"{name:24} {v:>18,}")
print("total =", total)
print("N =", format(N, ","))
print(f"certificate: 2^{a} * {RATE}^{P} <= N^{P} < 2^{a+1} * {RATE}^{P}")
print("log2(N/RATE) =", f"{log2(N) - log2(RATE):.10f}")
print(f"time_log2 = {(a + 1)/P:.5f}")
print(f"preprocessing: 2^{b} * {RATE}^{P} <= V^{P} < 2^{b+1} * {RATE}^{P}, V = {V}")
print(f"preprocessing_log2 = {(b + 1)/P:.5f}")
