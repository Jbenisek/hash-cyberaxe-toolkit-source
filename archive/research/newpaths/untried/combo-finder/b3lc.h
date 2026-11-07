/* b3lc.h -- stage solvers for the 2-round BLAKE3 message-only local collision
 * with message differences in m2, m3, m4, m6 (round-0 calls K1,K2,K3 -> D1,D3 ->
 * absorbed by round-1 C0 (m2,m6), C1 (m3), C3 (m4); round-1 diagonals see no difference).
 * Our own team research (combo-finder scout). Derivation of every condition is in RESULT.md.
 */
#ifndef B3LC_H
#define B3LC_H
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint32_t u32;
typedef uint64_t u64;

static inline u32 ror32(u32 x, int n){ n &= 31; return n ? (x >> n) | (x << (32 - n)) : x; }
static inline u32 rol32(u32 x, int n){ n &= 31; return n ? (x << n) | (x >> (32 - n)) : x; }

static const u32 B3IV[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                            0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};
static const int B3PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};

/* reference compression (same as hash-smash/verifier/blake3.py _compress), returns 16 words */
static void b3_g(u32 *v, int a, int b, int c, int d, u32 x, u32 y){
  v[a] = v[a] + v[b] + x; v[d] = ror32(v[d] ^ v[a], 16); v[c] = v[c] + v[d]; v[b] = ror32(v[b] ^ v[c], 12);
  v[a] = v[a] + v[b] + y; v[d] = ror32(v[d] ^ v[a], 8);  v[c] = v[c] + v[d]; v[b] = ror32(v[b] ^ v[c], 7);
}
static void b3_compress(const u32 cv[8], const u32 words[16], u64 counter, u32 blen, u32 flags, int rounds,
                        u32 out[16], u32 state_out[16]){
  u32 v[16], m[16], t[16];
  for (int i = 0; i < 8; i++) v[i] = cv[i];
  for (int i = 0; i < 4; i++) v[8 + i] = B3IV[i];
  v[12] = (u32)counter; v[13] = (u32)(counter >> 32); v[14] = blen; v[15] = flags;
  memcpy(m, words, sizeof m);
  for (int r = 0; r < rounds; r++){
    b3_g(v, 0, 4, 8, 12, m[0], m[1]);  b3_g(v, 1, 5, 9, 13, m[2], m[3]);
    b3_g(v, 2, 6, 10, 14, m[4], m[5]); b3_g(v, 3, 7, 11, 15, m[6], m[7]);
    b3_g(v, 0, 5, 10, 15, m[8], m[9]); b3_g(v, 1, 6, 11, 12, m[10], m[11]);
    b3_g(v, 2, 7, 8, 13, m[12], m[13]); b3_g(v, 3, 4, 9, 14, m[14], m[15]);
    for (int i = 0; i < 16; i++) t[i] = m[B3PERM[i]];
    memcpy(m, t, sizeof m);
  }
  if (state_out) memcpy(state_out, v, sizeof v);
  for (int i = 0; i < 8; i++){ out[i] = v[i] ^ v[i + 8]; out[i + 8] = v[i + 8] ^ cv[i]; }
}

/* ---- ADD/XOR compatibility: { a : a ^ (a + D) == e }.  Returns 1 and the cube (fixed mask F,
 * fixed values V; other bits free) if nonempty, else 0.  carry into bit i is k_i = e_i ^ D_i. */
static inline int compat_cube(u32 D, u32 e, u32 *F, u32 *V){
  u32 k = e ^ D;
  if (k & 1u) return 0;
  u32 kn = k >> 1;
  u32 eqm = (~(D ^ k)) & 0x7fffffffu;   /* D_i == k_i : a_i free, need k_{i+1} == D_i */
  if (eqm & (kn ^ D)) return 0;
  u32 neq = (D ^ k) & 0x7fffffffu;      /* D_i != k_i : a_i = k_{i+1} */
  *F = neq; *V = kn & neq;
  return 1;
}

