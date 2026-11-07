# Fix for 98b1c2c4 (POSGEN rejected at intake) - 10-15

## Root cause (not our messages)
Reason string "Orchard input must be exactly two 32-byte little-endian field encodings" is PoseidonInputError from verifier/poseidon.py digest(): raised for any message that is not exactly 64 bytes.
Organizer's experiments/runner.py `_python_result` line 351 does `sample_digest = digest_fn(b"")` (to size the digest) before checking any trial. For Poseidon this raises, pareto_pipeline.py catches it as VerificationError -> {"valid": false, reason}. So EVERY Poseidon package declaring a python-message-pairs-v1 experiment is rejected before its program runs (blocksek's same rejection fits). Reproduced: digest(b"", 56) raises exactly that error. Our package's intake-report was mechanically_valid; our returned messages were already 64 bytes of two canonical LE encodings (x, 0). POSR4M/POSR5M passed because they declare no experiments.
No fix on our side other than not declaring a python experiment. (Organizer bug; worth one line in the organizer notes batch: digest_fn(b"") for Poseidon.)

## Change
pkg2 (pkg left untouched): claim.json without experiment_manifest and without experiment: evidence ids; no experiments/ dir; proof.md keeps lines 1-51 numbering (evidence line ranges unchanged), Section 8 says none declared and why, rho.py printed verbatim as Appendix B (no-arg run prints plan). note.md: Files section rewritten, "Response to 98b1c2c4" and own-checks sections (8.5 KB). Old note: note_v1.md.
Checks: chk_exp (rho digest == organizer digest r=56; pairs 232/256 and 222/256 all verified, 64-byte canonical); slot pos_posgen2 (base pos_posr5m), pareto_candidate state ready; `pareto_pipeline.py --family poseidon intake` -> {"intake":"passed"} (no experiments, so no Docker needed; the Docker sandbox was not run since nothing is declared); rulecheck memgate PASS, 2 EXPOSED wording hits (R05/R13 on my Section 8 sentence, an old docstring, H1 "cannot be observed"), read by hand; prefile_check: all PASS except "ledger program printed N" (its N/C ledger form does not fit the T-units ledger; not applicable).
Submit script (NOT run): research/launch/submit_pareto_posgen2.sh (staged-files guard, no deps, appends one FILINGS.md line).

## Lemma constructs (for Lemma v2 agent)
Proof Section 4 uses: exact lazy-sampling product prod(1-(i+1)/N) <= exp(-n(n+1)/2N); hypergeometric/union bounds for detection and gaps; table overflow by a Chernoff upper tail on Binomial(S,theta), ln P = -241.08 (analytic, `plan`; this is the MGF-type bound but a closed form, no "midpoint" numeric bound), then loosely replaced by exp(-100). It does NOT use an exact Poisson cut law. Lemma not changed.
