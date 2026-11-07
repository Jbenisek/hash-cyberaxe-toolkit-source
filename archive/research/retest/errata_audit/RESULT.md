# Erratum audit of ePrint 2026/1120 and who copied it (2026-10-12)

Method (COMPUTED): conditions, characteristic rows and message pairs were transcribed straight from the PDF
(`pdftotext -layout -enc UTF-8`, kept in `paper_layout_utf8.txt`; script `audit.py`, raw log `run.log`, machine list
`bad.json`). Reduced-step SHA-256/512 is recomputed for each printed pair (every printed hash reproduced), then each
printed cell (`= 0 1 n u +`) and each printed two-bit condition is checked on both messages. Our chi files were NOT used
for the audit; they were compared afterwards (`chicmp.py`).

## 0. Two extraction hazards that make "copying" easy (COMPUTED)

1. **The not-equal sign is a combining slash (U+0338) and default pdftotext drops it.** 168 printed conditions are `!=`;
   `pdftotext -layout` (Latin-1 default) prints them all as `=`. A transcriber using the default tool gets 15 wrong-sign
   conditions in Table 16 (37-step) and 15 in Table 4 (38-step), and sees the published pair "violate" 16 and 16
   conditions. Use `-enc UTF-8` and treat `U+0338` before or after `=` as `!=`.
