"""Patch gen_c/gen.c (C generator of 0ecdfe35) for the select-gate full adder; 5-byte records for 2-input gates, 6-byte records for the select.
usage: python -B patch_genc.py <NMAX> <CODE_BYTES>"""
import os, sys
H = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(H, "gen_c", "gen.c")
t = open(P, encoding="utf-8", newline="").read()


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


rep("""   the lowest free register or a new one, and the instruction record (op byte, then dst, a, b as three 10-bit fields of a u32 LE: a 5-byte record) is written.""",
    """   the lowest free register or a new one, and the instruction record is written: a gate of two operands is the op byte then dst, a, b as three 10-bit
   fields of a u32 LE (5 bytes); the select s ? a : b is the op byte '?' then dst, s, a, b as four 10-bit fields of a 40-bit LE word (6 bytes).""")
rep("     code region   CODE_BYTES   final main-code size of the entry (5-byte records for the gates)",
    "     code region   CODE_BYTES   final main-code size of the entry (5-byte and 6-byte records for the gates)")
rep("#define NMAX 24679 ", "#define NMAX %s " % sys.argv[1])
rep("#define CODE_BYTES 170020", "#define CODE_BYTES %s" % sys.argv[2])
rep("#define REC 5\n", "")
rep("static u32 nn, calls, err, pass, kk, nxt, top, firstout;", "static u32 nn, calls, err, pass, kk, cb, nxt, top, firstout;")
rep("""static u32 mk(u32 op, u32 x, u32 y) {                       /* a new gate of the operands' nodes; returns the positive signal */
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    u32 a = NODE(x), b = NODE(y);
    if (getu(a) == 255 || getu(b) == 255) { err = 6; return 0; }
    setu(a, getu(a) + 1); setu(b, getu(b) + 1);
    return id << 1;
  }
  u32 ra = REG(x), rb = REG(y), d;
  drop(x); drop(y);
""", """static u32 gate(u32 op, const u32 *o, u32 no) {             /* a new gate (op 0 ^, 1 &, 2 |, 3 select) of the operands' nodes; returns the positive signal */
  u32 id = nn++, r[3], d;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    for (u32 i = 0; i < no; i++) if (getu(NODE(o[i])) == 255) { err = 6; return 0; }
    for (u32 i = 0; i < no; i++) setu(NODE(o[i]), getu(NODE(o[i])) + 1);
    return id << 1;
  }
  for (u32 i = 0; i < no; i++) r[i] = REG(o[i]);
  for (u32 i = 0; i < no; i++) drop(o[i]);
""")
rep("""  if (kk >= CODE_BYTES / REC) { err = 5; return 0; }
  u8 *rec = code + (u32)REC * kk++;
  rec[0] = op == 0 ? '^' : op == 1 ? '&' : '|';
  if (d >= 1024 || ra >= 1024 || rb >= 1024) { err = 7; return 0; }
  put32(rec + 1, d | (ra << 10) | (rb << 20));            /* 40-bit record: opcode byte, then three 10-bit register numbers */
  return (id << 1) | (d << 17);
}""", """  u32 rl = no == 3 ? 6 : 5;
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
}""")
rep("""  if (nv == 3) {
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
  }""", """  if (nv == 3) {                                           /* z, x of equal polarity, y the third: sum = (x ^ y) ^ z, carry = (x ^ y) ? z : x */
    u32 zi = 1, xi = 2;
    if ((vs[0] & 1) == (vs[1] & 1)) { zi = 0; xi = 1; } else if ((vs[0] & 1) == (vs[2] & 1)) { zi = 0; xi = 2; }
    u32 z = vs[zi], x = vs[xi], y = vs[3 - zi - xi];
    u32 tt = XOR(x, y);
    if (!NODE(tt)) { err = 9; return; }
    u32 s = XOR(tt, z);
    *sum = s; *carry = SEL(tt, z, x); return;
  }""")
rep("  err = 0; calls = 0; pass = 0; kk = 0; nxt = N; top = N;", "  err = 0; calls = 0; pass = 0; kk = 0; cb = 0; nxt = N; top = N;")
open(P, "w", encoding="utf-8", newline="").write(t)
print("patched gen.c", len(t.encode()))