/* ---- count / sample d in cube (Fd,Vd) with (C + d) ^ (Cp + d) == f */
static u64 xa2_count(u32 C, u32 Cp, u32 f, u32 Fd, u32 Vd){
  u64 cnt[4] = {1, 0, 0, 0};
  u32 phi = f ^ C ^ Cp;
  for (int i = 0; i < 32; i++){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1, ph = (phi >> i) & 1;
    int fixed = (Fd >> i) & 1; u32 fv = (Vd >> i) & 1;
    u64 nc[4] = {0, 0, 0, 0};
    for (int s = 0; s < 4; s++){
      if (!cnt[s]) continue;
      u32 k = s & 1, kp = s >> 1;
      if ((k ^ kp) != ph) continue;
      for (u32 di = 0; di < 2; di++){
        if (fixed && di != fv) continue;
        u32 kn = (Ci & di) | (Ci & k) | (di & k);
        u32 kpn = (Cpi & di) | (Cpi & kp) | (di & kp);
        nc[kn | (kpn << 1)] += cnt[s];
      }
    }
    memcpy(cnt, nc, sizeof nc);
  }
  return cnt[0] + cnt[1] + cnt[2] + cnt[3];
}
/* sample one solution using a random 64-bit value r for choices; returns 0 if none */
static int xa2_sample(u32 C, u32 Cp, u32 f, u32 Fd, u32 Vd, u64 r, u32 *dout){
  unsigned char ok[33][4];
  u32 phi = f ^ C ^ Cp;
  for (int s = 0; s < 4; s++) ok[32][s] = 1;
  for (int i = 31; i >= 0; i--){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1, ph = (phi >> i) & 1;
    int fixed = (Fd >> i) & 1; u32 fv = (Vd >> i) & 1;
    for (int s = 0; s < 4; s++){
      u32 k = s & 1, kp = s >> 1; ok[i][s] = 0;
      if ((k ^ kp) != ph) continue;
      for (u32 di = 0; di < 2; di++){
        if (fixed && di != fv) continue;
        u32 kn = (Ci & di) | (Ci & k) | (di & k);
        u32 kpn = (Cpi & di) | (Cpi & kp) | (di & kp);
        if (ok[i + 1][kn | (kpn << 1)]) { ok[i][s] = 1; break; }
      }
    }
  }
  if (!ok[0][0]) return 0;
  int s = 0; u32 d = 0;
  for (int i = 0; i < 32; i++){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1;
    int fixed = (Fd >> i) & 1; u32 fv = (Vd >> i) & 1;
    u32 k = s & 1, kp = s >> 1;
    u32 first = (u32)((r >> (i & 63)) & 1);
    int done = 0;
    for (u32 t = 0; t < 2 && !done; t++){
      u32 di = first ^ t;
      if (fixed && di != fv) continue;
      u32 kn = (Ci & di) | (Ci & k) | (di & k);
      u32 kpn = (Cpi & di) | (Cpi & kp) | (di & kp);
      int ns = kn | (kpn << 1);
      if (ok[i + 1][ns]) { d |= di << i; s = ns; done = 1; }
    }
    if (!done) return 0; /* cannot happen */
  }
  *dout = d;
  return 1;
}

/* pick a random element of a cube */
static inline u32 cube_pick(u32 F, u32 V, u32 r){ return (V & F) | (r & ~F); }

/* splitmix64 */
static u64 g_rng = 0x1234567;
static inline u64 rnd64(void){
  u64 z = (g_rng += 0x9E3779B97F4A7C15ULL);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}

/* ===== Stage K3: G(h3,h7,IV3,flags; m6,m7), dm6 = delta.  Outputs a,c differ; b,d equal.
 * A = h3+h7+m6 (free).  Returns 1 if a solution exists for (A,delta); fills outputs for one
 * random a2 choice.  D = modular difference of a2 (= dv3). */
