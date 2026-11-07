s = open('build_all_b4d.py', encoding='utf-8').read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)


rep("of the blake3-r4 entry", "of the blake3-r7 entry")
rep("assert UNIT == 846", "assert UNIT == 1470")
rep("TL1 = 125.35348\n", "TL1 = 125.35348\nTL4 = 125.06000\n")
# scan of table sizes for the proof text
rep("sc = b.gen_scratch()\n", """sc = b.gen_scratch()
_ml = b.MEM_LIMIT
_base = code + b.REGFILE + b.COUNTERS + b.ADVICE
scanrows = []
for _tm in (3000, 6000, 9000, 11500, 14000, 20000):
    b.MEM_LIMIT = _base + b.SPARE + b.ENTRY * _tm
    _p = b.plan(256)
    _lg = b.ledger(_p)
    _m = _base + b.ENTRY * _p["tmax"]
    scanrows.append((_p["tmax"], log2(_lg["total"] / UNIT), log2(_m / 2 ** 20)))
b.MEM_LIMIT = _ml
assert min(scanrows, key=lambda r: r[1] + r[2])[0] == 11500
scan = "; ".join("%d entries: %.5f + %.5f = %.5f" % (r[0], r[1], r[2], r[1] + r[2]) for r in scanrows)
""")
rep("mem = b.ENTRY * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE\n", """mem = b.ENTRY * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE
memlog2 = ceil(log2(mem) * 100000) / 100000
memterm = memlog2 - 20
assert b.MEM_LIMIT >= mem and b.MEM_LIMIT - mem <= 64
""")
rep("capped at 16 pages = 1,048,576 bytes emits", "capped at 29 pages = 1,900,544 bytes (below the claimed memory) emits")
rep("leaves %s bytes of the 1 MiB unused", "leaves %s bytes of the 29 pages unused")
rep("(a 3,229-byte text segment, %s bytes of bss) runs under `prlimit --data=1048576 --stack=65536`", "(a %s-byte text segment, %s bytes of bss) runs under `prlimit --data=%s --stack=65536` (the claimed memory)")
rep("fm(NATIVE[\"bss\"]), fm(NATIVE[\"as_ok\"])", "fm(NATIVE[\"text\"]), fm(NATIVE[\"bss\"]), fm(NATIVE[\"data_cap\"]), fm(NATIVE[\"as_ok\"])")
rep("run within the 1 MiB cap shown", "run within the caps shown")
rep("TL3=TL3, dr3=TL - TL3, TL1=TL1, dr1=TL1 - TL, dTL=TL - 125.02375,", "TL3=TL3, dr3=TL - TL3, TL1=TL1, dr1=TL1 - TL, dTL=TL - 125.02375, TL4=TL4, dr4=TL - TL4, memlog2=memlog2, memterm=memterm, score=TL + memterm, memlimit=fm(b.MEM_LIMIT), scan=scan,")
rep("memspare=b.MEM_LIMIT - ph2", "memspare=fm(b.MEM_LIMIT - ph2)")
# claim and texts
rep('with the walk g(x) = f(x) XOR q (f(x) = the complete 4-round digest', 'with the walk g(x) = f(x) XOR q (f(x) = the complete 7-round digest')
rep("blake3-r4-prefix-v1 restricted to 64-byte", "blake3-r7-prefix-v1 restricted to 64-byte")
rep("Not claimed for other messages, other round counts", "Not claimed for other messages, other round counts")
rep("4 rounds, unkeyed, the complete 256-bit digest (blake3-r4-prefix-v1)", "7 rounds, unkeyed, the complete 256-bit digest (blake3-r7-prefix-v1)")
rep("Plain birthday search; no differential or structural property of the 4 rounds is used.", "Plain birthday search; no differential or structural property of the 7 rounds is used.")
rep("846 operations (C of blake3-r4) to the unit.", "1470 operations (C of blake3-r7) to the unit.")
rep("%d bytes <= 2^20; claimed as 2^20. The circuit generator", "%d bytes = 2^%.5f; claimed as 2^%s (above 2^20, so the scalar policy adds %.5f to time_log2). The circuit generator")
rep("sandbox capped at 1,048,576 bytes of guest memory and as a native binary under prlimit; both emit", "sandbox capped at 1,900,544 bytes of guest memory and as a native binary under prlimit at the claimed memory; both emit")
rep("% (tmax, b.ENTRY * tmax, code, body + b.other_code(st), mem, b.GEN_CODE, genimg, sc[0], ph1, ph2))", "% (tmax, b.ENTRY * tmax, code, body + b.other_code(st), mem, log2(mem), memlog2, memterm, b.GEN_CODE, genimg, sc[0], ph1, ph2))")
rep("Credited derivative: our own 62cfd777 (the same program at 3 rounds), 0a9640ed and 3356413f", "Credited derivative: our own a6ee439c (the same program and proof at 4 rounds), 41b32afc, 75d5e1f9, 62cfd777 (3 rounds), 0a9640ed and 3356413f")
rep("complete 4-round digests agree in the stated low bits", "complete 7-round digests agree in the stated low bits")
rep('"target_profile": "blake3-r4-prefix-v1", "attack_class": "ordinary-collision", "rounds": 4,', '"target_profile": "blake3-r7-prefix-v1", "attack_class": "ordinary-collision", "rounds": 7,')
rep('"memory_log2_bytes": 20,', '"memory_log2_bytes": memlog2,')
rep('"baseline_improved": "blake3-r4-nominal-v2"', '"baseline_improved": "blake3-r7-nominal-v2"')
rep("The blake3-r4-prefix-v1 target with 64-byte messages 0^32 || x (one block, flags 11), collision of the low 18 bits", "The blake3-r7-prefix-v1 target with 64-byte messages 0^32 || x (one block, flags 11), collision of the low 18 bits")
rep("The blake3-r4-prefix-v1 target with 64-byte messages 0^32 || x at full width 256.", "The blake3-r7-prefix-v1 target with 64-byte messages 0^32 || x at full width 256.")
rep("complete 4-round digests agree in the low 18 bits", "complete 7-round digests agree in the low 18 bits")
rep("complete 4-round digests agree in the low 21 bits", "complete 7-round digests agree in the low 21 bits")
# the run of the fixed table: "tmax" now from MEM_LIMIT; text about 3.5 smaller files: same memory budget
rep("is above 2^20 bytes, so no table fits.", "is above the memory budget of the plan, so no table fits.")
open('build_all.py', 'w', encoding='utf-8').write(s)
print('ok')
