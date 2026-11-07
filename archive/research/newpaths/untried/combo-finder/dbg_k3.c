/* dbg_k3.c -- print one K3 solution step by step against the real G */
#include "b3lc.h"
int main(void){
  g_rng = 12345;
  for (u64 tries = 0;; tries++){
    u32 h3 = (u32)rnd64(), h7 = (u32)rnd64(), flags = (u32)(rnd64() & 15), A = (u32)rnd64(), delta = (u32)rnd64();
    K3sol s;
    if (!k3_try(h7, flags, A, delta, &s, 1)) continue;
    u32 m6 = A - h3 - h7, m7 = s.m7base;
    /* manual both sides */
    for (int side = 0; side < 2; side++){
      u32 x = side ? m6 + delta : m6;
      u32 a1 = h3 + h7 + x, d1 = ror32(flags ^ a1, 16), c1 = B3IV[3] + d1, b1 = ror32(h7 ^ c1, 12);
      u32 a2 = a1 + b1 + m7, d2 = ror32(d1 ^ a2, 8), c2 = c1 + d2, b2 = ror32(b1 ^ c2, 7);
      printf("side %d: a1 %08x d1 %08x c1 %08x b1 %08x | a2 %08x d2 %08x c2 %08x b2 %08x\n", side, a1, d1, c1, b1, a2, d2, c2, b2);
    }
    printf("model: A %08x delta %08x D %08x a2 %08x v3 %08x v3p %08x v7 %08x v11 %08x v11p %08x v15 %08x nsol %llu\n",
           A, delta, s.D, s.a2, s.v3, s.v3p, s.v7, s.v11, s.v11p, s.v15, (unsigned long long)s.nsol);
    /* recheck pieces */
    u32 Ap = A + delta;
    u32 d1 = ror32(flags ^ A, 16), d1p = ror32(flags ^ Ap, 16);
    u32 c1 = B3IV[3] + d1, c1p = B3IV[3] + d1p;
    u32 b1 = ror32(h7 ^ c1, 12), b1p = ror32(h7 ^ c1p, 12);
    u32 a2 = s.a2, a2p = a2 + s.D;
    printf("check (a): a2^a2p %08x vs d1^d1p %08x\n", a2 ^ a2p, d1 ^ d1p);
    u32 d2 = ror32(d1 ^ a2, 8), d2p = ror32(d1p ^ a2p, 8);
    printf("d2 %08x d2p %08x ; (c1+d2)^(c1p+d2) %08x vs b1^b1p %08x\n", d2, d2p, (c1 + d2) ^ (c1p + d2), b1 ^ b1p);
    break;
  }
  return 0;
}
