# Characteristic-guided valuation, schedule grounds and corrected negative results

Original filename: `FINDINGS_2026-10-26_ANGLE.md`.
Original SHA-256: `71293662a8b960fc5c411747fa6541b31e273b28c0bed0030b5f666da0d8b755`.
Original length: 78,399 bytes, 367 lines. Read completely on 2026-10-29 in contiguous chunks 1-180, 181-280 and 281-367. This is an independently authored scientific account of the mixed note; operational coordination and runtime-control content are not reproduced. Historical solver and verifier reports were not re-executed during publication review.

## A concrete positive control

The note reports a 39-step, 32-bit SHA-256 semi-free-start pair valued from a known signed characteristic in 44 minutes. Both computations use the same chosen chaining value, not the standard IV. Independent recomputation was reported by two implementations. The pair is a new assignment on a known characteristic, not a new step record or an ordinary standard-IV collision.

Common chaining value, in the source's a-through-h word order:

```text
7c26242b dc3fba8a 203e2a9a 91a5b2e0 dcf7cf9b c78982f9 894e7dcd 8b93290c
```

Message block 1:

```text
a247aef7 d2929cc6 9db25158 79d9fb69 a960f705 30e3f354 5fbf7d7f a6395b0a
72895c61 210771c6 b06bff8b b69f804f a946e11e b05f04ad 43660038 d80d950f
```

Message block 2:

```text
a247aef7 d2929cc6 9db25158 79d9fb69 a960f705 30e3f354 5fbf7d7f a6395b0a
32895c61 298761c6 f06bff8b b09da37b a956f91e b05f04ad 43660038 d80d950f
```

Reported common output:

```text
fb1bb2df 59a68f8f 8d5801be a5351af9 c18fe335 8f475eac ae6b3af9 6169e336
```

The differing input words are 8, 9, 10, 11 and 12. A fully pinned positive control was reported immediately satisfiable. Unguided instances remained unresolved after 26 hours, but that observation is not a controlled universal speed-up benchmark.

Four known characteristic families were reported valued with independently checked pairs: pin39b in 44 minutes, llw39 in 18, zh37 in 48 and mns38 in three. Reference pointers in the original are ePrint 2026/1120, 2023/285, 2026/232, 2021/292 and 2015/350. These papers are references only and were not freshly reviewed in this pass. Claims of a thousand-fold advantage over literature runtimes cannot be inferred from different machines, algorithms and experimental budgets alone.

## Local changes and the seam bridge

Releasing selected conditions while preserving final equality produced independently reported pairs with a three-bit change at E20 and a three-bit change at W24 relative to the reference characteristic. Other single-row releases returned the original pattern. These show local non-rigidity of that characteristic, not a complete catalogue or a new family relative to all literature.

A 38-step bridge used the entry of pin38 through row 16, a free seam on rows 17-22, and pin38b's exit from row 23 onward. Its reported pair passed the independent verifier after 410 minutes. This corrects an earlier broad claim that all cross-tunnel hybrids were UNSAT: that claim concerned more restrictive or seam-free constructions. The later separate seam audit supplies a mapped positive control for this witness.

A reported pin38b witness was withdrawn after a second runner overwrote the model file before decoding. Another early relaxed-tail SAT candidate had unequal outputs because its final equality rows had been freed; it too was discarded. Neither is a counterexample to the target hash. The scientific lesson is to bind a solver verdict, model, decoder and independent check to the same immutable artifact.

## Door words and exact schedule grounds

For the chosen common-CV R-step collision relation, the final state registers correspond to the A/E rows R-4 through R-1. Those state differences must vanish. The message differences at those same rows need not vanish: they can cancel an entering state residual. The initial model mistakenly also forced W36 through W39 equal for 40-step candidates. Its strict-door UNSATs remain statements about that narrower model, not exclusions of all collision-compatible doors.

