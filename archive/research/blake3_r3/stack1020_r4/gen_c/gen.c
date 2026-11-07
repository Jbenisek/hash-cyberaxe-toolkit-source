/* GEN_C: C port of Gen / trace(256) / allocate, two passes, no node table (no shared, no dead gate), no libc.  Pass 0 counts the uses
   of each node (8 bits); pass 1 rebuilds, frees a register when its count reaches 0 (output j pinned to register j), writes 5-byte records
   (op byte, then dst, a, b as 10-bit fields).  Column choice by dry trials (dry = 1: counted, not recorded), as Gen.add3. */
typedef unsigned char u8; typedef unsigned int u32;
#ifndef NMAX
#define NMAX 23736
#endif
#ifndef CODE_BYTES
#define CODE_BYTES 135582
#endif
#define ROUNDS 4
#define N 256
#define REC 5
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[5248];
static u8 uses[NMAX + 1];
static u32 v[16][32], tmp[32], mw[32], fbits[24];
static u32 nn, calls, err, pass, kk, nxt, top, firstout, dry;
static struct { u32 ninst, nreg, nodes, calls, err, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 KEY[8] = {0x80000000u,0,0x80000000u,0,0x70000000u,0,0,0};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};
/* COLLIB: polarity key, oU, gate count, 9 gates (op 0 xor 1 and 2 or, i, j), outputs s, u', U' (node or 255, polarity flip) */
static const u8 LIB[4][36] = {
 {16,0,9, 0,0,4, 0,1,5, 0,1,2, 0,3,5, 2,6,7, 0,2,6, 1,4,8, 0,5,9, 0,9,11, 10,1, 12,0, 13,0},
 {16,1,8, 0,1,4, 0,3,5, 0,0,2, 0,2,5, 2,7,8, 1,4,6, 0,0,8, 0,9,10, 0,0,0, 11,1, 255,0, 12,0},
 {7,0,9,  0,0,2, 0,1,5, 0,3,6, 0,0,1, 2,4,7, 2,5,8, 0,6,9, 0,9,10, 0,4,6, 13,1, 11,0, 12,1},
 {7,1,8,  0,1,2, 0,0,5, 0,0,1, 2,5,7, 0,4,6, 0,3,9, 2,4,10, 0,8,11, 0,0,0, 9,1, 255,0, 12,1}};

