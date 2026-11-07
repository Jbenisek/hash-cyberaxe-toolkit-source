#!/usr/bin/env python3
"""Worst-case charge of stage E (root isolation, split.c split_find_root_capped) and of the coin draw, for the algebraic-paper program.
Each function is ported statement by statement from the shipped split.c / line.c / poly.c / pallas.c with the charges of common.h.
Bounds used where the charge depends on data:
  * allocator: xalloc <= 120 + 13 (2 L + 1) with L = live blocks, xfree = 105 (LEDGER.md A3).  In stage E the live blocks are: the twiddle table, G,
    S, Sm, Gp, Gm and the two arrays of gcd_cl (8 blocks), plus at most 4 inside taylor_shift / sqr_mod: L <= LMAX_E = 16 is used.
  * gcd_cl: at most d outer iterations (the degree of B strictly decreases from at most d - 1 to -1), at most 2d + 1 division steps (the sum of the two
    degrees drops by at least one per step); every step is charged at the largest dB (= d).
Nothing here is measured; test_e.c (Appendix C of the proof) compares these bounds with the counters of the program."""
import math

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL = 2310
STAGE_BK = 1000
LMAX_E = 16
DMAX, ZCAP = 16, 64


def powcost(e):
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


def XA(L=LMAX_E):            # one NEW_FP: CTL(1) + xalloc
    return 1 + 120 + 13 * (2 * L + 1)


XF = 105
LD = lambda n: 2 * n
ST = lambda n: 2 * n
LOOPC = lambda n: 3 * n + 2
INV = powcost(PM2) + INV_CTL            # fp_inv + CTL(INV_CTL)

COIN_DRAW = (1 + 1 + 1 + 3) + 3 * (1 + 1 + 1) + (3 * 3 + 2) + 1 + 2 + 2      # one 256-bit word: 1 random-word operation, 1 load, 1 store, 3 control (two addresses, the position increment) = 6; reduction mod p by three rounds of (comparison, branch, subtraction) = 9 with the loop control 3*3+2 = 11; one Montgomery conversion 1; entry 2; address of w 2: 31
SHIFT_ZERO_TEST = 5 + 2                  # split.c: CTL(5) zero test and branch, and (worst case, the branch taken) ST(1) = 2 for the replacement of a zero draw by 1
COIN_WORDS = 2 * (1 + 64)                # K (1 + ZCAP) draws of 1 word, K = 2
COIN_BYTES = COIN_WORDS * 8
SYS_READ = 10000 + (COIN_BYTES << 3)     # single.c: the one read system call of the coin tape (as SYS_WRITE)
COIN_READ = 0                           # no input: the random words are the cost model primitive


def poly_mul_naive(n):
    terms = n * n
    adds = n * n - (2 * n - 1)
    return terms + adds + 10 * terms + 11 * (2 * n - 1) + 2


def taylor_shift(d):
    n = d + 1
    c = 2 * XA()
    c += n + 2 * (n - 1) + LD(n) + ST(n) + LOOPC(n) + 2 * n + 1       # first loop and its charges
    c += XF                                                           # xfree(G)
    c += INV + powcost(d) + 80 + INV + 1                              # 1/d!, a^d, 1/a, conversion of d
    c += 4 * n + ST(n) + LOOPC(n) + n                                 # second loop
    c += 2                                                            # test n <= 48
    assert n <= 48
    c += XA() + poly_mul_naive(n)
    c += 1 + 3 * n + LD(n) + ST(n) + LOOPC(n) + n + 1                # third loop, conversion of d
    c += 2 * XF
    return c


