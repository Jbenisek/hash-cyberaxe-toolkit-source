# BLAKE3, 3 rounds: bit-sliced 256-lane search with pivot full adders and a mask walk

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), both bit-sliced 256-lane searches with a declared register file that passed the judges, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took two ideas and re-implemented them in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92 and Jbenisek's e479cbbf.
The target is the plain one of 0a9640ed: 64-byte messages 0^32 || x, one block, flags 11. Compared with 0a9640ed, three things change:

1. Pivot full adder (credited to 6ae36351): of three variable inputs two have equal polarity, so the third is the pivot p and u = x ^ p, sum = u ^ y, carry = (u & (y ^ p)) ^ p; the AND always sees equal polarities, so every adder bit is 5 gates and no extra operation is spent on polarities. Our generator folds constants and drops dead gates as before.
2. Mask walk (credited to 6ae36351): the circuit's digest planes are stored as the circuit produces them and fed back as the next input planes, so the chain is g(x) = f(x) XOR q for a fixed 256-bit mask q (weight {qweight}) that the generator derives. No complement operation, no polarity climb and no advice word are needed; g(x) = g(y) if and only if f(x) = f(y). The recovery circuit has 8 more operations (XOR with q), charged.
3. The success argument is restated for the judges' rulings on the earlier entries: the score-critical premise H1 compares the fixed target with a uniformly random function (success of the single attempt on the target is at least success against a random function, over r and F); the approximations used in the random-function computation (independent exponential ages, Poisson cut count, linear cut loss, geometric lengths) are a separate named heuristic H2; experiments are reported as program checks with no inference drawn from counts; every term of the ledger is enforced by a halt and printed by the program.

The step is {PH} operations for 256 trails (19,022 in 0a9640ed, 18,866 in 3356413f); the loop body is {body} operations; the shorter program leaves room for {tmax} table entries (Tp = {Tp}). Registers, memory convention and instruction charge are those of 0a9640ed: 1,024 registers of 256 bits counted as 32,768 bytes of memory, every transfer charged, 36 bytes per instruction (no shorter encoding is used).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | {TL} |
| operations per batch of 256 trails | {body} (step {PH}, stage-1 test {filt}, loop 3) |
| total N | {N} operations = 2^{log2N:.6f} units of 638 |
| memory | {mem} bytes including code ({instr} instructions of 36 bytes), the table ({tmax} entries of 25 bytes), counters and the 1,024-register file; claimed as 2^20 ({spare} bytes to spare) |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds {Pl:.4f} under H1 and H2) |
| preprocessing | none offline; setup and generator 2^{log2setup:.2f} units are in the time bound (claimed 14.2) |
| nonuniform advice | none |

Against 6ae36351 (124.91252) this is {gain:.4f} bit; against 0a9640ed {gain0:.4f}; against 3356413f {gain3:.4f}. The main loop is {pmain:.2f} percent of the total, recovery {prec:.2f} percent.

## Premises, and what was checked

H1 (score-critical, model premise): success of the attempt on the fixed target is at least the success of the same procedure against a uniformly random function. It cannot be tested at width 256 and is declared, not proved; a deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits, and eps up to {eps:.4f} is absorbed by the margin. H2 (supporting): the named approximations of Lemma 2. H3 (score-critical): the 1,024-register machine convention.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): {stats1}; {stats2}.
Outside the shipped experiments, the program was compared with the organizer's reference `blake3(M, 3)`: the scalar digest on 300 messages, the bit-sliced step on 8,192 messages plus 256 messages chained 4 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes.

## Generator peak memory (the ruling on 036e270d asked for it)

The straight line is generated at setup. Model (proof 3.6): {nodes} nodes, peak scratch {scratch} bytes, generator code {gencode} instructions, all held in the region the table and the register file occupy once the search runs (setup phase {ph1} bytes, search phase {mem}). Measured: a freestanding C port of the generator (source embedded in bsrho.py as `GEN_C`, `--gen-c`) compiled to WebAssembly in a sandbox whose guest memory is capped at 1,048,576 bytes emits the identical program (instruction text equal line by line, same q), with static arrays of {cpst} bytes including the final code region and counters and a scratch peak of {cpe} bytes. The Python generator's own resident set (83 MB) is the interpreter's and is not charged.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The 1,024-register file is this entry's declaration; the profile fixes no register count. Smaller files cost {t512:.4f} (512 registers) and {t256:.4f} (256) in time_log2.
- The overlay of the generator's code and scratch on the table region is an assumption of the layout; the C port shows the generator itself fits with room to spare, but the machine of the cost model is not executed by any organizer check.
- The generator's code is charged by Python bytecode count ({gencodeexact} instructions, rounded to {gencode}).
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line. Together they are below 1e-7 of the ledger.
