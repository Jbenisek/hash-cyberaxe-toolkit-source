# Second-class closure: withdrawn UNSATs and the independent-check lesson

Original filename: `FINDINGS_2026-10-23_151.md`.
Original complete-file SHA-256: `385cdb1312abedc5cd6bede8c6bf2d201f352ce3ff033607c44cb6037249437e`.
Reviewed on 2026-10-29: the 19 paragraphs absent from the local 1025 curated snapshot, spanning entries 133 through 150 and the final correction. This is not a claim that the whole 115,910-byte source was newly reviewed. Only scientific content from the new paragraphs is retained here.

## Correction that supersedes the negative result

The final 2026-10-29 correction withdraws the claims in entry 143 item 1 and entry 147 that the second schedule-chain class has no full-state structure at widths 12, 16 and 32 under the stated pins. The zero-time UNSAT results were produced by an encoder conflict: signed differences together with a symmetry breaker excluded the pinned direction of the first required difference. The first digit at the top bit of W8 was `n`, but the symmetry rule chose the opposite orientation. The formula was therefore inconsistent by construction, before testing the intended cryptographic question.

The earlier explanation that the width-8 witness survived because narrow words change carries is also withdrawn. In this instance the width-8 witness happened to use first digit `u`, while the wider witnesses used `n`. The correct final status of that second-class question at widths 12, 16 and 32 is **OPEN**, pending a corrected encoding with the incompatible symmetry constraint removed. A historical closed-cell map must not retain those verdicts as mathematical exclusions.

## Other scientific observations in the missing entries

- A schedule witness for the second class, with W17's top-bit difference pinned, was reported at widths 8, 12, 16 and 32. Schedule satisfiability alone is weaker than final-state closure.
- For one width-8, 27-step instance, a recentered orbit around a previously found partial solution satisfied equality of a, b and e at step 27 in 911 seconds; the other five state words remained free. The next stronger stage was UNKNOWN at its recorded budget. This is a partial equality result, not a collision.
- Finite nearness probes found examples with 16 unequal bits among 64 final-state bits at width 8 and 32 among 96 at width 12. The source conjectured roughly proportional scaling. That extrapolation is not a proved bound for width 32, and solver timeouts do not establish the optimal attainable distance.
- A new encoder-independent Python verifier recomputed compression from decoded initial state and message words, requiring distinct messages and equality of all eight outputs. A schedule-only width-16 model failed this complete check, as expected. A successful schedule decoder is therefore not interchangeable with a collision verifier.
- Four tested rotations of a known signed characteristic were reported UNSAT. These are finite observations, not a general impossibility theorem. A tail relaxation initially removed the final equality rows and returned SAT with unequal outputs; that candidate was discarded, and the generator was corrected to retain the collision boundary.
- The added entries report no newly scorable collision from those runs. Long unresolved solver runs remain UNKNOWN. Historical workload details and control instructions have been omitted.

## Reusable verification rule

Before trusting either a SAT witness or an UNSAT exclusion, bind the encoder to a known positive control in the same target and orientation convention. A symmetry breaker is valid only if it preserves at least one representative of every solution class after all signed pins are applied. Pair swapping changes the orientation of signed differences, so it is not automatically a symmetry of an already oriented instance. A complete collision claim additionally needs the original message schedule, legal domain, correct IV/chaining model and independently recomputed outputs.