typedef struct { u32 A, delta, D, a2, m7base; u32 v3, v3p, v7, v11, v11p, v15; u64 nsol; } K3sol;
static inline int k3_try(u32 h7, u32 flags, u32 A, u32 delta, K3sol *o, int want){
  if (!delta) return 0;                 /* trivial (no difference) */
  u32 Ap = A + delta;
  u32 d1 = ror32(flags ^ A, 16), d1p = ror32(flags ^ Ap, 16);
  u32 c1 = B3IV[3] + d1, c1p = B3IV[3] + d1p;
  u32 b1 = ror32(h7 ^ c1, 12), b1p = ror32(h7 ^ c1p, 12);
  u32 S = A + b1, Sp = Ap + b1p, D = Sp - S;
  u32 Fa, Va;
  if (!compat_cube(D, d1 ^ d1p, &Fa, &Va)) return 0;
  /* d2 = ror(d1 ^ a2, 8): cube */
  u32 Fd = ror32(Fa, 8), Vd = ror32((Va ^ d1) & Fa, 8);
  u64 n = xa2_count(c1, c1p, b1 ^ b1p, Fd, Vd);
  if (!n) return 0;
  if (!want) { if (o) o->nsol = n; return 1; }
  u32 d2;
  if (!xa2_sample(c1, c1p, b1 ^ b1p, Fd, Vd, rnd64(), &d2)) return 0;
  u32 a2 = rol32(d2, 8) ^ d1;
  u32 c2 = c1 + d2, c2p = c1p + d2;
  o->A = A; o->delta = delta; o->D = D; o->a2 = a2; o->m7base = a2 - S; o->nsol = n;
  o->v3 = a2; o->v3p = a2 + D; o->v7 = ror32(b1 ^ c2, 7); o->v11 = c2; o->v11p = c2p; o->v15 = d2;
  return 1;
}

/* ===== Stage K2: G(h2,h6,IV2,blen; m4,m5), dm4 forced.  Outputs b,d differ; a,c equal. */
typedef struct { u32 A, dm4, a2, d2, d2p, v2, v6, v6p, v10, v14, v14p; u32 m5; u64 cube; } K2sol;
static inline int k2_a(u32 h6, u32 blen, u32 A, u32 dm4){
  u32 Ap = A + dm4;
  u32 b1 = ror32(h6 ^ (B3IV[2] + ror32(blen ^ A, 16)), 12);
  u32 b1p = ror32(h6 ^ (B3IV[2] + ror32(blen ^ Ap, 16)), 12);
  return (A + b1) == (Ap + b1p);
}
static inline int k2_b(u32 h6, u32 blen, u32 A, u32 dm4, K2sol *o){
  u32 Ap = A + dm4;
  u32 d1 = ror32(blen ^ A, 16), d1p = ror32(blen ^ Ap, 16);
  u32 c1 = B3IV[2] + d1, c1p = B3IV[2] + d1p;
  u32 b1 = ror32(h6 ^ c1, 12), b1p = ror32(h6 ^ c1p, 12);
  if (A + b1 != Ap + b1p) return 0;
  u32 eta = ror32(d1 ^ d1p, 8), M = c1 - c1p, F, V;
  if (!compat_cube(M, eta, &F, &V)) return 0;
  if (!o) return 1;
  u32 d2 = cube_pick(F, V, (u32)rnd64());
  u32 d2p = d2 ^ eta;
  u32 a2 = rol32(d2, 8) ^ d1;
  u32 c2 = c1 + d2;
  o->A = A; o->dm4 = dm4; o->a2 = a2; o->d2 = d2; o->d2p = d2p; o->m5 = a2 - A - b1;
  o->v2 = a2; o->v10 = c2; o->v14 = d2; o->v14p = d2p; o->v6 = ror32(b1 ^ c2, 7); o->v6p = ror32(b1p ^ c2, 7);
  o->cube = 1ULL << (32 - __builtin_popcount(F));
  return 1;
}

/* ===== Stage K1: G(h1,h5,IV1,t_hi; m2,m3), dm2 = -delta forced, dm3 forced by C1:
 * 2*dm3 = -((S'-S) + dv6).  Outputs a,c differ; b,d equal. */
