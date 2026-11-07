/* Freestanding C port of the bsrho.py circuit generator for the 5-round target (Gen / trace(256) / allocate), in two passes and without a node table.
   No libc, no malloc, no imports.  Exports: run(), info_ptr(), code_ptr().
   The straight line has no shared gate and no dead gate at this target (the reference generator with a hash-consing table finds 0 hits), so a gate is a
   new node every time and the node numbers are the creation order.  Pass 0 builds the circuit and counts the uses of every node (8 bits per node).
   Pass 1 builds the same circuit again; every signal carries its register, so no node table is needed: an operand whose use count reaches zero frees
   its register (registers 256 and above; the output planes are pinned: output plane j in register j, the register of input plane j), the result takes
   the lowest free register or a new one, and the instruction record is written: a gate of two operands is the op byte then dst, a, b as three 10-bit
   fields of a u32 LE (5 bytes); the select s ? a : b is the op byte '?' then dst, s, a, b as four 10-bit fields of a 40-bit LE word (6 bytes).
   Static memory map (all inside the guest, at 5 rounds):
     code region   CODE_BYTES   final main-code size of the entry (5-byte and 6-byte records for the gates)
     counters      16,384 B     (reserved as in the machine layout)
     uses          NMAX + 1 B   8-bit use counts (8-bit counts suffice)
     state         v[16][32] u32 = 2,048 B, tmp[32] and mw[32] u32 = 256 B, free-register bitmap fbits[24] u32 = 96 B, info                       */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;

#ifndef NMAX
#define NMAX 21543                 /* nodes: constant 0, 256 inputs, one per gate */
#endif
#ifndef CODE_BYTES
#define CODE_BYTES 160680
#endif
#define ROUNDS 5
#define N 256
#define CTR_BYTES 16384
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static u8 uses[NMAX + 1];
static u32 v[16][32], tmp[32], mw[32], fbits[24];

static u32 nn, calls, err, pass, kk, cb, nxt, top, firstout;
static struct { u32 ninst, nreg, nodes, calls, err, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};

static u32 getu(u32 n) { return uses[n]; }
static void setu(u32 n, u32 c) { uses[n] = (u8)c; }
static void put32(u8 *p, u32 w) { p[0] = (u8)w; p[1] = (u8)(w >> 8); p[2] = (u8)(w >> 16); p[3] = (u8)(w >> 24); }

static void drop(u32 s) {                                   /* one use of operand s is consumed (pass 1) */
  u32 n = NODE(s), c = getu(n) - 1;
  setu(n, c);
  if (c == 0 && REG(s) >= N) { u32 r = REG(s) - N; fbits[r >> 5] |= 1u << (r & 31); }
}
static u32 gate(u32 op, const u32 *o, u32 no) {             /* a new gate (op 0 ^, 1 &, 2 |, 3 select) of the operands' nodes; returns the positive signal */
  u32 id = nn++, r[3], d;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    for (u32 i = 0; i < no; i++) if (getu(NODE(o[i])) == 255) { err = 6; return 0; }
    for (u32 i = 0; i < no; i++) setu(NODE(o[i]), getu(NODE(o[i])) + 1);
    return id << 1;
  }
  for (u32 i = 0; i < no; i++) r[i] = REG(o[i]);
  for (u32 i = 0; i < no; i++) drop(o[i]);
  if (id >= firstout) {
    d = id - firstout;
    if (getu(1 + d) != 0) { err = 4; return 0; }            /* input plane d is still needed after this gate */
  } else {
    u32 w = 0;
    while (w < 24 && fbits[w] == 0) w++;
    if (w < 24) { u32 b = 0; while (!((fbits[w] >> b) & 1u)) b++; fbits[w] &= ~(1u << b); d = N + 32 * w + b; }
    else d = nxt++;
  }
  if (d + 1 > top) top = d + 1;
  u32 rl = no == 3 ? 6 : 5;
  if (cb + rl > CODE_BYTES) { err = 5; return 0; }
  u8 *rec = code + cb; cb += rl; kk++;
  rec[0] = op == 0 ? '^' : op == 1 ? '&' : op == 2 ? '|' : '?';
  if (d >= 1024 || r[0] >= 1024 || r[1] >= 1024 || (no == 3 && r[2] >= 1024)) { err = 7; return 0; }
  put32(rec + 1, d | (r[0] << 10) | (r[1] << 20) | (no == 3 ? (r[2] & 3u) << 30 : 0));
  if (no == 3) rec[5] = (u8)(r[2] >> 2);                  /* 48-bit record: opcode byte, then four 10-bit register numbers */
  return (id << 1) | (d << 17);
}
static u32 mk(u32 op, u32 x, u32 y) {
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 o[2] = {x, y};
  return gate(op, o, 2);
}
static u32 SEL(u32 s, u32 a, u32 b) {                      /* s ? a : b, a and b of equal polarity; a selector of polarity 1 swaps a and b */
  calls++;
  if (s & 1) { u32 t = a; a = b; b = t; }
  if (!NODE(s) || !NODE(a) || !NODE(b) || (a & 1) != (b & 1)) { err = 8; return 0; }
  if (NODE(a) == NODE(b)) return a;
  calls++;
  u32 o[3] = {s, a, b};
  return gate(3, o, 3) | (a & 1);
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
  if (nv == 3) {                                           /* z, x of equal polarity, y the third: sum = (x ^ y) ^ z, carry = (x ^ y) ? z : x */
    u32 zi = 1, xi = 2;
    if ((vs[0] & 1) == (vs[1] & 1)) { zi = 0; xi = 1; } else if ((vs[0] & 1) == (vs[2] & 1)) { zi = 0; xi = 2; }
    u32 z = vs[zi], x = vs[xi], y = vs[3 - zi - xi];
    u32 tt = XOR(x, y);
    if (!NODE(tt)) { err = 9; return; }
    u32 s = XOR(tt, z);
    *sum = s; *carry = SEL(tt, z, x); return;
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
static u32 inp(u32 j) { return ((1 + j) << 1) | (j << 17); }
static u32 *msg(u32 w) { for (u32 b = 0; b < 32; b++) mw[b] = w < 8 ? ZERO : inp(32 * (w - 8) + b); return mw; }   /* message word w of 0^32 || x */

static void trace(void) {                                  /* the 5-round network of the block 0^32 || x */
  u32 mi[16], nm[16];
  nn = 1 + N;
  for (int i = 0; i < 8; i++) constw(v[i], IV[i]);
  for (int i = 0; i < 4; i++) constw(v[8 + i], IV[i]);
  constw(v[12], 0); constw(v[13], 0); constw(v[14], 64); constw(v[15], 11);
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;
  for (int r = 0; r < ROUNDS; r++) {
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
  firstout = nn;                                           /* the 256 output gates are the last 256 gates, in order, none constant */
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
  err = 0; calls = 0; pass = 0; kk = 0; cb = 0; nxt = N; top = N;
  trace();
  info.nodes = nn;
  if (err) { info.err = err; return (int)err; }
  pass = 1;
  trace();
  info.calls = calls;
  info.ninst = kk; info.nreg = top; info.err = err;
  return (int)err;
}
