/* Freestanding C port of the bsrho.py generator of the rolled 5-round program (Gen, listing()), two passes per segment, no node table, no libc.  Exports run(), info_ptr(),
   code_ptr().  Segment 0 = rounds 1 and 2 (straight, outputs = 512 state planes in registers 256..767, temporaries from 768), then the complement of inverted planes, the
   message slots of round 3, the loop control, segment 1 = one generic round (state 256..767, message slots 768..1279, temporaries from 1312, outputs in place), the message
   permutation, the 256 output XORs.  No shared and no dead gate (hits 0, dead 0), so node numbers are creation order.  Pass 0 counts the uses of every node and records the
   register of every output node; pass 1 rebuilds the segment, an operand whose use count reaches 0 frees its register (temporaries only), a result takes its pinned register,
   else the lowest free one, else a new one.  Record = 36 bytes: op, dst, a, b as u16 LE (0xFFFF = none), rest zero.                                                          */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;

#ifndef NMAX
#define NMAX 10056                 /* nodes of the larger segment: constant 0, inputs, one per gate */
#endif
#ifndef CODE_BYTES
#define CODE_BYTES 795996
#endif
#define KPRE 2
#define N 256
#define SB 256
#define WB 768
#define TB 1312
#define REC 36
#define CTR_BYTES 16384
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u
#define NONE 0xFFFFu

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static u8 uses[NMAX];
static u16 pinreg[NMAX];
static u32 v[16][32], tmp[32], mw[32], fbits[32];

static u32 nn, calls, err, pass, kk, nxt, top, base, seg;
static struct { u32 ninst, nreg, nodes, calls, err, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};

static void put16(u8 *p, u32 w) { p[0] = (u8)w; p[1] = (u8)(w >> 8); }
static void emit(u32 op, u32 d, u32 a, u32 b) {            /* one instruction record */
  if (kk >= CODE_BYTES / REC) { err = 5; return; }
  u8 *rec = code + (u32)REC * kk++;
  rec[0] = (u8)op; put16(rec + 1, d); put16(rec + 3, a); put16(rec + 5, b);
}
static void drop(u32 s) {                                   /* one use of operand s is consumed (pass 1) */
  u32 n = NODE(s), c = uses[n] - 1u;
  uses[n] = (u8)c;
  if (c == 0 && REG(s) >= base) { u32 r = REG(s) - base; fbits[r >> 5] |= 1u << (r & 31); }
}
static u32 mk(u32 op, u32 x, u32 y) {                       /* a new gate of the operands' nodes; returns the positive signal */
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    u32 a = NODE(x), b = NODE(y);
    if (uses[a] == 255 || uses[b] == 255) { err = 6; return 0; }
    uses[a]++; uses[b]++;
    return id << 1;
  }
  u32 ra = REG(x), rb = REG(y), d;
  drop(x); drop(y);
  if (pinreg[id]) {
    d = pinreg[id];
    if (seg == 1 && uses[1 + d - SB] != 0) { err = 4; return 0; }    /* the input plane in this register is still needed after this gate */
  } else {
    u32 w = 0;
    while (w < 32 && fbits[w] == 0) w++;
    if (w < 32) { u32 b = 0; while (!((fbits[w] >> b) & 1u)) b++; fbits[w] &= ~(1u << b); d = base + 32 * w + b; }
    else d = nxt++;
  }
  if (d + 1 > top) top = d + 1;
  emit(op == 0 ? '^' : op == 1 ? '&' : '|', d, ra, rb);
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
    *sum = s; *carry = AND(xx ^ 1, t ^ 1) ^ 1; return;
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
static void xorrot(u32 *D, const u32 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  for (int i = 0; i < 32; i++) tmp[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = tmp[(i + r) & 31];
}
static void constw(u32 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (val >> i) & 1u; }
static u32 inp(u32 j, u32 r) { return ((1 + j) << 1) | (r << 17); }   /* input node 1 + j living in register r */
static u32 *msg(u32 w) {                                     /* message word slot w: segment 0: word w of 0^32 || x; segment 1: the plane slot w in the registers 768.. */
  for (u32 b = 0; b < 32; b++) mw[b] = seg == 1 ? inp(512 + 32 * w + b, WB + 32 * w + b) : w < 8 ? ZERO : inp(32 * (w - 8) + b, 32 * (w - 8) + b);
  return mw;
}
static void rounds(u32 *mi, int nr) {
  u32 nm[16];
  for (int r = 0; r < nr; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      add(v[a], v[b], v[a]); add(v[a], msg(mi[2 * j]), v[a]);
      xorrot(v[d], v[a], 16);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 12);
      add(v[a], v[b], v[a]); add(v[a], msg(mi[2 * j + 1]), v[a]);
      xorrot(v[d], v[a], 8);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 7);
    }
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
}
static void outputs(void) {                                 /* the 512 state planes are the outputs of the segment: plane 32 w + b is pinned to register 256 + 32 w + b */
  for (u32 j = 0; j < 512; j++) {
    u32 s = v[j >> 5][j & 31];
    if (!NODE(s)) { err = 3; return; }
    if (pass == 0) pinreg[NODE(s)] = (u16)(SB + j);
    else if (s & 1) { if (seg == 0) emit('~', SB + j, SB + j, NONE); else err = 7; }   /* complement of a plane stored inverted */
  }
}
static void segment(u32 sg, int nr, u32 b0, u32 first) {
  u32 mi[16];
  seg = sg; base = b0;
  for (int p = 0; p < 2; p++) {
    pass = (u32)p; nn = first;
    if (p == 0) { for (u32 i = 0; i < NMAX; i++) { uses[i] = 0; pinreg[i] = 0; } }
    else { for (u32 i = 0; i < 32; i++) fbits[i] = 0; nxt = b0; }
    for (int i = 0; i < 16; i++) mi[i] = (u32)i;
    if (sg == 0) {
      for (int i = 0; i < 8; i++) constw(v[i], IV[i]);
      for (int i = 0; i < 4; i++) constw(v[8 + i], IV[i]);
      constw(v[12], 0); constw(v[13], 0); constw(v[14], 64); constw(v[15], 11);
    } else {
      for (u32 w = 0; w < 16; w++) for (u32 b = 0; b < 32; b++) v[w][b] = inp(32 * w + b, SB + 32 * w + b);
    }
    rounds(mi, nr);
    outputs();
    if (err) return;
  }
}