typedef struct { u32 A, dm2, dm3, a2, Dm, m3base; u32 v1, v1p, v5, v9, v9p, v13; u64 nsol; } K1sol;
static inline int k1_try(u32 h5, u32 thi, u32 A, u32 dm2, u32 dv6, int which, K1sol *o, int want){
  if (!dm2) return 0;
  u32 Ap = A + dm2;
  u32 d1 = ror32(thi ^ A, 16), d1p = ror32(thi ^ Ap, 16);
  u32 c1 = B3IV[1] + d1, c1p = B3IV[1] + d1p;
  u32 b1 = ror32(h5 ^ c1, 12), b1p = ror32(h5 ^ c1p, 12);
  u32 S = A + b1, Sp = Ap + b1p;
  u32 R = (Sp - S) + dv6;
  if (R & 1u) return 0;
  u32 dm3 = ((u32)(0u - R)) >> 1; if (which) dm3 += 0x80000000u;
  u32 Dm = (Sp - S) + dm3;
  u32 Fa, Va;
  if (!compat_cube(Dm, d1 ^ d1p, &Fa, &Va)) return 0;
  u32 Fd = ror32(Fa, 8), Vd = ror32((Va ^ d1) & Fa, 8);
  u64 n = xa2_count(c1, c1p, b1 ^ b1p, Fd, Vd);
  if (!n) return 0;
  if (!want) { if (o) o->nsol = n; return 1; }
  u32 d2;
  if (!xa2_sample(c1, c1p, b1 ^ b1p, Fd, Vd, rnd64(), &d2)) return 0;
  u32 a2 = rol32(d2, 8) ^ d1;
  u32 c2 = c1 + d2, c2p = c1p + d2;
  o->A = A; o->dm2 = dm2; o->dm3 = dm3; o->a2 = a2; o->Dm = Dm; o->m3base = a2 - S; o->nsol = n;
  o->v1 = a2; o->v1p = a2 + Dm; o->v5 = ror32(b1 ^ c2, 7); o->v9 = c2; o->v9p = c2p; o->v13 = d2;
  return 1;
}

/* ===== Stage D3: G(v3,v4,v9,v14; m14,m15).  Input diffs a,c,d; output only a differs.
 * A = v3+v4+m14 (free), A' = A + dv3.  (i) v9 + d1 == v9' + d1'; (ii) compat(dv3, d1^d1') */
static inline int d3_i(u32 dv3, u32 v9, u32 v9p, u32 v14, u32 v14p, u32 A){
  return v9 + ror32(v14 ^ A, 16) == v9p + ror32(v14p ^ (A + dv3), 16);
}
static inline int d3_ii(u32 dv3, u32 v14, u32 v14p, u32 A, u32 *F, u32 *V){
  u32 d1 = ror32(v14 ^ A, 16), d1p = ror32(v14p ^ (A + dv3), 16);
  return compat_cube(dv3, d1 ^ d1p, F, V);
}

/* ===== Stage D1: G(v1,v6,v11,v12; m10,m11).  Input diffs a,b,c (v12 free via K0);
 * outputs a,d differ; b,c equal.  A = v1+v6+m10, A' = A + Delta1 (Delta1 = dv1+dv6 = -dm3).
 * (i) (v11 + q) ^ (v11' + (q ^ eps')) == v6 ^ v6',  q = ror(v12 ^ A,16), eps' = ror(A ^ A',16)
 * (ii) c1 + d2 == c1' + d2',  d2 = ror(d1 ^ a2, 8), d2' = ror(d1' ^ (a2 + Delta1), 8) */
