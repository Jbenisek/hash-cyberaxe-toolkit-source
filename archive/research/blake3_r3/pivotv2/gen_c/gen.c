/* Freestanding C port of the bsrho.py circuit generator (Gen / trace(256) / Step DCE / allocate).
   No libc, no malloc, no imports.  Exports: run(), info_ptr(), code_ptr().
   Static memory map:
     code region  687,060 B (final main-code size of the entry; 36-byte records: op, dst, a, b as u16 LE)
     counters      16,384 B
     nodes          4 B/node  (2-bit op | 15-bit a | 15-bit b), op 0 xor, 1 and, 2 or, 3 leaf (node 0 const, 1..256 inputs)
     union scratch: trace phase  hash 2^15 x 2 B + signal state (v, m, tmp)
                    emit  phase  mark 1 B + last 4 B + reg 2 B per node + heap 1024 x 2 B
     outs[256] uint16 output signals (node<<1|neg)                                                       */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;

#ifndef NMAX
#define NMAX 17495
#endif
#define N 256
#define REC 36
#define CODE_BYTES 687060
#define CTR_BYTES 16384
#define HASHN 32768
#define HEAPN 1024

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static u32 nodes[NMAX];
static u16 outs[N];

typedef struct { u16 hash[HASHN]; u16 v[16][32]; u16 m[16][32]; u16 tmp[32]; } TraceScr;
typedef struct { u8 mark[NMAX]; u32 last[NMAX]; u16 reg[NMAX]; u16 heap[HEAPN]; } EmitScr;
static union { TraceScr t; EmitScr e; } S;

static u32 nn, calls, err, hsz;
static struct {
  u32 ninst, nreg, nodes, calls, err, maxheap, maxprobe, hashfill; u8 q[32];
  u32 sz_code, sz_ctr, sz_nodes, sz_outs, sz_trace_scr, sz_emit_scr, sz_union, sz_hash, sz_state, sz_heap;
} info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};

#define ZERO 0
#define ONE 1

