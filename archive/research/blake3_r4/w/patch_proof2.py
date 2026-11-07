import sys
p = sys.argv[1]
s = open(p, encoding='utf-8', newline='').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)
rep("table capacity tmax = {tmax} entries of 25 bytes.", "table capacity tmax = {tmax} entries of 26 bytes.")
rep("(F < {Tp} < 2^8 and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 177 differ.", "(F < {Tp} <= 2^{fb} and the key holds its {fb} low bits), so equal keys of two DPs differ only if their bits above {keytop} differ.")
rep("the key space is 2^56 * {Tp} = 2^{log2keys:.2f}", "the key space is 2^{kb} * {Tp} = 2^{log2keys:.2f}")
rep("The checked event is that the complete 3-round digests agree in the low 18 bits and the messages are distinct.", "The checked event is that the complete 4-round digests agree in the low 18 bits and the messages are distinct.")
rep("Table: {tmax} entries * 25 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes);", "Table: {tmax} entries * 26 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (16 bytes; a length is below c + 2^48 < 2^{log2capr1:.1f}), kept in three arrays (keys 4 per word, numbers 16 per word, lengths two per word);")
rep("(loop body {body}, handlers 1,000, recovery 650, setup, cut and slice 160)", "(loop body {body}, handlers 1,000, recovery {recov}, setup, cut and slice 160)")
rep("tmax = floor((2^20 - {codebytes} - 32,768 - 16,384) / 25)", "tmax = floor((2^20 - {codebytes} - 32,768 - 16,384) / 26)")
rep("the program has a longer generator (the pivot rule), both charged.", "the generator is new (Section 3.6), charged.")
rep("Credited to our 0a9640ed, 3356413f and cf8b0e92 and to Jbenisek's e479cbbf: the relation,", "Credited to our 62cfd777, 0a9640ed, 3356413f and cf8b0e92 and to Jbenisek's e479cbbf: the relation,")
i = s.index("### 3.5 Register file and smaller files"); j = s.index("### 3.7 Preprocessing")
new = """### 3.5 Register file and smaller files
Premise H3: the machine has 1,024 registers of 256 bits. The generated line needs {regs} (peak live planes {peak}, no spills: `spill_ops(1024)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{rows35}
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). {note256} The claim assumes R >= {regs}; 1,024 is declared.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry. It is the freestanding C program `GEN_C` embedded in `experiments/bsrho.py` (`python3 bsrho.py --gen-c`, {srcbytes} bytes). It builds the network of Section 3.2 with the pivot adders and allocates the registers in two passes and keeps no node table. Pass 0 builds the network and counts the uses of every node (4 bits per node). Pass 1 builds the same network again; every signal carries its register, an operand whose use count reaches zero frees its register (registers 256 and above; the output planes are pinned, output plane j in register j), the result takes the lowest free register or a new one, and the instruction record is written. This is possible because the network has no shared and no unused gate (Section 3.2), and its output gates are the last 256 gates in order (the generator checks the second, the selftest the first). It emits the same program as the reference generator (`Step`, `allocate`) of the Python program. The code of the generator is charged at its size compiled to WebAssembly by clang -Os: {gencode} instructions (`llvm-objdump -d`, one line per instruction), 36 bytes each = {gencodebytes} bytes. There is no polarity vector to search and nothing to store: q falls out of the generator, and it is written into the recovery circuit as 8 immediates.
Its scratch (the static arrays of the C program, `gen_scratch` of the program): use counts {nodes} nodes x 4 bits = {usesbytes} bytes, signal state 2,400 (the 16 x 32 state words 2,048, two 32-word temporaries 256, the free-register bitmap 96), shadow stack 2,048, result record 68: {scratch} bytes. The generator builds the network twice; its work is charged in the setup row (Section 3.3).
Layout. The setup phase holds the main code (counted at its final size, {codebytes} bytes; it is written as the generator emits it), the counters and plane copy (16,384), the generator's code image ({gencodebytes}) and its scratch ({scratch}): {ph1} bytes. The generator is never called after setup. In the search phase the same region holds the table ({tablebytes} bytes), the register file (32,768) and the counters: main code + counters + register file + table = {mem} bytes. The memory of the entry is the larger of the two, {mem} bytes ({memspare} bytes to spare under 2^20); the region is {region} bytes against {genneed} bytes of generator image and scratch. The table size of Section 7 is the largest that fits with this layout.
Measured peak memory of the generator (not the machine model, which is the byte account above): {measured}
No other run determines a number of the claim: the circuit, its size, its registers, q and the instruction count come from the generator, which was run under the 1 MiB caps above; the plan (Tp, B, c, tmax) is a deterministic computation of `plan(256)` from the stated formulas, and the experiments and checks of Sections 1, 5 and 6 test the program and select nothing.

"""
s = s[:i] + new + s[j:]
open(p, 'w', encoding='utf-8', newline='').write(s)
print("ok")