static void put32(u8 *p, u32 w) { p[0] = (u8)w; p[1] = (u8)(w >> 8); p[2] = (u8)(w >> 16); p[3] = (u8)(w >> 24); }
static void drop(u32 s) {
  u32 n = NODE(s), c = uses[n] - 1u;
  uses[n] = (u8)c;
  if (c == 0 && REG(s) >= N) { u32 r = REG(s) - N; fbits[r >> 5] |= 1u << (r & 31); }
}
static u32 mk(u32 op, u32 x, u32 y) {
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++;
  if (dry) return id << 1;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    u32 a = NODE(x), b = NODE(y);
    if (uses[a] == 255 || uses[b] == 255) { err = 6; return 0; }
    uses[a]++; uses[b]++;
    return id << 1;
  }
  u32 ra = REG(x), rb = REG(y), d;
  drop(x); drop(y);
  if (id >= firstout) {
    d = id - firstout;
    if (uses[1 + d] != 0) { err = 4; return 0; }
  } else {
    u32 w = 0;
    while (w < 24 && fbits[w] == 0) w++;
    if (w < 24) { u32 b = 0; while (!((fbits[w] >> b) & 1u)) b++; fbits[w] &= ~(1u << b); d = N + 32 * w + b; }
    else d = nxt++;
  }
  if (d + 1 > top) top = d + 1;
  if (kk >= CODE_BYTES / REC) { err = 5; return 0; }
  u8 *rec = code + (u32)REC * kk++;
  rec[0] = op == 0 ? '^' : op == 1 ? '&' : '|';
  if (d >= 1024 || ra >= 1024 || rb >= 1024) { err = 7; return 0; }
  put32(rec + 1, d | (ra << 10) | (rb << 20));
  return (id << 1) | (d << 17);
}
static u32 XOR(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return y ^ (x & 1);
  if (!NODE(y)) return x ^ (y & 1);
  if (NODE(x) == NODE(y)) return (x ^ y) & 1;
  return mk(0, x, y) ^ ((x ^ y) & 1);
}
static u32 AND(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return (x & 1) == 0 ? ZERO : y;
  if (!NODE(y)) return (y & 1) == 0 ? ZERO : x;
  if (NODE(x) == NODE(y)) return x == y ? x : ZERO;
  if (!(x & 1) && !(y & 1)) return mk(1, x, y);
  if ((x & 1) && (y & 1)) return mk(2, x, y) | 1;
  u32 p = (x & 1) == 0 ? x : y, q = (x & 1) == 0 ? y : x;
  return XOR(p, mk(1, p, q));
}
static u32 OR(u32 x, u32 y) { return AND(x ^ 1, y ^ 1) ^ 1; }
static void fa(u32 a, u32 b, u32 c, u32 *sum, u32 *carry) {
  u32 ops[3] = {a, b, c}, vs[3], nv = 0, k = 0, nc = 0, cs[3] = {0, 0, 0};
  for (int i = 0; i < 3; i++) {
    if (!NODE(ops[i])) { cs[nc++] = ops[i] & 1; k ^= ops[i] & 1; } else vs[nv++] = ops[i];
  }
  if (nv == 3) {
    u32 p = 0, x = 0, y = 0;
    for (int pi = 0; pi < 3; pi++) {
      u32 o0 = vs[pi == 0 ? 1 : 0], o1 = vs[pi == 2 ? 1 : 2];
      if ((o0 & 1) == (o1 & 1)) { p = vs[pi]; x = o0; y = o1; break; }
    }
    u32 u = XOR(x, p);
    u32 s = XOR(u, y);
    u32 w = XOR(y, p);
    u32 an = AND(u, w);
    *sum = s; *carry = XOR(an, p); return;
  }
  if (nv == 2) {
    u32 x = vs[0], y = vs[1];
    u32 t = XOR(x, y);
    u32 s = t ^ k;
    if ((x & 1) == (y & 1)) {
      if (k == 0) { *sum = s; *carry = AND(x, y); return; }
      *sum = s; *carry = AND(x ^ 1, y ^ 1) ^ 1; return;
    }
    u32 nt = t ^ 1;
    u32 xx = (x & 1) == (nt & 1) ? x : y;
    if (k == 0) { *sum = s; *carry = AND(xx, nt); return; }
    u32 yy = (x & 1) == (t & 1) ? x : y;                  /* k = 1, opposite polarities: carry = yy OR (x XOR y) */
    *sum = s; *carry = AND(yy ^ 1, t ^ 1) ^ 1; return;
  }
  if (nv == 1) {
    u32 x = vs[0], k1 = cs[0], k2 = cs[1];
    *sum = x ^ k; *carry = (k1 == 1 && k2 == 1) ? ONE : (k1 == 0 && k2 == 0) ? ZERO : x; return;
  }
  u32 kk3 = cs[0] + cs[1] + cs[2];
  *sum = (kk3 % 2 == 0) ? ZERO : ONE; *carry = kk3 >= 2 ? ONE : ZERO;
}
static void add(const u32 *A, const u32 *B, u32 *out) {   /* out may alias A */
  u32 c = ZERO;
  for (int i = 0; i < 32; i++) {
    if (i == 31) out[i] = XOR(XOR(A[i], B[i]), c);
    else { u32 si; fa(A[i], B[i], c, &si, &c); out[i] = si; }
  }
}
static void col(u32 x, u32 y, u32 z, u32 u, u32 U, int tm, int oU, u32 *s, u32 *uo, u32 *Uo) {   /* Gen._col */
  if (tm == 2) {
    u32 key = (x & 1) | (y & 1) << 1 | (z & 1) << 2 | (u & 1) << 3 | (U & 1) << 4, e = 0;
    while (e < 4 && !(LIB[e][0] == key && LIB[e][1] == (u32)oU)) e++;
    if (e == 4) tm = 0;
    else {
      const u8 *L = LIB[e];
      u32 nd[14] = {x & ~1u, y & ~1u, z & ~1u, u & ~1u, U & ~1u};
      for (u32 g = 0; g < L[2]; g++) {
        const u8 *G = L + 3 + 3 * g;
        nd[5 + g] = G[0] == 0 ? XOR(nd[G[1]], nd[G[2]]) : G[0] == 1 ? AND(nd[G[1]], nd[G[2]]) : OR(nd[G[1]], nd[G[2]]);
      }
      *s = nd[L[30]] ^ L[31];
      if (L[32] != 255) *uo = nd[L[32]] ^ L[33];
      *Uo = nd[L[34]] ^ L[35];
      return;
    }
  }
  if (tm) {
    u32 w = XOR(y, U), n8 = XOR(z, w);
    *s = XOR(x, n8);
    u32 t1 = XOR(y, u), n6 = OR(U, t1);
    if (!oU) *uo = XOR(n6, w);
    u32 t2 = XOR(x, w), t3 = AND(n8, t2);
    *Uo = XOR(n6, t3);
  } else {
    u32 n5 = XOR(z, U), n9 = XOR(x, n5);
    *s = XOR(y, n9);
    u32 n6 = XOR(x, y), t1 = XOR(z, u), n8 = OR(U, t1), n11 = AND(n6 ^ 1, n9);
    if (!oU) *uo = XOR(n5, n11);
    *Uo = XOR(n8, n11);
  }
}
static void add3(const u32 *A, const u32 *B, const u32 *C, u32 *out) {   /* Gen.add3; out may alias A */
  u32 U, u = ZERO, s, uo = 0, Uo, s0;
  fa(A[0], B[0], C[0], &s0, &U);
  out[0] = s0;
  for (int i = 1; i < 31; i++) {
    u32 a = A[i], b = B[i], c = C[i];
    u32 o[6][3] = {{a, b, c}, {a, c, b}, {b, a, c}, {b, c, a}, {c, a, b}, {c, b, a}};
    u32 bk = 1000, bo = 0, bt = 0;
    for (u32 j = 0; j < 6; j++)
      for (u32 tm = 0; tm < 3; tm++) {
        u32 n0 = nn;
        dry = 1; col(o[j][0], o[j][1], o[j][2], u, U, (int)tm, i == 30, &s, &uo, &Uo); dry = 0;
        u32 k = nn - n0; nn = n0;
        if (k < bk) { bk = k; bo = j; bt = tm; }
      }
    col(o[bo][0], o[bo][1], o[bo][2], u, U, (int)bt, i == 30, &s, &uo, &Uo);
    out[i] = s; u = uo; U = Uo;
  }
  out[31] = XOR(XOR(XOR(A[31], B[31]), C[31]), U);
}
static int allvar(const u32 *A) { for (int i = 0; i < 32; i++) if (!NODE(A[i])) return 0; return 1; }
static void s3(u32 *a, const u32 *b, const u32 *m) {      /* a = a + b + m */
  if (allvar(a) && allvar(b) && allvar(m)) add3(a, b, m, a);
  else { add(a, b, a); add(a, m, a); }
}
static void xorrot(u32 *D, const u32 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  for (int i = 0; i < 32; i++) tmp[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = tmp[(i + r) & 31];
}
static void constw(u32 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (val >> i) & 1u; }
static u32 inp(u32 j) { return ((1 + j) << 1) | (j << 17); }
static u32 *msg(u32 w) {                                  /* message word w of KEY || x */
  if (w < 8) constw(mw, KEY[w]); else for (u32 b = 0; b < 32; b++) mw[b] = inp(32 * (w - 8) + b);
  return mw;
}
static void trace(void) {
  u32 mi[16], nm[16];
  nn = 1 + N;
  for (int i = 0; i < 8; i++) constw(v[i], IV[i]);
  for (int i = 0; i < 4; i++) constw(v[8 + i], IV[i]);
  constw(v[12], 0); constw(v[13], 0); constw(v[14], 64); constw(v[15], 11);
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;
  for (int r = 0; r < ROUNDS; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      s3(v[a], v[b], msg(mi[2 * j]));
      xorrot(v[d], v[a], 16);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 12);
      s3(v[a], v[b], msg(mi[2 * j + 1]));
      xorrot(v[d], v[a], 8);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 7);
    }
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
  firstout = nn;                                           /* the 256 output gates are the last 256 gates, in order */
  for (u32 j = 0; j < N; j++) {
    u32 s = XOR(v[j >> 5][j & 31], v[(j >> 5) + 8][j & 31]);
    if (!NODE(s) || NODE(s) != firstout + j) err = 3;
    info.q[j >> 3] |= (u8)((s & 1) << (j & 7));
  }
}
__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }
__attribute__((export_name("run"))) int run(void) {
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses;
  info.sz_state = sizeof v + sizeof tmp + sizeof mw + sizeof fbits;
  err = 0; calls = 0; pass = 0; kk = 0; nxt = N; top = N; dry = 0;
  trace();
  info.nodes = nn;
  if (err) { info.err = err; return (int)err; }
  pass = 1;
  trace();
  info.calls = calls;
  info.ninst = kk; info.nreg = top; info.err = err;
  return (int)err;
}