2. **Orientation:** `n = (x,x') = (0,1)`, `u = (1,0)` with x = the message printed SECOND (M'), x' = M. With this reading
   every cell of Tables 3,6,9 (Table 2 pair),12,15,18 holds on the published pair (0 violations; Table 21 has the 2 W16 violations of section 1; the opposite
   reading gives 110-230). `+` = equal to the same bit of the vertically adjacent `+` (all 138 `+` cells hold).

## 1. Erratum table (published pair vs printed conditions)

SHA-256 (the contest tracks) first.

| Table / step | Printed | Pair says | Corrected reading (nearest that the pair satisfies) | Our chi file |
|---|---|---|---|---|
| 16 / 37-step | `A16[29] = A17[29]` | holds on M only, fails on M' (A16[29] is a `u` cell; A17 `=`) | `A15[29] = A17[29]` (also holds on both) | chi37.txt:3,37 correct |
| 4 / 38-step | `W25[4] = W25[9]` | fails on both messages | `W25[4] = W25[6]` (bit 19 of s1(W25) = W25[4]^W25[6]^W25[29]); other 1-edit candidates satisfied by chance: `W25[3]=W25[9]`, `W25[4]=W25[10]` | chi38.txt:3,74 correct |
| 3,15 | every other cell of rows -4..37 | all hold | none | rows identical to the PDF text (COMPUTED) |
| 4,16 | every other condition (46 of 47; 30 of 31) | all hold, `!=` included | none | sets identical except the two lines above |
| 9-11 / 36-step | Table 9/10 vs Table 11 SFS pair | Table 11 pair does NOT satisfy Table 9 (231 cell violations, E column matches nothing at any row shift) | Table 9/10 are satisfied by the **Table 2** collision pair (M1,M1', 0 violations, 30/30 conditions) | not held |
| 21-23 / 39-step | `W16[4]`,`W16[2]` fixed `1` in Table 21 row 16 | pair has 0 at both | reading `0` (no neighbour fits better) | not held |
| 22 / 39-step | `A17[30]=A18[30]` (A18[30] is `u`); `E17[5]!=E18[5]`; `E20[3]=E21[20]`; `E21[3]!=E21[17]`; `W23[2]!=W23[0]`; `W25[21]!=W25[28]`; `W25[0]=W25[23]` | all fail | `E20[3]=E20[20]` does not fit; op flip or 1-bit shift fits each, no unique reading (`bad.json`) | not held |

SHA-512 (same defect classes, not contest tracks): 37-step `A16[61]=A17[61]` (same erratum as 256-37, fits `A15[61]=A17[61]`),
`E20[18]=E20[55]`, `E20[32]!=E20[36]`, `W8[54]!=W8[60]`; 38-step `A15[63]!=A16[63]`, `A16[47]!=A17[47]`,
`A16[55]!=A17[55]`, `A16[61]!=A17[61]` (pair has equal; op flip fits), `E16[14]=E16[51]` (u cell; fits `E16[13]=E16[51]`);
36-step `A15[59]=A16[59]` (n cell; fits `A14[59]=A16[59]`), `E19[32]=E19[36]`. 39-step SHA-512: **the printed Table 26 pair
does not verify** (word 11 of M printed with 15 hex digits `3201f73c35ebd0e`; padding it does not restore a collision;
a single-digit search over M' and CV finds nothing) so Tables 24/25 could not be checked (COMPUTED, unresolved).

### Printed cells with ambiguous sign convention or row label (DERIVED from the extraction)

- `!=` glyph (see section 0.1). `M`/`M'` labels sit in the second of four text lines in the layout dump; orientation
  is decided only by testing (section 0.2).
- Tables 4/10/16/22: the left label (A16, A17, E16...) is the row at which a group is checked, not the row of the
  indices inside (group `A16` contains `A14[..]` and `A15[..]`); the `Pro.` column floats between wrapped lines (Table 22 is the worst).
- Index order inside a pair is not sorted (`A16[18] != A16[6]`, `W8[30] != W8[9]`); harmless.
- Table 9 W row and Table 11 pair use word-5/6/7 differences while Table 15 starts at W6: do not mix the 36-step table and its SFS pair.

## 2. Who copied them (rival r37/r38 packages held; read as data only)

| Package (track, author) | Condition list / checker reading | Where |
|---|---|---|
| 6c77089c r37 winglock (first to correct) | corrected `A15[29]=A17[29]`; board note: "Table 16 prints A16[29]=A17[29], involves a difference bit and holds on one member only" | `research/rivals/boards_sha256-r37-exploratory.json` (note of 6c77089c) |
| 0db0eeb6 r37 (leader, companygardener lineage) | corrected | `rivals/pkgs_1011/sha256-r37_0db0eeb6/sha256-r37/proof.md:112` ("printed: A16[29] = A17[29]"), `experiments/xtab.py:66-67` |
| 7319bba9 r37 winglock | corrected | `grok/in/job98_shaves/7319bba9/*proof.md:139`, `*spec6core.py:59-60` |
| 7c46d8cb Th0rgal, c3041753, fb039a6e 0xshikhar, fe65a7cb, ffbe30bb Jbenisek (r37) | corrected | each `*_proof.md` (lines 113-114, 113, 114, 132, 132) and `*xtab.py` X2 block (L66, L66, L66, L62, L62) in `grok/in/job98_shaves/<id>/` |
| 81 Th0rgal, 86 r37c_fix, 91 leader (r37 copies of the above) | corrected | `grok/in/job81_r37_th0rgal/proof.md:116`, `job86_r37c_fix/proof.md:116`, `job91_r37/leader_proof.md:112` |
| 29be77ba, 84f1f00b jungjipdo (r37, failed) | **own reading**: "on the unprimed message it reads A16[29] != A17[29], the same condition A17[29] = 0" (equals `A15[29]=A17[29]` on the published pair, where A15[29]=A17[29]=0; equal in general only if A15[29]=0 on every Step-1 solution used) | note in `boards_sha256-r37-exploratory.json` (not held as package) |
| r38 20a43626/3d819a4b winglock, then b99301f4 leech1996, 20dbd783, 012400ff, 37742a53, 44cb527b, aa0496d3, fdef4bab, 19c9e7e7, 8f02e559, f8e24d8d, 0bf9d76b | corrected `W25[4]=W25[6]` | proofs `...proof.md:106-122` (e.g. `rivals/pkgs_1011/sha256-r38_44cb527b/sha256-r38/proof.md:106`), code `vt38.py:56` X2 tuple `(2,25,4,1,2,25,6,25)`; all 9 `vt38.py` files and all 8 `xtab/spec6core.py` files hold a condition set EXACTLY equal to printed-with-the-two-fixes (47 and 31 conditions, `!=` correct) (COMPUTED by `who.py`) |
| aedef47e r38 (board note) | reads `W25[4]=W25[6]`, justification via s1 bit 19 and the printed `W16[4] != W16[6]` | `boards_sha256-r38-exploratory.json` |
| Other r37/r38 filers (~40 ids: 8de337d5, d3ec5c41, 44921815, generic birthday searches ...) | not decidable: only a note head is held, no package | `BOARDS_TABLE.tsv` |

Result: **none of the held packages uses a printed (wrong) reading.** The misprints were found by winglock (r37 first,
r38 first) and propagated as corrections with credit; nobody held copied them. The copy risk is the extraction hazard
(0.1), not the two readings.

## 3. Consequences if the printed reading were used (DERIVED)

- r37 `A16[29]=A17[29]`: A16[29] differs between members and A17[29] does not, so the condition cannot hold on both;
  a checker that tests member x (second printed) rejects the published pair (A16[29]=1, A17[29]=0 there) and an
  exact-event q3 would be measured on the complementary value of A17[29] (still a 1-bit factor 2^-1, but the later
  chain `A17[29]=A18[29]` then sees the other branch) or be 0 if checked on both members.
- r38 `W25[4]=W25[9]`: the published pair fails it, so a pair-based self-test rejects its own reference; the intended
  event (s1 bit 19 cancellation feeding W27) is replaced by an unrelated 1-bit event, so q3 would be measured on the
  wrong event (factor 2^-1 both ways, different downstream behaviour). Output validity is unaffected because outputs are
  verified by the compression, as the rival proofs state (`44cb527b proof.md:462`).
- Not computed: the numerical size of the q3 change for either wrong reading (no run made).