Allowing a paid W39 produced a real modular-schedule ground with lit expanded rows {16,17,24,26,39}. The source records a 12-bit ground with weights {3,1,2,1,5} on those rows, independently recomputed from its message words. Later in the note it records three distinct cores attaining the same weights. An initial minimum claim used only failed caps 8 and 10 versus a cap-12 witness, which would not alone rule out 11; a later attributed independent check explicitly reports cap 11 UNSAT. These are statements about the constrained schedule shape, not full-state collision probabilities.

The first selected ground did not fit the initially imposed early-clean state tails. A later gate check showed that several such tails were already structurally contradictory for their lit schedule rows, so their UNSATs do not establish a difficult middle-solving obstruction. Ground and state-entry pins must be compatible; mixing a new ground with a different member's fully pinned entry can contradict immediately.

## Linear maps, padding and real modular schedules

The note initially treated the XOR-linear schedule as a necessary relaxation of the modular-difference problem. An independent check withdrew that interpretation: real modular grounds existed with lit patterns assigned zero nullity by the XOR model. Carry behavior can produce modular differences absent from the XOR shadow. Nullity zero excludes that linear model only, unless an explicit sound implication from the real problem has been proved.

The same check found inactive padding rows in 937 of 987 trigger-map entries. Forcing every listed row nonzero then tested a different, often contradictory support. The initial claim that 79 of 88 real-schedule tests showed modular carries killing the families was withdrawn; many formulas forced padding rows that the supposed source kernel never used. Some stored ground files were trivial equal-message assignments: 67 of 102 in that inspection. Filenames and support labels are not evidence of a nontrivial schedule.

A revised full-core map expanded kernel vectors to their actual supports. Its reported distinct XOR-shape counts for R39..47 were 80, 108, 122, 122, 111, 89, 57, 32 and 16. Exact modular-schedule tests on selected shapes returned 81 SAT models from 96 tests, with 15 undecided, and all 81 reported independently verified expansions. These are schedule grounds, not state collisions. No independently verified 40-plus-step collision was reported in the note's final audit.

## Why solver budgets and condition counts are not a cost proof

An early apparently favorable row-26 band consisted of cells that merely survived a five-second timeout. Later exact tests refuted specific candidates. The broader claim that the whole 39-step shape could not reach 40 was withdrawn when a paid-door schedule ground was found. The source also corrected its assertion that every short UNSAT was propagation-only: among 75 with recorded statistics, 62 had zero conflicts and 13 involved search.

Known-satisfiable self-seam controls often remained undecided at 60 seconds. Thus a cell's survival of that budget is not evidence of SAT or proximity to a collision. Solver wall time is sensitive to the exact encoding, sign orientation and fixed conditions, and is not the attack's probability or charged work.

The source built a signed-difference relaxation with modular digit arithmetic and a count C of active state bits and Boolean-input conditions. Exact known-pair validation checked SAT at each pair's own count and UNSAT at one less. However, initial calibration runs omitted the requested K field entirely: the formulas did not contain the advertised bound. Those calibration claims were explicitly withdrawn. Corrected runs proved C > 60 on one calibration window, while C <= 90 remained unresolved at the stated budget.

The final source also withdraws a cost closure based on C > 120..200 for selected dense-core grounds. C is a condition-count objective, not log2 construction work. The same document notes that a practical filed 39-step line had C = 120 in one window and a different work exponent; these are not interchangeable units. The surviving observation is a structural contrast between low late-row C in known pairs and larger C in tested grounds. It does not price a family or close all 40-plus attacks.

A global relaxed model admitted a purported low-C 40-step characteristic that failed exact conformance even when only its late rows were tested. A separate linearized codeword search failed its known-positive calibration. Neither model's attractive candidate nor unfavorable search weights can therefore be published as a real collision or an impossibility bound. A final kick-row correction likewise distinguishes rows allowed to differ from rows forced nonzero; previously excluded lt03 variants remain open under the weaker intended specification.

## External references recorded by the source

- https://eprint.iacr.org/2026/1120
- https://eprint.iacr.org/2023/285
- https://eprint.iacr.org/2026/232
- https://eprint.iacr.org/2021/292
- https://eprint.iacr.org/2015/350

These are bibliographic pointers, not newly verified external claims. No PDF payload or external-paper text is included.