def sqr_mod(d):
    return XA() + 2 * d + 3 * (d * (d - 1) // 2) + 2 * d * d, XF


def mulx_mod(d):
    return 2 * d


def pow_half(d):
    nsqr = 253                                   # bits 252..0 of (p-1)/2 (top bit 253)
    nmul = bin(PM1H).count('1') - 1
    arith = nsqr * (2 * d + 3 * (d * (d - 1) // 2) + 2 * d * d) + nmul * mulx_mod(d)
    c = 2 + arith + nsqr * (XA() + XF) + nsqr * (3 + 7 + 2 + 3)
    c += 9 * arith                               # bound_mem_since: per field operation 2 loads, 1 store, 6 control
    return c


def gcd_cl(d_a, d_b):
    """worst case of gcd_cl(a of degree d_a, b with degree bound d_b), d_a >= d_b."""
    d = d_a
    c = 2 * XA() + LD(d_a + d_b + 2) + ST(d_a + d_b + 2) + LOOPC(d_a + d_b + 2)
    c += 9 * (0 + d_b + 2) + 4                   # degree scans (a is exact, b may be the zero polynomial)
    outer = d
    c += outer * (2 + 2 + INV + 6)               # CTL(2), inversion with LD(1), CTL(6) swap
    steps = 2 * d + 1
    c += steps * (3 + 1 + 2 + 2 * d + LD(2 * d) + ST(d) + LOOPC(d) + d + 2) + 9 * (2 * d + steps) + 6 * steps + 4 * d
    c += 2 + 2 + INV + LD(d + 1) + (d + 1) + ST(d + 1) + LOOPC(d + 1) + 2 * XF
    return c


def round_cost(d):
    """one round of the while loop of split_find_root_capped at current degree d (2 <= d <= DMAX)."""
    c = 6 + COIN_DRAW + SHIFT_ZERO_TEST + 1      # loop tests, the coin draw, the zero test (a = 0 replaced by 1), fp_neg
    c += taylor_shift(d) + 1                     # G(Z - a), shift += a
    c += 2 * XA()                                # S, Sm
    c += pow_half(d)
    c += LD(d) + ST(d) + LOOPC(d) + 2 + LD(2) + ST(2)
    c += 2 * XA()                                # Gp, Gm
    c += 2 * gcd_cl(d, d - 1)
    c += 2 * XF + 8
    c += 3 * XF + XA() + ST(2)                   # branch tails (the largest: three frees, the new G = Z)
    return c


def stage_E(rounds=ZCAP, d=DMAX):
    """one trial: the entry CTL(3), `rounds` rounds at degree d (all at the largest degree), the exit (isolation failure or the root)."""
    return STAGE_BK + 3 + rounds * round_cost(d) + 3 + 1 + LD(1) + 1 + XF + 2


def stage_F():
    """stage F worst case (single.c, pallas.c, line.c): stage_open 1000 + CTL(12000) + CTL(2) + 10 x (field operations), because bound_mem_since adds 9 per operation.
    Field operations: fp_pow(Q), fp_pow(QP1H), Tonelli-Shanks (outer iteration with parameter m costs m squarings and 2 multiplications; m falls strictly from 32),
    two map_back (3 fifth-root powers, 2 multiplications, 2 additions, 2 subtractions each), one addition, one subtraction."""
    Q = (P - 1) >> 32
    QP1H = (Q + 1) >> 1
    E5INV = (4 * (P - 1) + 1) // 5
    ts = sum(m + 2 for m in range(1, 33))
    arith = powcost(Q) + powcost(QP1H) + ts + 2 * (3 * powcost(E5INV) + 6) + 2
    return STAGE_BK + 12000 + 2 + 10 * arith, arith


if __name__ == '__main__':
    print('COIN_DRAW', COIN_DRAW, 'COIN_READ', COIN_READ, 'SHIFT_ZERO_TEST', SHIFT_ZERO_TEST)
    print('INV', INV, 'XA', XA())
    for d in (2, 4, 8, 16):
        print('d', d, 'taylor', taylor_shift(d), 'pow_half', pow_half(d), 'gcd_cl', gcd_cl(d, d - 1), 'round', round_cost(d))
    print('stage_E(64 rounds at d=16)', stage_E())
    print('stage_F', stage_F())
