# blake3-r1-exploratory: a two-word complement-fold collision, two 64-byte messages, time_log2 = 2.5477

## Credit first

Nobody named here has reviewed this package, and a credit is not an endorsement. proof.md Section 9 credits
every contributor in one line.

- **rickmanelius** (`7e29738c`), **Subflatus3** (`75a58077`, `d959036c`, `ae5c11f3`, `3a9b4c9d`) and
  **pratikgx** (`cbd3581a`): complement collisions on this track. The mechanism is common here; this entry
  is not a new mechanism for the track.
- **Claude (Anthropic) agents** that I run: the c1 = 0 choice of m8 and m12 and the pair.
- **Jbenisek** (me): the counting and the package.

## The claim

A deterministic algorithm outputs two distinct 64-byte messages A and B with the same complete 1-round
BLAKE3-256 digest, `a60b648064d9445baa8f41405ca2283f497c0ecbe4ab151c020d61c692d60301`. Unkeyed, standard IV,
flags 11, counter 0, block length 64, feed-forward, full 256-bit digest: an ordinary collision of two
distinct complete messages. They differ only in m9 and m13.

- **Lemma 1 (proof.md Section 2).** In a G call with c1 = 0, changing y to y - 2*a2 - 1 turns a2 into NOT a2
  and complements all four outputs.
- **Choosing x.** c1 = 0 exactly when x = (d0 XOR ROR(0 - c0, 16)) - a0 - b0; m8 does this in D0, m12 in D2.
- **Lemma 2 (fold).** D0 leaves words 0, 5, 10, 15 and D2 leaves 2, 7, 8, 13; the fold o[i] = s[i] XOR s[i+8]
  pairs them, so the complements cancel in o[0..7].
- **Against my earlier r1 entries.** Those cancel a difference in the length, flags, counter or chaining
  value. Here all four agree; the difference is in two message words and cancels in the output fold.

## The ledger (proof.md Section 6)

C = 222; conventions as in `f0dab7bd`, `31acfdbb`, `c8160a0a`, `6b039da2`.

| Step | Work | Units | Primitive operations |
| --- | --- | ---: | ---: |
| 1 | column step with m0..m7 = 0, 110 data operations | | 440 |
| 2 | D0 and D2 solves, 19 data operations each | | 152 |
| 3 | RAM words of A and B: 6 data operations, 2 constant stores | | 26 |
| 4 | H(A) and H(B), handling 2 * 80 | 2 | 160 |
| 4 | digest test, 17 data operations; output and halt 8 | | 76 |
| | total | 2 | 854 |

T = 2 + 854/222 = 1,298/222 = 5.8468 units; log2 T = 2.54766..., rounded up: 2.5477. My counting script,
on the program that produced the certificate, finds the 154 data operations of steps 1 to 3.

## Success, memory and advice

Deterministic, success probability 1. Memory below 2^18 bytes. No preprocessing, table, stored collision or
nonuniform advice; no heuristic.

## Evidence

- **Certificate `compl-pair`**: `certificates/compl-pair-a.bin` and `certificates/compl-pair-b.bin`.
- **No experiment is declared**: the output is one fixed pair, which the certificate covers.

## Limits

- One round only; the pair's 2-round digests differ.
- Root output words 8, 10, 13, 15 differ (outside the 256-bit digest).
- No literature survey; no priority or novelty claim.

## Earlier entries on this track, one line each

- `beea45d4`, 0, cancelled. `f0dab7bd`, 2, accepted (length). `31acfdbb`, 4.7545 (flags).
  `c8160a0a`, 6.2351 (counter). `6b039da2`, 3.1334 (chaining value).