__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }

__attribute__((export_name("run"))) int run(void) {
  u32 mi[16], nm[16];
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses + sizeof pinreg;
  info.sz_state = sizeof v + sizeof tmp + sizeof mw + sizeof fbits;
  err = 0; calls = 0; kk = 0; top = TB + 32;
  segment(0, KPRE, WB, 1 + N);                               /* nodes: the constant, 256 input planes, the gates */
  if (err) { info.err = err; return (int)err; }
  info.nodes = nn;
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;               /* message planes of round 3: slot s holds word mi[s] of 0^32 || x */
  for (int r = 0; r < KPRE; r++) { for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]]; for (int i = 0; i < 16; i++) mi[i] = nm[i]; }
  for (u32 s = 0; s < 16; s++) for (u32 b = 0; b < 32; b++) {
    if (mi[s] < 8) emit('z', WB + 32 * s + b, NONE, NONE); else emit('=', WB + 32 * s + b, 32 * (mi[s] - 8) + b, NONE);
  }
  emit('I', NONE, NONE, NONE);
  segment(1, 1, TB, 1 + 1024);
  if (err) { info.err = err; return (int)err; }
  if (nn > info.nodes) info.nodes = nn;
  emit('D', NONE, NONE, NONE); emit('C', NONE, NONE, NONE); emit('Z', NONE, NONE, NONE);
  for (u32 s0 = 0; s0 < 16; s0++) {                          /* slot s takes slot PERM[s]; one temporary word per cycle, cycles in order of their least slot */
    u32 skip = 0, s1 = PERM[s0];
    while (s1 != s0) { if (s1 < s0) skip = 1; s1 = PERM[s1]; }
    if (skip) continue;
    for (u32 b = 0; b < 32; b++) emit('=', TB + b, WB + 32 * s0 + b, NONE);
    u32 cur = s0;
    for (;;) {
      u32 nx = PERM[cur];
      for (u32 b = 0; b < 32; b++) emit('=', WB + 32 * cur + b, nx == s0 ? TB + b : WB + 32 * nx + b, NONE);
      if (nx == s0) break;
      cur = nx;
    }
  }
  emit('J', NONE, NONE, NONE);
  for (u32 j = 0; j < N; j++) emit('^', j, SB + j, SB + 256 + j);
  info.calls = calls;
  info.ninst = kk; info.nreg = top; info.err = err;
  return (int)err;
}