/* (i) as a DP over q bits: (C + q) ^ (Cp + (q ^ x)) == f  -> count/sample q */
static int d1i_sample(u32 C, u32 Cp, u32 x, u32 f, u64 r, u32 *qout, u64 *count){
  /* state (k, kp) carries of C+q and Cp+(q^x) */
  u64 cnt[33][4]; memset(cnt, 0, sizeof cnt); cnt[0][0] = 1;
  for (int i = 0; i < 32; i++){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1, xi = (x >> i) & 1, fi = (f >> i) & 1;
    for (int s = 0; s < 4; s++){
      if (!cnt[i][s]) continue;
      u32 k = s & 1, kp = s >> 1;
      for (u32 qi = 0; qi < 2; qi++){
        u32 qpi = qi ^ xi;
        u32 o = Ci ^ qi ^ k, op = Cpi ^ qpi ^ kp;
        if ((o ^ op) != fi) continue;
        u32 kn = (Ci & qi) | (Ci & k) | (qi & k);
        u32 kpn = (Cpi & qpi) | (Cpi & kp) | (qpi & kp);
        cnt[i + 1][kn | (kpn << 1)] += cnt[i][s];
      }
    }
  }
  u64 tot = cnt[32][0] + cnt[32][1] + cnt[32][2] + cnt[32][3];
  if (count) *count = tot;
  if (!tot || !qout) return tot ? 1 : 0;
  /* backward sampling: choose final state weighted, walk back */
  /* simple approach: forward walk with backward reachability */
  unsigned char ok[33][4];
  for (int s = 0; s < 4; s++) ok[32][s] = 1;
  for (int i = 31; i >= 0; i--){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1, xi = (x >> i) & 1, fi = (f >> i) & 1;
    for (int s = 0; s < 4; s++){
      u32 k = s & 1, kp = s >> 1; ok[i][s] = 0;
      for (u32 qi = 0; qi < 2; qi++){
        u32 qpi = qi ^ xi; u32 o = Ci ^ qi ^ k, op = Cpi ^ qpi ^ kp;
        if ((o ^ op) != fi) continue;
        u32 kn = (Ci & qi) | (Ci & k) | (qi & k), kpn = (Cpi & qpi) | (Cpi & kp) | (qpi & kp);
        if (ok[i + 1][kn | (kpn << 1)]) { ok[i][s] = 1; break; }
      }
    }
  }
  if (!ok[0][0]) return 0;
  int s = 0; u32 q = 0;
  for (int i = 0; i < 32; i++){
    u32 Ci = (C >> i) & 1, Cpi = (Cp >> i) & 1, xi = (x >> i) & 1, fi = (f >> i) & 1;
    u32 k = s & 1, kp = s >> 1; u32 first = (u32)((r >> (i & 63)) & 1); int done = 0;
    for (u32 t = 0; t < 2 && !done; t++){
      u32 qi = first ^ t, qpi = qi ^ xi; u32 o = Ci ^ qi ^ k, op = Cpi ^ qpi ^ kp;
      if ((o ^ op) != fi) continue;
      u32 kn = (Ci & qi) | (Ci & k) | (qi & k), kpn = (Cpi & qpi) | (Cpi & kp) | (qpi & kp);
      int ns = kn | (kpn << 1);
      if (ok[i + 1][ns]) { q |= qi << i; s = ns; done = 1; }
    }
    if (!done) return 0;
  }
  *qout = q;
  return 1;
}
/* (ii): find a2 with ror(d1p ^ (a2+Dl),8) - ror(d1 ^ a2,8) == M.  DP over a2 bits j with
 * add-carry c (a2+Dl, from bit 0) and sub-borrow b of z' - z ... implemented as z' = z + M where
 * z = ror(d1^a2,8): z bit i = (d1^a2) bit (i+8).  Guess the add-carry into bit 8. */
