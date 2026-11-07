# Exact ledger of the entry, integers only (standard library). Run: python3 -B ledger.py
# BASE reproduces the ledger of 7c2264a8 (57.3737); NEW is this entry (changes 1 to 10 are those of c994a61f, 11 to 13 new). Each row is machine units (430 make one unit of time).
from math import isqrt
def cdiv(a, b):
    return -(-a // b)
E_COUNT = (23_820_160 + 34_028_800) // 2            # exact E-word counts of the two member types, averaged
# exact kept counts of the 16 member classes (type t, e1[2], e1[26], e1[27]); the classes have 32,768 members each
KEPT16 = [20_034_560] * 3 + [20_092_800, 20_034_560, 20_092_800, 20_034_560, 20_034_560] + \
         [28_620_800] * 3 + [28_704_000, 28_620_800, 28_704_000, 28_620_800, 28_620_800]
assert sum(KEPT16) == 389_525_760 and sum(KEPT16) % 16 == 0
E_KEPT = sum(KEPT16) // 16                           # 24,345,360: mean kept words of a uniform member
BUILD = 834_078_790_425_024                          # build of the 16 class lists, exact event counts (first section)
FACTOR = 974 * 77_309_411_328 // 1000                # declared 0.974 factor, rounded down
RUN_CONTEXTS = cdiv(cdiv(24797 << 128, 50000 * FACTOR * ((1 << 21) - 1)), 1 << 19)
RUN_STEPS = RUN_CONTEXTS << 19
S = isqrt(10 * RUN_CONTEXTS - 1) + 1                # Hoeffding reserve over contexts
MEMBERS, NBLK, LIVE16, ALPHA_B = 8, 16, 4160, 1_002_793
S_OLD = 116 * 18021 * (1 << 42) // 2 + 116 * ((1 << 51) + (1 << 10)) + (1 << 50)
ONCE_BASE = 1_128_752_545_267_752
ONCE = ONCE_BASE + (1 << 17) + (1 << 40) + (1 << 38) + (1 << 24) + (1 << 48) + (1 << 30) + (1 << 50) + (1 << 38) + (1 << 36) + (1 << 24) + (1 << 17)
# Parameters. pass_count: words per 2^32 passed by test (1); u_*: machine units; mu_millionths: MU in millionths of a unit per outer step;
# pre: call-only lane units debited with the screen; words: boundary words per live block (old: k words, new: ceil((E + b L)/7));
# partial: partial words per live block; setup/piece/wrap/ranges/pieces: live-block units and counts; final_per_chunk: units to write
# both messages for one chunk; u_word: the word row with its test (u_wt); u_pf: the prefilter of every word (kept words 1/8 + s).
BASE = dict(e_count=E_COUNT, build=0, pass_count=8_778_240, u_word=44, u_wt=2, u_pf=7, mu_millionths=11701, pre=0, u_pass=45, u_pass_x=10,
            words=("old", 28), partial=34, setup=241, piece=13, wrap=1, ranges=17, pieces=16,
            u_block=13, u_member=71, final_per_chunk=512, u_partial=2)
MU_NOPRE, MU_PRE = 4375, 4459                                   # declared by the preregistered run of this entry
NEW = dict(e_count=E_KEPT, build=BUILD, pass_count=14_110_208, u_word=46, u_wt=3, u_pf=7, mu_millionths=MU_PRE, pre=15, u_pass=39, u_pass_x=1,
           words=("new", 115), partial=31, setup=21, piece=10, wrap=0, ranges=16, pieces=16,
           u_block=9, u_member=71, final_per_chunk=128, u_partial=2)
def ledger(c):
    share = c["pass_count"] * E_COUNT
    e_b = cdiv(1_000_051 * RUN_STEPS * c["e_count"], 10 ** 6 << 32) + (S << 19)
    p_b = cdiv(1_001_440 * RUN_STEPS * share, 10 ** 6 << 64) + (S << 19)
    live_b = cdiv(ALPHA_B * LIVE16 * NBLK * RUN_CONTEXTS, 10 ** 6 << 16) + NBLK * S
    if c["words"][0] == "old":
        words_b = cdiv(e_b, 7) + c["words"][1] * live_b                        # ceil(E/7) + k per live block
    else:
        words_b = cdiv(e_b + c["words"][1] * live_b, 7)                        # ceil((E + 186 L) / 7)
    part_b = c["partial"] * live_b
    pf_b = cdiv(words_b, 8) + S                                                # kept words: 1/8 of the words, plus the reserve
    epf_b = 7 * pf_b                                                           # E lanes of kept words (seven slots each)
    u_pp = c["u_pass"] + c["u_pass_x"] + 12                                    # passing lane with the scan of its word
    u_live = c["setup"] + c["piece"] * c["pieces"] + c["wrap"] + 19 * c["ranges"]
    wb = ((c["u_word"] + c["u_pf"] - c["u_wt"]) * words_b + c["u_partial"] * part_b + u_live * live_b + 3 * epf_b
          + c["u_wt"] * pf_b + u_pp * p_b)
    if c["words"][0] == "old":
        w_ctx = ((c["u_word"] + c["u_pf"] + c["u_partial"] + 21) * (cdiv(1 << 19, 7) + 2 * c["ranges"] * NBLK)
                 + (u_pp << 19) + u_live * NBLK)
    else:
        w_ctx = ((c["u_word"] + c["u_pf"] + 21) * cdiv((1 << 19) + c["words"][1] * NBLK, 7)
                 + c["u_partial"] * c["partial"] * NBLK + (u_pp << 19) + u_live * NBLK)
    capx = 3 * 7466 + 614 + 64 + 3 * 20 + c["pre"]
    mc, lc = cdiv(c["mu_millionths"] * RUN_STEPS, 10 ** 6), capx << 19
    credit = mc + isqrt(40 * lc * mc - 1) + 1 + 14 * lc + capx
    ctx_rows = (436 + 7 + c["u_member"] * MEMBERS) * (RUN_CONTEXTS + 1)
    blk_rows = c["u_block"] * NBLK * RUN_CONTEXTS
    final = (430 + 64) * 2 + c["final_per_chunk"] * (1 << 48) + 430 * 2 ** 38
    n = ctx_rows + blk_rows + wb + w_ctx + credit + ONCE + c["build"] + S_OLD + final
    return dict(RUN_CONTEXTS=RUN_CONTEXTS, S=S, E_B=e_b, P_B=p_b, LIVE_B=live_b, WORDS_B=words_b, PART_B=part_b, PF_B=pf_b,
                EPF_B=epf_b, WB=wb, W_CTX=w_ctx, CAPX=capx, credit=credit, context_and_member_rows=ctx_rows,
                block_rows=blk_rows, once=ONCE + c["build"], S_old=S_OLD, final=final, N=n)
def certificate(n):
    # k with 2^k * 430^10000 <= n^10000 < 2^(k+1) * 430^10000, k = floor(10000 * log2(n / 430))
    lo, hi = 0, 10 ** 7
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if (1 << mid) * 430 ** 10000 <= n ** 10000:
            lo = mid
        else:
            hi = mid - 1
    k = lo
    assert (1 << k) * 430 ** 10000 <= n ** 10000 < (1 << (k + 1)) * 430 ** 10000
    return k
# The changes, each as the parameters it sets, applied to BASE in this order.
CHANGES = (
    ("1 pass row at the executed share 14,110,208", dict(pass_count=14_110_208)),
    ("2 word test three units (AND, compare, branch)", dict(u_word=45, u_wt=3)),
    ("3 Y9 fill 39 units (the 38-unit fill is not executable)", dict(u_word=46)),
    ("4 MU re-declared, without the call-only units", dict(mu_millionths=MU_NOPRE)),
    ("5 call-only lane words debited with the call", dict(pre=15, u_pass=39, u_pass_x=1, mu_millionths=MU_PRE)),
    ("6 closed-form cut, doubled lists, 16 ranges", dict(setup=21, piece=10, wrap=0, ranges=16, partial=32)),
    ("7 boundary words 115/7, partial words 31", dict(words=("new", 115), partial=31)),
    ("8 block 9, test for a second block in the member", dict(u_block=9, u_member=73)),
    ("9 member 68", dict(u_member=68)),
    ("10 final step at 256-bit words", dict(final_per_chunk=128)),
    ("11 lists of the member's class: E_KEPT for E_COUNT", dict(e_count=E_KEPT)),
    ("12 build of the 16 class lists in the once row", dict(build=BUILD)),
    ("13 member 71: the class in the table index", dict(u_member=71)),
)
if __name__ == "__main__":
    from math import log2
    def show(name, c):
        r = ledger(c)
        k = certificate(r["N"])
        print(name)
        for key, v in r.items():
            if key in ("E_B", "WORDS_B", "PF_B", "WB", "W_CTX", "credit", "context_and_member_rows", "block_rows", "once", "S_old", "final"):
                print("  %-22s %s" % (key, format(v, ",")))
        return r, k
    r0 = ledger(BASE)
    k0 = certificate(r0["N"])
    print("  base N %s, certificate 2^%d, log2(N/430) = %.8f" % (format(r0["N"], ","), k0, log2(r0["N"] / 430)))
    cur, prev = dict(BASE), log2(r0["N"])
    print("bits of each change on log2 N, in this order (after the changes above it)")
    for label, ch in CHANGES:
        cur.update(ch)
        now = log2(ledger(cur)["N"])
        print("  %-62s %+.5f" % (label, now - prev))
        prev = now
    assert cur == NEW
    r, k = show("NEW", NEW)
    print("  certificate: 2^%d * 430^10000 <= N^10000 < 2^%d * 430^10000" % (k, k + 1))
    print("  log2(N/430) = %.8f" % log2(r["N"] / 430))
    print("  N = %d" % r["N"])
    print("  time_log2 = %.4f" % ((k + 1) / 1e4))
