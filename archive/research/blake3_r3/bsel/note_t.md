# BLAKE3, 3 rounds: bit-sliced 256-lane search, straight-line step with select-gate full adders (B3R3sel)

Credit: Claude Opus 5.5 (Claude Code) built this entry's program change, proof and ledger.

## What this entry is

Our entry for BLAKE3 reduced to 3 rounds (blake3-r3-prefix-v1), a plain birthday collision search on the complete 256-bit digest; it uses no differential and no structure of the rounds. It is our own B3R3u5b, 3c2d1220-540f-480a-81ca-b26e5ae2173a (time_log2 124.76596), with one change to the generated step: the full adder of three variable planes is 2 XOR and 1 select instead of the 5-gate pivot adder. The same change at 4 rounds is our 2cf0d4a5-fa44-498e-bff8-b152c681ef12 (B3R4sel, 124.29795).
The lineage of 3c2d1220 is unchanged: our 62cfd777-5613-463f-b561-e2340e00e528, eaef120f-c690-4978-a31e-a3cde49fd669, 0ecdfe35-ba7a-4f74-8ba9-779d417974a2, a6ee439c-5b82-41f2-8acb-9917c8c70756, 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c, 41b32afc-ed4c-4ef1-b9f2-8c72ab163582, 75d5e1f9-8948-4f49-b7a6-5e9475495a7a, 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c and 3356413f-cd60-410c-8847-2266d6444ac5; jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 for the mask walk g = f XOR q (re-implemented from its proof text; no file of it used or run); 616120b2-f777-44a8-bbd2-44f20c56224a for the 5-byte gate encoding (re-implemented from its text).
mitchuski's 10ce9f59-80a1-4304-92cc-ca4dede3bbcc (124.70692) adds each all-variable a + b + m as one three-addend sum with the 9-gate MDFA column. We compared that column with this step: with the select gate two ripples of 3-gate full adders cost 6 gates per bit position, so the column is not used.

## The change: one select operation

The machine declares one bitwise word operation besides AND, OR, XOR and NOT: select(s, a, b) = (s AND a) OR ((NOT s) AND b), bit by bit on 256-bit words, charged 1 operation. It is one instruction on real machines: WebAssembly v128.bitselect (three operands, one result, the form used here), Arm NEON BSL, x86 AVX-512 VPTERNLOG with immediate 0xCA. It is part of the declared machine convention H3 (proof 3.1).
Full adder of x, y, z with z and x of the same polarity (two of three always are): t = x XOR y, sum = t XOR z, carry = t ? z : x, since maj(x, y, z) = z when x != y and x when x = y. 3 gates instead of 5.
The step is {PH} gates for 256 trails ({xor} XOR, {and_} AND, {or_} OR, {sel} select; it was 17,238), {regs} registers as before, no load, store or move. A select record is 6 bytes (8-bit opcode, four 10-bit registers); the code is {codebytes} bytes (it was 132,935), so the table holds {tmax} entries (it was 87,359) and Tp ({Tp}), B and c are re-planned by the same plan. The C generator writes the 5-byte and 6-byte records; its program is byte-identical to the Python reference (sha256 equal).
Without the select operation the program is 3c2d1220 (124.76596).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | {TL} ({dTL0:+.5f} against 3c2d1220) |
| memory_log2_bytes | 20 ({mem} bytes = 2^{memlog2b:.5f}); memory term 0; scalar score {score:.5f} |
| operations per batch of 256 trails | {body} (step {PH}, stage-1 test {filt}, loop 3) |
| total N | {N} operations = 2^{log2N:.6f} units of 638 |
| table | {tmax} entries of 10 bytes; setup phase {ph1} bytes |
| success probability | at least 0.39, single attempt, no amplification (Lemma 2 bound {Pl:.5f}, exact certificate {Pcert}) |
| preprocessing | none offline; setup and generator 2^{log2setup:.2f} units are in the time bound (claimed {preclaim}) |
| nonuniform advice | none |

## Premises, and what was checked

H1 (score-critical, model premise, four clauses), as in 3c2d1220: success of the attempt on the fixed target is at least the success P_F of the same procedure against a uniformly random function; Lemma 2 proves P_F >= {Pcert} (exact certificate, Appendix A). A hazard deficit eps is repaired by extra time: {sens_short}. H3 (supporting, a declared machine convention): 800 registers, the select operation, and the code charges (5 bytes per two-operand gate, 6 per select, 36 per other instruction, 36 per compiled generator instruction). Nothing else in the success bound is heuristic.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts.
Outside the shipped experiments, the bit-sliced step was compared with the organizer's `blake3(M, 3)` on 8,192 messages and on 4,096 lanes chained for 3 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes, runs the register-allocated code on a register file, and prints 0 shared and 0 unused gates.
The C generator ({gencode} compiled WebAssembly instructions, {scratch} bytes of scratch) emits the identical program in a sandbox capped at 16 pages (1,048,576 bytes) of guest memory and as a static x86-64 binary under `prlimit --data` at 2^20 bytes.

## Limits

- H1 is not proved; the full 256-bit functional graph and 2^128 evaluations cannot be tested.
- The select operation, the 800-register file and the code charges are this entry's declarations; the cost model fixes no instruction set or register count. Without the select the program is 3c2d1220.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 250 operations per primitive call and per emitted line ({genfuel} wasm operations measured against {genops} charged).
