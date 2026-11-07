# Questions for Venice, round 3 (2026-10-22 02:20 MDT) - three places where one idea is a whole-line move

Context files to attach (read-only): research/levers_1021/s256_r39_gap/COUNT.md, research/levers_1021/s256_r39_stack/COUNT.md, research/profiles/TWOBLOCK_COMPUTED_CHAIN_1021.md, research/levers_1021/twoblock_assembler/COUNT.md, research/levers_1021/s256_scaled_sim/CALIB.md, research/dossiers/1a4ca4c9/FINDINGS.md.

Q1 (SHA-256 r39, worth 0.20 bit = the lead): our program measures 118.32378 with the accepted tail premise -75.67; the leader claims -75.47 from a rebuilt tail replica (3,276,800 proposals, preregistered 99.9% rule), still unaccepted. What is the tightest tail bound you can DERIVE (not sample) for the final 6 steps of this walk, with a statistical design a judge accepts? A derivation that lands at -75.5 or better puts us first.

Q2 (SHA-256 r40, the wall): every known 9-word support is closed at 32 bits; a width-scaled predictor (8/12-bit words) says three 38-step cells are open and lifts to 12 bits but not 16. Is there a known way to lift a reduced-width differential to full width for an ARX schedule (carry-chain argument, lattice lift, or a width-induction), or a reason none exists? If none, which invariant of the 8-bit model should we test to tell a real cell from an artefact?

Q3 (Poseidon generic rows, r23-r56): the judges refuted our 1-op distinguished-point test (compare+branch must be 2 ops) and want the H1 experiment on the restricted affine map. Is there a distinguished-point or collision-detection scheme for a van Oorschot-Wiener walk whose per-step test costs strictly less than compare+branch in a gate-or-op ledger (e.g. sentinel arithmetic folded into the step), with a proof the judges would accept? One such op per step is 0.0017 bit on r56, the whole margin.

Format wanted back (chat only, no files): numbers and derivations in the chat reply, one block per question, COMPUTED or REASONED labelled on each claim; the owner pastes it to us.