static u32 mk(u32 op, u32 a, u32 b) {
  calls++;
  if (a > b) { u32 t = a; a = b; b = t; }
  u32 key = (op << 30) | (a << 15) | b;
  u32 h = (key * 0x9E3779B1u) >> 17;           /* 15 bits */
  u32 probes = 0;
  for (;;) {
    u32 e = S.t.hash[h];
    if (e == 0) {
      if (nn >= NMAX) { err = 1; return 0; }
      nodes[nn] = key; S.t.hash[h] = (u16)nn;
      if (probes > info.maxprobe) info.maxprobe = probes;
      return nn++;
    }
    if (nodes[e] == key) { if (probes > info.maxprobe) info.maxprobe = probes; return e; }
    h = (h + 1) & (HASHN - 1); probes++;
  }
}
static u16 XOR(u16 x, u16 y) {
  calls++;
  if (!(x >> 1)) return (u16)(y ^ (x & 1));
  if (!(y >> 1)) return (u16)(x ^ (y & 1));
  if ((x >> 1) == (y >> 1)) return (u16)((x ^ y) & 1);
  u32 n = mk(0, x >> 1, y >> 1);
  return (u16)((n << 1) | ((x ^ y) & 1));
}
static u16 AND(u16 x, u16 y) {
  calls++;
  if (!(x >> 1)) return (x & 1) == 0 ? ZERO : y;
  if (!(y >> 1)) return (y & 1) == 0 ? ZERO : x;
  if ((x >> 1) == (y >> 1)) return x == y ? x : ZERO;
  if (!(x & 1) && !(y & 1)) return (u16)(mk(1, x >> 1, y >> 1) << 1);
  if ((x & 1) && (y & 1)) return (u16)((mk(2, x >> 1, y >> 1) << 1) | 1);
  u16 p = (x & 1) == 0 ? x : y, q = (x & 1) == 0 ? y : x;
  u16 an = (u16)(mk(1, p >> 1, q >> 1) << 1);
  return XOR(p, an);
}
static void fa(u16 a, u16 b, u16 c, u16 *sum, u16 *carry) {
  u16 ops[3] = {a, b, c}, vs[3]; u32 nv = 0, k = 0, nc = 0, cs[3] = {0, 0, 0};
  for (int i = 0; i < 3; i++) {
    if (!(ops[i] >> 1)) { cs[nc++] = ops[i] & 1; k ^= ops[i] & 1; } else vs[nv++] = ops[i];
  }
  if (nv == 3) {
    u16 p = 0, x = 0, y = 0;
    for (int pi = 0; pi < 3; pi++) {
      u16 o0 = vs[pi == 0 ? 1 : 0], o1 = vs[pi == 2 ? 1 : 2];
      if ((o0 & 1) == (o1 & 1)) { p = vs[pi]; x = o0; y = o1; break; }
    }
    u16 u = XOR(x, p);
    u16 s = XOR(u, y);
    u16 w = XOR(y, p);
    u16 an = AND(u, w);
    u16 cr = XOR(an, p);
    *sum = s; *carry = cr; return;
  }
  if (nv == 2) {
    u16 x = vs[0], y = vs[1];
    u16 t = XOR(x, y);
    u16 s = (u16)(t ^ k);
    if ((x & 1) == (y & 1)) {
      if (k == 0) { u16 cr = AND(x, y); *sum = s; *carry = cr; return; }
      u16 cr = AND((u16)(x ^ 1), (u16)(y ^ 1));
      *sum = s; *carry = (u16)(cr ^ 1); return;
    }
    u16 nt = (u16)(t ^ 1);
    u16 xx = (x & 1) == (nt & 1) ? x : y;
    if (k == 0) { u16 cr = AND(xx, nt); *sum = s; *carry = cr; return; }
    u16 cr = AND((u16)(xx ^ 1), (u16)(t ^ 1));
    *sum = s; *carry = (u16)(cr ^ 1); return;
  }
  if (nv == 1) {
    u16 x = vs[0]; u32 k1 = cs[0], k2 = cs[1];
    *sum = (u16)(x ^ k); *carry = (k1 == 1 && k2 == 1) ? ONE : (k1 == 0 && k2 == 0) ? ZERO : x; return;
  }
  u32 kk = cs[0] + cs[1] + cs[2];
  *sum = (kk % 2 == 0) ? ZERO : ONE; *carry = kk >= 2 ? ONE : ZERO;
}
static void add(const u16 *A, const u16 *B, u16 *out) {   /* out may alias A */
  u16 c = ZERO;
  for (int i = 0; i < 32; i++) {
    if (i == 31) { u16 t = XOR(A[i], B[i]); out[i] = XOR(t, c); }
    else { u16 si; fa(A[i], B[i], c, &si, &c); out[i] = si; }
  }
}
static void xorrot(u16 *D, const u16 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  u16 *t = S.t.tmp;
  for (int i = 0; i < 32; i++) t[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = t[(i + r) & 31];
}
static void constw(u16 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (u16)((val >> i) & 1); }

static void trace(void) {
  u32 mi[16];
  for (int i = 0; i < HASHN; i++) S.t.hash[i] = 0;
  calls = 0;
  nodes[0] = 3u << 30; nn = 1;                                       /* const node 0 (leaf) */
  for (int j = 0; j < N; j++) nodes[nn++] = (3u << 30) | (u32)j;     /* input j -> node 1+j */
  for (int i = 0; i < 8; i++) constw(S.t.m[i], 0);
  for (int i = 0; i < 8; i++) for (int b = 0; b < 32; b++) S.t.m[8 + i][b] = (u16)((1 + 32 * i + b) << 1);
  for (int i = 0; i < 8; i++) constw(S.t.v[i], IV[i]);
  for (int i = 0; i < 4; i++) constw(S.t.v[8 + i], IV[i]);
  constw(S.t.v[12], 0); constw(S.t.v[13], 0); constw(S.t.v[14], 64); constw(S.t.v[15], 11);
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;
  for (int r = 0; r < 3; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      const u16 *x = S.t.m[mi[2 * j]], *y = S.t.m[mi[2 * j + 1]];
      add(S.t.v[a], S.t.v[b], S.t.v[a]); add(S.t.v[a], x, S.t.v[a]);
      xorrot(S.t.v[d], S.t.v[a], 16);
      add(S.t.v[c], S.t.v[d], S.t.v[c]);
      xorrot(S.t.v[b], S.t.v[c], 12);
      add(S.t.v[a], S.t.v[b], S.t.v[a]); add(S.t.v[a], y, S.t.v[a]);
      xorrot(S.t.v[d], S.t.v[a], 8);
      add(S.t.v[c], S.t.v[d], S.t.v[c]);
      xorrot(S.t.v[b], S.t.v[c], 7);
    }
    u32 nm[16];
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
  for (int i = 0; i < 8; i++) for (int b = 0; b < 32; b++) outs[32 * i + b] = XOR(S.t.v[i][b], S.t.v[i + 8][b]);
}

static void hpush(u16 v) {
  if (hsz >= HEAPN) { err = 2; return; }
  u16 *h = S.e.heap; u32 i = hsz++;
  if (hsz > info.maxheap) info.maxheap = hsz;
  while (i > 0) { u32 p = (i - 1) >> 1; if (h[p] <= v) break; h[i] = h[p]; i = p; }
  h[i] = v;
}
static u16 hpop(void) {
  u16 *h = S.e.heap; u16 top = h[0]; u16 v = h[--hsz]; u32 i = 0;
  for (;;) {
    u32 c = 2 * i + 1; if (c >= hsz) break;
    if (c + 1 < hsz && h[c + 1] < h[c]) c++;
    if (h[c] >= v) break;
    h[i] = h[c]; i = c;
  }
  if (hsz) h[i] = v;
  return top;
}
static void put16(u8 *p, u32 v) { p[0] = (u8)v; p[1] = (u8)(v >> 8); }

__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }

