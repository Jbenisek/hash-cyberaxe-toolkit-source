# traillab: testing levers on the 37- and 38-step characteristics

traillab is one C library and one CLI. All of the code is ours. It replaces our one-off programs: `pre_sha256_1/smc_exact.c`, `rows22_24/automaton/r2224.c`, `montecarlo/mc.c`, `job104 measure.c` and the four-pattern `q3smc.c`.

## How a lever is tested

You already know what a working lever must produce: a pair whose output difference is zero after the last step. traillab therefore tests a lever like this:

1. It produces real pairs from the attack's free variables.
2. It counts how often the **exact event** happens on the same samples as the printed cells and any relaxation you name.
3. The lever's gain is the ratio between those counts, with an error bar.

A ratio taken from a single row is not a gain. Only a ratio measured up to the exact event counts.

The tool never holds an expanded word W16 or later fixed while it changes earlier words. Each sample is defined by the 16 message words of both members plus one chaining value. Every later word comes from the real message expansion, and every state row comes from the real step function.

## Build and test (inside WSL)

```
cd ./research/tools/traillab
make            # gcc -O3 -march=native -pthread -> ./traillab
make quicktest  # skips the 2^32 enumerations, smaller Monte-Carlo runs: 48 of 48, 49 s (2026-10-12)
make test       # all 53 known answers including the 2^32 enumerations: 317 s (5 min 17 s) at 6 threads (2026-10-12)
```

Add `--threads N` to any command. The default is 6.

## Characteristic files (`chi/chi37.txt`, `chi/chi38.txt`)

Both files are plain text, one directive per line, and `#` starts a comment.