static int d1ii_sample(u32 d1, u32 d1p, u32 Dl, u32 M, u64 r, u32 *aout, u64 *count){
  /* process j = 8..31 then 0..7.  z-bit i = j-8 (mod 32); z-chain carry starts 0 at j=8.
   * add chain (w = a2, w' = a2 + Dl): carry into bit 8 guessed g; at j=0 carry 0; must reach g at j=8. */
  u64 total = 0; int found = 0; u32 best = 0;
  for (u32 g = 0; g < 2; g++){
    /* state: (cadd, cz) ; order of j: 8..31, 0..7 */
    int order[32]; for (int t = 0; t < 32; t++) order[t] = (t + 8) & 31;
    u64 cnt[33][4]; memset(cnt, 0, sizeof cnt);
    cnt[0][g | 0] = 1; /* cadd = g at j=8, cz = 0 */
    for (int t = 0; t < 32; t++){
      int j = order[t];
      for (int s = 0; s < 4; s++){
        if (!cnt[t][s]) continue;
        u32 ca = s & 1, cz = s >> 1;
        if (j == 0) { if (ca != 0) { continue; } }
        for (u32 w = 0; w < 2; w++){
          u32 Dj = (Dl >> j) & 1;
          u32 wp = w ^ Dj ^ ca; u32 can = (w & Dj) | (w & ca) | (Dj & ca);
          if (j == 31) can = 0; /* carry out of bit 31 discarded; next is j=0 with carry 0 */
          u32 x = ((d1 >> j) & 1) ^ w, xp = ((d1p >> j) & 1) ^ wp;
          u32 i = (u32)((j - 8) & 31); u32 Mi = (M >> i) & 1;
          /* z' bit = z ^ M ^ cz must equal xp */
          if ((x ^ Mi ^ cz) != xp) continue;
          u32 czn = (x & Mi) | (x & cz) | (Mi & cz);
          if (i == 31) czn = 0;
          /* at j == 7 the add carry out must equal g (carry into bit 8) */
          if (j == 7 && can != g) continue;
          cnt[t + 1][can | (czn << 1)] += cnt[t][s];
        }
      }
    }
    u64 tot = cnt[32][0] + cnt[32][1] + cnt[32][2] + cnt[32][3];
    total += tot;
    if (tot && aout && !found){
      /* sample by forward walk with backward reachability (recompute ok) */
      unsigned char ok[33][4]; for (int s = 0; s < 4; s++) ok[32][s] = 1;
      for (int t = 31; t >= 0; t--){
        int j = order[t];
        for (int s = 0; s < 4; s++){
          u32 ca = s & 1, cz = s >> 1; ok[t][s] = 0;
          if (j == 0 && ca != 0) continue;
          for (u32 w = 0; w < 2; w++){
            u32 Dj = (Dl >> j) & 1; u32 wp = w ^ Dj ^ ca; u32 can = (w & Dj) | (w & ca) | (Dj & ca);
            if (j == 31) can = 0;
            u32 x = ((d1 >> j) & 1) ^ w, xp = ((d1p >> j) & 1) ^ wp;
            u32 i = (u32)((j - 8) & 31); u32 Mi = (M >> i) & 1;
            if ((x ^ Mi ^ cz) != xp) continue;
            u32 czn = (x & Mi) | (x & cz) | (Mi & cz); if (i == 31) czn = 0;
            if (j == 7 && can != g) continue;
            if (ok[t + 1][can | (czn << 1)]) { ok[t][s] = 1; break; }
          }
        }
      }
      int s = g; u32 a = 0; int okw = ok[0][s];
      if (okw){
        for (int t = 0; t < 32; t++){
          int j = order[t]; u32 ca = s & 1, cz = s >> 1; u32 first = (u32)((r >> t) & 1); int done = 0;
          for (u32 tt = 0; tt < 2 && !done; tt++){
            u32 w = first ^ tt; u32 Dj = (Dl >> j) & 1; u32 wp = w ^ Dj ^ ca; u32 can = (w & Dj) | (w & ca) | (Dj & ca);
            if (j == 31) can = 0;
            u32 x = ((d1 >> j) & 1) ^ w, xp = ((d1p >> j) & 1) ^ wp;
            u32 i = (u32)((j - 8) & 31); u32 Mi = (M >> i) & 1;
            if ((x ^ Mi ^ cz) != xp) continue;
            u32 czn = (x & Mi) | (x & cz) | (Mi & cz); if (i == 31) czn = 0;
            if (j == 7 && can != g) continue;
            int ns = can | (czn << 1);
            if (ok[t + 1][ns]) { a |= w << j; s = ns; done = 1; }
          }
          if (!done) { okw = 0; break; }
        }
        if (okw) { best = a; found = 1; }
      }
    }
  }
  if (count) *count = total;
  if (found && aout) *aout = best;
  return total ? 1 : 0;
}

/* ===== general rotation DP: solutions w of  ror(cp ^ (w + Dl), R) - ror(c ^ w, R) == M  (R in 1..31).
 * Used for D1(ii) (R = 8) and D3(i) (R = 16, c = v14, cp = v14', Dl = dv3, M = v9 - v9').
 * Returns number of solutions in *count and one random solution in *wout (if any). */