__attribute__((export_name("run"))) int run(void) {
  err = 0; info.maxprobe = 0; info.maxheap = 0;
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_nodes = sizeof nodes; info.sz_outs = sizeof outs;
  info.sz_trace_scr = sizeof(TraceScr); info.sz_emit_scr = sizeof(EmitScr); info.sz_union = sizeof S;
  info.sz_hash = sizeof(((TraceScr *)0)->hash); info.sz_state = sizeof(TraceScr) - info.sz_hash; info.sz_heap = HEAPN * 2;
  trace();
  info.calls = calls; info.nodes = nn;
  if (err) { info.err = err; return 1; }
  for (int j = 0; j < N; j++) if (!(outs[j] >> 1)) { info.err = 3; return 3; }
  for (int j = 0; j < 32; j++) info.q[j] = 0;
  for (int j = 0; j < N; j++) info.q[j >> 3] |= (u8)((outs[j] & 1) << (j & 7));
  u32 fill = 0; for (u32 i = 0; i < HASHN; i++) fill += S.t.hash[i] != 0; info.hashfill = fill;
  /* emit phase reuses the scratch union */
  for (u32 k = 0; k < nn; k++) { S.e.mark[k] = 0; S.e.last[k] = 0xFFFFFFFFu; S.e.reg[k] = 0; }
  for (u32 j = 0; j < HEAPN; j++) S.e.heap[j] = 0;
  for (int j = 0; j < N; j++) S.e.mark[outs[j] >> 1] = 1;
  for (u32 k = nn - 1; k >= 1; k--) {
    if (S.e.mark[k] && (nodes[k] >> 30) != 3) { S.e.mark[(nodes[k] >> 15) & 0x7FFF] = 1; S.e.mark[nodes[k] & 0x7FFF] = 1; }
  }
  for (int j = 0; j < N; j++) { u32 nd = outs[j] >> 1; S.e.mark[nd] |= 2; S.e.reg[nd] = (u16)j; }   /* output flag; last j wins */
  for (int j = 0; j < N; j++) S.e.reg[1 + j] = (u16)j;                                           /* input plane j in register j */
  u32 ng = 0;
  for (u32 k = 1; k < nn; k++) {
    if (S.e.mark[k] && (nodes[k] >> 30) != 3) {
      S.e.last[(nodes[k] >> 15) & 0x7FFF] = ng; S.e.last[nodes[k] & 0x7FFF] = ng; ng++;
    }
  }
  /* register allocation, in node order */
  hsz = 0;
  u32 nxt = N, top = N, kk = 0;
  for (u32 k = 1; k < nn; k++) {
    u32 op = nodes[k] >> 30;
    if (!S.e.mark[k] || op == 3) continue;
    u32 a = (nodes[k] >> 15) & 0x7FFF, b = nodes[k] & 0x7FFF;
    u32 ra = S.e.reg[a], rb = S.e.reg[b];
    if (S.e.last[a] == kk && !(S.e.mark[a] & 2) && ra >= N) hpush((u16)ra);
    if (b != a && S.e.last[b] == kk && !(S.e.mark[b] & 2) && rb >= N) hpush((u16)rb);
    u32 d;
    if (S.e.mark[k] & 2) {
      d = S.e.reg[k];
      if ((int)S.e.last[1 + d] > (int)kk && S.e.last[1 + d] != 0xFFFFFFFFu) { info.err = 4; return 4; }
    } else if (hsz) d = hpop();
    else d = nxt++;
    S.e.reg[k] = (u16)d;
    if (d + 1 > top) top = d + 1;
    if (kk >= CODE_BYTES / REC) { info.err = 5; return 5; }
    u8 *rec = code + (u32)REC * kk;
    rec[0] = op == 0 ? '^' : op == 1 ? '&' : '|';
    put16(rec + 1, d); put16(rec + 3, ra); put16(rec + 5, rb);
    kk++;
  }
  info.ninst = kk; info.nreg = top; info.err = err;
  return err;
}