| line | meaning |
|---|---|
| `name`, `steps` | label and number of steps |
| `cv`, `mx`, `my`, `digest` | the published pair. x = the message printed second (M'), y = M. `digest` is checked |
| `row R <A> <E> <W>` | 32 symbols per word, MSB first. Rows that are not listed are all `=` |
| `x2 A15[29] = A17[29]` / `!=` | two-bit condition. chi37 carries the corrected reading A15[29]=A17[29]; chi38 carries W25[4]=W25[6] |
| `lin E18[1]^E18[11]=0` | a general XOR condition on member x, up to 6 terms |
| `anchor K` | the dense part: rows K-3..K of both members are held. A word W_i with i <= K moves only rows below i-3 and the CV (step inversion); a word with i > K moves rows forward |
| `edrive 16 21` | rows 16..21 are driven by E: E_t^x is chosen, W_t comes from it, and W0..W5 are solved through the inverse expansion. All six are free coordinates of the attack |
| `elist 16 v1 v2 ...` | optional list of E-values to propose for an E-driven row (chi38's 32-word row-16 set) |
| `var W7 fset s0 017f8000 late` | a free word. Kinds: `rand`, `fset F T` ({w : F(w+d)-F(w)=T}, where d = the published y-x), `cell` (the word's printed cell and two-bit conditions), `cell+fset`, `list v...`, `list @file`, `a0list @file` (A0-variants mapped to W8). Suffix `back`: the moved row E_{i-4} must keep its cell. Suffix `late`: the word is drawn again for every window proposal |
| `except W6 W7` | the attack replaces these words' cells with their F-sets, so their cells are left out of the model's conditions. `check` still tests them on the published pair |
| `relax NAME op ; op ...` | a named relaxation (ops listed below) |

Symbols: `n` = (x,y) = (0,1) and adds +2^b; `u` = (1,0); `0`/`1` = fixed and equal; `=` = equal; `+` = equal to the same bit of the `+` directly above or below; `x` = differs, sign free; `?` = no condition.

Relaxation ops (separated by `;`):

| op | effect |
|---|---|
| `dropv K<r> MASK` | drop value-only conditions |
| `dropsign K<r> MASK` | drop the sign but keep the XOR |
| `dropx K<r> MASK` | drop all conditions on these bits |
| `droprow K<r>` | drop the whole row and its two-bit conditions |
| `dropx2 K<r>` | drop only the row's two-bit conditions |
| `dropq E<r> MASK` | drop `+` relations |
| `lin <expr>=c` | add an XOR condition |
| `parity K<r>[b],K<r>[b],...` | replace those value conditions by their parity group, i.e. pairwise parities, so the whole group may be complemented |
| `sym K<r> <32 symbols>` | replace the cell, e.g. to test another signing |
| `setv K<r> MASK VALUE` | add value conditions |

On the command line, `--relax NAME` uses a relaxation from the file. `--relax 'name=op ; op'` defines one inline.

Model notes:

- **chi37** (r37 second block): anchor 14; W15 is one of the 32 l; W6 is in F6; W7 is in F7; W8 is in the A0-variant set, which `exact` counts as exactly the 12,103,680 entries of `allg_classes`; E16..E21 are driven by E.
- **chi38** (R38M proof): anchor 13 (A0..A13); W6 is random; W7 is in F7; W8 is in G (2^26); E16 is in the 32-word set; E17..E21 are driven by E.

## Commands

### `check --chi F [--n N]`

Runs these checks:

- the SHA-256 reference (the "abc" test vector);
- the A/E trace against textbook registers;
- step inversion;
- the published pair's outputs and digest;
- every printed condition on the published pair, row by row, with the reason for any failure;
- each relaxation on the published pair;
- an exact rebuild of the published coordinates.

It then makes N random draws of every free coordinate and checks four things: that the forward replay of the x member from its own CV matches, that the y member's words equal the real expansion, that the incremental rebuild equals the full rebuild, and that the y member stays on its dense rows. It finishes with the density of each variable set.

### `window --chi F --rows A B [--event out|state] [--relax R]... [--seeds 1,2,3]`

Mode (c): the comparison on the same samples.

**How the samples are drawn.** A sequential Monte Carlo produces samples conditioned on rows lorow..A-1. It runs in four stages:

1. **Initial draw.** Early and late words are drawn once, and rows anchor+1..15 are checked.
2. **E-driven stages, one per row up to A-1.** Each stage proposes `--m` values per particle and forces the cell's value bits, each forced bit carrying weight 2^-1. It then resamples.
3. **Late stage (only if A-1 > e1).** The late words are drawn again (`--mt2` per particle), the pair is rebuilt in full, and every prefix row is checked.
4. **Window stages (only if the window starts inside the E-driven rows).** These rows are filtered by the union of the cell events (`--carrier union`, the default). The exact event is then counted together with that carrier. `--carrier none` removes the filter, so the exact event is unrestricted, but the run is slower.

**What is counted.** Each particle draws `--mt` final proposals, with the late words drawn again and a full rebuild each time. Every proposal is evaluated on:

- **(i)** `cells`: every model condition of rows A..B;
- **(ii)** `EXACT`: zero output difference after the last step (`out`), or zero state difference after row B (`state`);
- **(iii)** every relaxation.

**Output.**

- counts, rates and Wilson 95% intervals;
- the ratios EXACT/cells and relaxation/cells, with a 95% interval that is cluster-robust over particles;
- the same ratios for two halves of the particles;
- a pooled result and the seed-to-seed spread over fresh `--seeds`;
- log2 P(prefix) from the SMC;
- diagnostics that must be 0: prefix broken by the redraw, y-anchor inconsistent, replay mismatches.

**Main options.**

| option | default | meaning |
|---|---|---|
| `--np` | 2048 | particles |
| `--m` | 256 | proposals per particle per E stage |
| `--mt2` | 1024 | late-stage proposals |
| `--mw` | 256 | window-stage proposals |
| `--mt` | 4096 | final proposals per particle |
| `--prefix-relax R` | | run the prefix under a relaxation |
| `--var 'W8 rand late'` | | override a free word |

### `exact --chi F --rows A B --enum SPEC [--enum SPEC2] [--relax R]... [--base pub|smc]`

Mode (d): exhaustive counting with integer results.

SPEC is one of:

- `E<t>:all|cell|mask:HEX` for an E-driven row. This is an incremental rebuild that starts at row t.
- `W<i>:all|set|cell|mask:HEX` for a base word, i < 16. This rebuilds in full: backward from the anchor, then E-driven rows, then the inverse expansion, then forward.

`set` is the model's set for that word. With two SPECs the tool enumerates their product.

It counts, exactly:

- members of the set;
- rows < A that hold (the prefix);
- the cells of rows A..B;
- the exact event;
- each relaxation;
- the joint counts with the prefix and with the exact event.

`--base pub` uses the published coordinates. `--base smc --np N --pick K --seed S` uses K particles from an SMC prefix and also prints their sum.

### `sdiff --delta D [--func id|s0|s1|S0|S1 --out T] [--xor X] [--chi F --cell W22] [--maxhw H]`

Mode (e), at the level of one word.

- With no `--func`, it lists every signed-digit pattern of the modular difference D, up to weight H. Each pattern has Pr = 2^-weight over uniform x, which is PROVED, and the tool reports the probability mass the list covers.
- With `--func`, it counts exactly, over all 2^32 values, the x with F(x+D)-F(x)=T. It gives a histogram by XOR pattern and by signed pattern. Optionally it adds the count inside a printed cell, the cell's value and two-bit conditions included.

### `backward --chi F --rows B0 B1 [--maxhw H] [--noenum]`

Mode (e), at the level of rows. It runs in two parts.

**For each row t in B0..B1:**

- It takes the step equations: dE_t = dA_{t-4} + dE_{t-4} + X_E + dW_t, and dA_t = dE_t - dA_{t-4} + X_A.
- It computes the exact distribution of X_E = dS1(E_{t-1}) + dCH(E_{t-1}, E_{t-2}, E_{t-3}) and of X_A, by enumerating every free bit that matters. The cells fix the remaining bits. Two-bit and `+` conditions are not applied, and the output says so.
- It gives the probability that the characteristic's own differences close the row.
- For the most likely values of X, it lists every signed pattern of W_t and of E_{t-4} that produces the required modular difference.
- It lists every alternative signing of the characteristic's XOR patterns of W_t and E_{t-4}, with Pr[row holds].

**Message schedule, for every t >= 16:**

- It splits dW_t into its four terms. A term counts as constant when its word is fixed, when the word is in an F-set of that sigma, or when the word's list is constant. A dW_t made only of constant terms is printed as PROVED.
- When exactly one sigma term depends on the values, it prints the requirement sigma(W_j + d_j) - sigma(W_j) = T. It then counts that requirement exactly over 2^32, both alone and inside W_j's printed cell, and gives the ratio exact/cell.

This is the rows 22-24 analysis of `r2224.c`, done for any row and either characteristic.

### `varcount --chi F --word W7`

Gives the exact size of a variable set over 2^32.

### `flip --chi F --word W<t> --mask HEX` (added 2026-10-12)

Word-level test of "free" value bits of an expanded word. Every pattern of the mask bits is written into W_t of BOTH members of the published pair (the bits must carry no difference), W_{t+1}.. are re-expanded from it, and the tool prints ds1(W_t), dW_{t+2} (modular and XOR) and the first later word whose modular difference differs from the published one. A bit set is free only if more than one pattern keeps every later modular difference. Example: chi37 W22 bits 13,17,26 and chi38 W23 bits 13,17,26 each keep only the printed pattern (1 of 8).

### `rowtable --chi F --row T --over W<i>` (added 2026-10-12)

Exact row table: for every value of the listed word W_i (e.g. the 32 l of W15), every E_T with the row's fixed x-bits imposed is tried (T = the first E-driven row) and row T is checked with every model condition. It reports the pairs (u, value), the distinct u = W_T - s1(W_{T-2}) - W_{T-7} (for T = 16: u = W0 + s0(W1)) and the nonempty values.

### Diagnostics added to `window` and `exact` (2026-10-12)

- `window --equiv R,j1,j2,...`: counts, on every sample, the predicate "zero state difference after row R and dW_j = 0 for every listed j" against EXACT: predicate and EXACT, predicate without EXACT, EXACT without predicate. For chi37 `--equiv 24,26` tests eq36 <=> eq24 and dW26 = 0.
- `window` prints `log2 P(rows lorow..b, model cells) = prefix + log2 rate(cells)` per seed (for chi37 rows 22..36 this is q3) and a summary over the seeds: pooled ratios with a 95% half-width, q3 mean and seed sd.
- `exact --hist NAME`: lists every enumerated value (pattern of the mask bits) that passes the prefix and the named condition set, with counts; summed over SMC bases with `--base smc`.
- `--hold-from T` (any command): ARTIFACT MODE. W_T.. of each member are held at the published values instead of the message expansion. The messages are not real; the mode exists only so the tool can reproduce, and therefore detect, the held-fixed artifact. It prints a warning line. No reading in this mode is a gain.

## Known answers (`make test`)

Worked backwards: every number below comes from an earlier, independent program or proof of ours, and traillab must reproduce it. A failing test is fixed in the tool, not in the expected value. `make test` on 2026-10-12: **53 of 53 pass, 317 s at 6 threads.** The groups K1..K7 are the seven known answers of the 2026-10-12 brief.

| # | check | expected (source) | traillab, 2026-10-12 |
|---|---|---|---|
| K1 | Table-17 pair (chi37), Tables 3-5 (chi38) | outputs equal, digest a856d46e 4b46eb28 4935248c 92a2fc98 e0fb2610 10a9951f 54264f5b 80954580; 0 failing rows (rows -4..-1 are the CV and carry no conditions) | full digest printed and equal; 0 failing rows, model conditions 0; rebuild exact; 20,000 random draws: 0 inconsistent, 0 replay / expansion / incremental mismatches |
| K2 | W22 s1-set; W24 s1-set (r2224 enum) | 9,830,400 = 75*2^17 vs cell 2^22; 285,212,672 = 17*2^24 vs cell 2^28 | equal (exhaustive 2^32), 6 XOR patterns, chi pattern 32/75 |
| K2 | q_event/q_cell, uniform W22/W24 model | 1275/512 | integer identity 9830400 * 285212672 * 512 = 4194304 * 268435456 * 1275 holds |
| K2 | eq36 <=> eq24 and dW26 = 0 (r2224 section 1) | 0 counterexamples | `window --equiv 24,26`, 2^28 real samples: 20,293 with both, 0 predicate-without-EXACT, 0 EXACT-without-predicate |
| K2 | backward row 22 (r2224 consts/sign) | X_E = 0 Pr 1; only (24n,23n,15u); other 7 signings Pr 0; dW23 = dW25 = 0 PROVED; dW24 / dW26 requirements | equal |
| K3 | real-pipeline EXACT/cells, chi37 rows 22..36 (r2224 validate) | 2.4648 +- 0.0145 | 2.45648 +- 0.04074 (2 seeds x 2^27 samples); a separate run at np 8192 gave 2.4934 +- 0.0424. Test: the two 95% intervals overlap. log2 P(rows 4..21) = -58.92 / -58.98 |
| K4 | four patterns (r37_unforced.md, pkgR37P) | 8 value bits of E18/E19 = 6 parities; 4 patterns; q3 gain about +2.0 (1.98) | the 6 parities admit exactly 4 of 256 patterns, the printed one among them; on 512 SMC prefixes rows 18..21 pass 1024 times without the 8 values and 1024 times with the parities (equal), exactly 4 patterns occur (266/253/246/259); rows 18..21 gain 2.057 bits; **q3 gain 1.9919 bits** (4 seeds each, np 8192) |
| K5 | expansion artifact (expansion_audit w22, why) | W22 bits 13,17,26 and chi38 W23 bits 13,17,26 NOT free; held-fixed model gives '+3' | `flip`: all 8 dW24 (chi37) and all 8 dW25 (chi38) equal the audit tables, only the printed pattern (110 / 111) keeps the later differences; real expansion: R2disputed/cells = W23free/cells = 1.00000 exactly; `--hold-from`: 7.767 +- 0.304 (chi37) and 7.801 +- 0.419 (chi38), i.e. the '+3 bits' artifact is reproduced and detected |
| K6 | row-16 table (r37 proof 6.2) | 1,052,672 (u,l) pairs, 1,042,240 distinct u, 28 of 32 l nonempty | `rowtable`: equal (exact, 2 s) |
| K7 | study-B q3 (r37 proof 7.4) | mean 2^-73.9987, 99% bound 2^-74.0225 | 2^-73.9646, seed sd 0.048 (4 seeds, np 8192, m 512, mt 4096); a 2-seed run at mt 16384 gave 2^-73.9944. Test: within 3 standard errors of the study mean (replicate sd 0.0545 bit) |
| X | W8 A0-variant set; F7 (chi37); F7, G (chi38); chi38 E16 (32 words); chi38 E19 relaxed (2^26) | allg_classes, smc_exact, R38M fam38.c / r16enum.py, job104 measure.c | equal |

### Fixes made while working backwards (2026-10-12)

- **Window final stage, windows that start after row e1+1** (`smc.c`, `tl_window`). The late words were redrawn only when the window started at or before e1+1; otherwise each particle gave one sample and `--mt` was ignored (chi38 rows 23..37 had 1,024 samples and 0 cell hits, so the chi38 W23 tests failed). Now the late words are redrawn for every final proposal whenever the model has late words, and a redraw that breaks a prefix row is rejected and counted. chi37 rows 22.. is unchanged (bit-identical counts).
- **Test parser** for the K3 ratio read the wrong field of the summary line (fixed in the test, not in the expected value).
- Added for the known answers: `flip`, `rowtable`, `window --equiv`, `exact --hist`, the per-seed and summary q3 line, the full digest in `check`, and the artifact mode `--hold-from` (needed so the tool can show it detects the held-fixed artifact).

## First readings from the tool (COMPUTED, small runs; not established beyond these runs)

- chi38 rows 22..37, event out, 8.4M samples on one seed: EXACT/cells = 2.85 +- 0.44, i.e. about +1.5 bits. This is the r38 counterpart of the r37 late-rows lever (2.46). It needs fresh seeds and larger runs before any credit.
- chi38 W23 bits 13, 17, 26 (`W23free`): ratio 1.00000. This agrees with job104's "gain 0".
- chi38 SMC prefix log2 P(rows 6..21) = -85.13 (row 16: exactly -27).
- (2026-10-12, after the window fix) chi38 rows 23..37, one seed, 2.1M accepted samples: EXACT/cells = 2.27 +- 0.41; log2 P(rows 6..37, cells) = -100.87. Small run, not established.
- (2026-10-12) chi37, E18's 8 bits and E19[29] enumerated with every other coordinate of an SMC prefix held: exactly 2 of the 4 parity patterns pass rows 18..21 on every one of 512 prefixes (1024 = 2 x 512). The four patterns appear in equal shares over prefixes, so the gain of 2 bits comes from prefixes in which the printed pattern is not among the 2.

## Not done

- **No reduced-width model.** All counts are at full width.
- **K7 / K4 tolerances.** The q3 test accepts 3 standard errors of the difference from study B's mean, using study B's replicate spread (0.0545 bit) or ours if larger; the q3-gain test uses the same rule around 2.0. The K3 test accepts overlapping 95% intervals. These are Monte-Carlo checks, not exact ones.
- **K4 "4 patterns" in the full system.** The tool proves 4 solutions of the 6 parities and finds exactly 4 patterns on SMC prefixes over rows 18..21. The all-solutions solver statement over the whole 37-step system (r37_unforced.md) is not re-run here.
- **`flip` is word-level.** It writes the bits into W_t directly and re-expands the later words; it shows that the modular differences downstream change. The consistent-message version of the same question is the `window` ratio (R2disputed, W23free = 1.00000).
- **Two-bit and `+` conditions in `backward`.** The X distributions do not apply them; they are listed as a model assumption.
- **Joint value-dependent schedule terms.** When a dW_t has two or more value-dependent terms, `backward` prints the requirement but does not enumerate it.
- **The window carrier.** When a window starts inside the E-driven rows, the exact event is counted only on carrier samples. For the fully exact event use `--carrier none`, which may be slow, or start the window at e1+1.
- **chi38 transcription.** The cells come from our R38M proof text, not from a new reading of the PDF. They are checked against the published pair: 0 failures on every printed condition.