static int rotdp(u32 c, u32 cp, u32 Dl, int R, u32 M, u64 r, u32 *wout, u64 *count){
  int order[32]; for (int t = 0; t < 32; t++) order[t] = (t + R) & 31;
  u64 total = 0; int found = 0; u32 best = 0;
  for (u32 g = 0; g < 2; g++){
    u64 cnt[33][4]; memset(cnt, 0, sizeof cnt); cnt[0][g] = 1;
    unsigned char ok[33][4];
    for (int pass = 0; pass < 2; pass++){
      /* pass 0: forward counts; pass 1: backward reachability then sampling */
      if (pass == 1){
        if (!(cnt[32][0] | cnt[32][1] | cnt[32][2] | cnt[32][3]) || found || !wout) break;
        for (int s = 0; s < 4; s++) ok[32][s] = 1;
        for (int t = 31; t >= 0; t--){
          int j = order[t];
          for (int s = 0; s < 4; s++){
            u32 ca = s & 1, cz = s >> 1; ok[t][s] = 0;
            if (j == 0 && ca) continue;
            for (u32 w = 0; w < 2; w++){
              u32 Dj = (Dl >> j) & 1, wp = w ^ Dj ^ ca, can = (w & Dj) | (w & ca) | (Dj & ca);
              if (j == 31) can = 0;
              u32 x = ((c >> j) & 1) ^ w, xp = ((cp >> j) & 1) ^ wp;
              u32 i = (u32)((j - R) & 31), Mi = (M >> i) & 1;
              if ((x ^ Mi ^ cz) != xp) continue;
              u32 czn = (x & Mi) | (x & cz) | (Mi & cz); if (i == 31) czn = 0;
              if (j == ((R - 1) & 31) && can != g) continue;
              if (ok[t + 1][can | (czn << 1)]) { ok[t][s] = 1; break; }
            }
          }
        }
        if (!ok[0][g]) break;
        int s = g; u32 a = 0, good = 1;
        for (int t = 0; t < 32 && good; t++){
          int j = order[t]; u32 ca = s & 1, cz = s >> 1, first = (u32)((r >> t) & 1); int done = 0;
          for (u32 tt = 0; tt < 2 && !done; tt++){
            u32 w = first ^ tt, Dj = (Dl >> j) & 1, wp = w ^ Dj ^ ca, can = (w & Dj) | (w & ca) | (Dj & ca);
            if (j == 31) can = 0;
            u32 x = ((c >> j) & 1) ^ w, xp = ((cp >> j) & 1) ^ wp;
            u32 i = (u32)((j - R) & 31), Mi = (M >> i) & 1;
            if ((x ^ Mi ^ cz) != xp) continue;
            u32 czn = (x & Mi) | (x & cz) | (Mi & cz); if (i == 31) czn = 0;
            if (j == ((R - 1) & 31) && can != g) continue;
            int ns = can | (czn << 1);
            if (ok[t + 1][ns]) { a |= w << j; s = ns; done = 1; }
          }
          if (!done) good = 0;
        }
        if (good) { best = a; found = 1; }
        break;
      }
      for (int t = 0; t < 32; t++){
        int j = order[t];
        for (int s = 0; s < 4; s++){
          if (!cnt[t][s]) continue;
          u32 ca = s & 1, cz = s >> 1;
          if (j == 0 && ca) continue;
          for (u32 w = 0; w < 2; w++){
            u32 Dj = (Dl >> j) & 1, wp = w ^ Dj ^ ca, can = (w & Dj) | (w & ca) | (Dj & ca);
            if (j == 31) can = 0;
            u32 x = ((c >> j) & 1) ^ w, xp = ((cp >> j) & 1) ^ wp;
            u32 i = (u32)((j - R) & 31), Mi = (M >> i) & 1;
            if ((x ^ Mi ^ cz) != xp) continue;
            u32 czn = (x & Mi) | (x & cz) | (Mi & cz); if (i == 31) czn = 0;
            if (j == ((R - 1) & 31) && can != g) continue;
            cnt[t + 1][can | (czn << 1)] += cnt[t][s];
          }
        }
      }
    }
    total += cnt[32][0] + cnt[32][1] + cnt[32][2] + cnt[32][3];
  }
  if (count) *count = total;
  if (found && wout) *wout = best;
  return total ? 1 : 0;
}

#endif
