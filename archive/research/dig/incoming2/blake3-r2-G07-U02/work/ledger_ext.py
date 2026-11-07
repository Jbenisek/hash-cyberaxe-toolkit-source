# BASE reproduces the ledger of 9638e584 (57.6134); NEW is this entry. Each row is machine units (430 make one unit of time).
from math import isqrt
def cdiv(a, b):
    return -(-a // b)
E_COUNT = (23_820_160 + 34_028_800) // 2            # exact E-word counts of the two member types, averaged
FACTOR = 97 * 77_309_411_328 // 100                 # H1': 97/100 of the rate, rounded down
RUN_CONTEXTS = cdiv(cdiv(24797 << 128, 50000 * FACTOR * ((1 << 21) - 1)), 1 << 19)
RUN_STEPS = RUN_CONTEXTS << 19
S = isqrt(10 * RUN_CONTEXTS - 1) + 1                # Hoeffding reserve over contexts
MEMBERS, NBLK, LIVE16, ALPHA_B = 8, 16, 4160, 1_002_793
S_OLD = 5_486_510_246_044_225_536                   # preprocessing SEL, charged at its cap (not changed here)
ONCE_BASE = 1_128_752_545_267_752
ONCE = ONCE_BASE + (1 << 17) + (1 << 40) + (1 << 38) + (1 << 24) + (1 << 48) + (1 << 30) + (1 << 50) + (1 << 38) + (1 << 36) + (1 << 24) + (1 << 17)
# Parameters. pass_count: words per 2^32 passed by test (1); u_*: machine units; mu_millionths: MU in millionths of a unit per outer step;
# pre: call-only lane units debited with the screen; words/partial: boundary words per live block (old: 2 per range, new: ceil((E + b L)/7));
# setup/piece/wrap/ranges/pieces: live-block units and counts; final_per_chunk: units to write both messages for one chunk.
BASE = dict(pass_count=8_778_240, u_word=45, mu_millionths=11701, pre=0, u_pass=45, u_pass_x=10,
            words=("old", 17), partial=34, setup=241, piece=13, wrap=1, ranges=17, pieces=16,
            u_block=13, u_member=71, final_per_chunk=512)
NEW = dict(pass_count=14_110_208, u_word=46, mu_millionths=4425, pre=15, u_pass=39, u_pass_x=1,
           words=("new", 186), partial=31, setup=21, piece=10, wrap=0, ranges=16, pieces=16,
           u_block=9, u_member=68, final_per_chunk=128)
def ledger(c):
    share = c["pass_count"] * E_COUNT
    e_b = cdiv(1_000_051 * RUN_STEPS * E_COUNT, 10 ** 6 << 32) + (S << 19)
    p_b = cdiv(1_001_440 * RUN_STEPS * share, 10 ** 6 << 64) + (S << 19)
    live_b = cdiv(ALPHA_B * LIVE16 * NBLK * RUN_CONTEXTS, 10 ** 6 << 16) + NBLK * S
    if c["words"][0] == "old":
        words_b = cdiv(e_b, 7) + ((12 * c["words"][1] + 6) // 7) * live_b      # base: ceil(E/7) + 30 per live block
    else:
        words_b = cdiv(e_b + c["words"][1] * live_b, 7)                        # ceil((E + 186 L) / 7)
    part_b = c["partial"] * live_b
    u_pp = c["u_pass"] + c["u_pass_x"] + 21                                    # passing lane with the scan of its word
    u_live = c["setup"] + c["piece"] * c["pieces"] + c["wrap"] + 19 * c["ranges"]
    wb = c["u_word"] * words_b + 4 * part_b + u_live * live_b + 3 * e_b + u_pp * p_b
    if c["words"][0] == "old":
        w_ctx = (c["u_word"] + 4) * (cdiv(1 << 19, 7) + 2 * c["ranges"] * NBLK) + ((3 + u_pp) << 19) + u_live * NBLK
    else:
        w_ctx = c["u_word"] * cdiv((1 << 19) + c["words"][1] * NBLK, 7) + 4 * c["partial"] * NBLK + ((3 + u_pp) << 19) + u_live * NBLK
    capx = 3 * 7466 + 614 + 64 + 3 * 20 + c["pre"]
    mc, lc = cdiv(c["mu_millionths"] * RUN_STEPS, 10 ** 6), capx << 19
    credit = mc + isqrt(40 * lc * mc - 1) + 1 + 14 * lc + capx
    ctx_rows = (500 + 7 + c["u_member"] * MEMBERS) * (RUN_CONTEXTS + 1)
    blk_rows = c["u_block"] * NBLK * RUN_CONTEXTS
    final = (430 + 64) * 2 + c["final_per_chunk"] * (1 << 48) + 430 * 2 ** 38
    n = ctx_rows + blk_rows + wb + w_ctx + credit + ONCE + S_OLD + final
    rows = dict(RUN_CONTEXTS=RUN_CONTEXTS, S=S, E_B=e_b, P_B=p_b, LIVE_B=live_b, WORDS_B=words_b, PART_B=part_b, WB=wb,
                W_CTX=w_ctx, CAPX=capx, credit=credit, context_and_member_rows=ctx_rows, block_rows=blk_rows,
                once=ONCE, S_old=S_OLD, final=final, N=n)
    return rows
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
if __name__ == "__main__":
    from math import log2
    for name, c in (("BASE (9638e584)", BASE), ("NEW", NEW)):
        r = ledger(c)
        k = certificate(r["N"])
        print(name)
        for key, v in r.items():
            print("  %-22s %s" % (key, format(v, ",")))
        print("  certificate: 2^%d * 430^10000 <= N^10000 < 2^%d * 430^10000, time_log2 = %.4f (log2(N/430) = %.8f)" % (k, k + 1, (k + 1) / 1e4, log2(r["N"] / 430)))
