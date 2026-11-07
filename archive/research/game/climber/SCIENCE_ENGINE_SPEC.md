# Round Climber - science engine spec (from Ledger, 2026-10-23, CyberAxe order)

> **Revisions 2026-10-23 (Ledger, after the game dev questions in reply.md):** stage A walls only on the exact word rule (XOR-linear = predictor badge); cost meter = schedule cost estimate only (compression not priced); word sizes 8/12/16 (not 10); v1 one CNF per shape; DRAT deferred; label `Candidate - needs full scan`; encoder in JavaScript with our CaDiCaL WASM kit in kit/. reply.md answers take precedence over the text below.

Goal: let a player test any shape at any depth, up to the full 64 steps, with real maths in the browser, and send
real candidates to the server. The game never says "works" unless a solver found a pair and the game re-checked it.

## 1. Verdict ladder (labels shown to the player, in this order)
| Stage | Runs where | Label on success | Label on failure |
|---|---|---|---|
| A. Necessary checks (schedule spread, bit conditions, rank, freedom) | browser, ms | `Passes checks to row N` | `Wall at row N (why)` |
| B. Cost meter (sum of per-row condition costs, log2) | browser, ms | `Cost 2^c, under budget` | `Over budget at row N` (cannot beat generic) |
| C. Scaled solver ladder: same 64-step function with word size w = 8, 10, 12 | browser, Web Worker | `Solved at w=8/10/12` (pair re-checked) | `Impossible at w (proved)` or `Unknown at w (cap)` |
| D. Full size (w = 32) | server only | `Candidate - queued for full scan` | - |
Never collapse these. "Passes checks" is necessary, not sufficient. Full-size is "not yet tested" until the server answers.

## 2. Budget
- Generic bound for a collision on a d-bit digest: 2^(d/2). At word size w the digest is 8w bits, so the bound is 2^(4w)
  (w=8: 2^32, w=12: 2^48, w=32: 2^128). Stage B compares the shape's summed cost to this bound for the chosen w.
- The contract toggle (standard IV / semi-free-start / free-start) changes the freedom shown, not the bound.

## 3. Solver
- Use CaDiCaL (MIT licence), compiled with Emscripten (-O3) to WebAssembly, run in a Web Worker with a hard time cap
  and progress messages. Same DIMACS also runs natively (kissat or CaDiCaL) on the server for stage D, so browser and
  server answers are comparable.
- Caps: w=8 10 s, w=10 60 s, w=12 300 s (player can raise to 15 min locally). Stop the worker at the cap: verdict Unknown.
- SAT result: decode the pair, recompute both hashes in plain JS at that word size, accept only if digests match.
- UNSAT result: record it as "impossible at w" (optional: emit DRAT and check with drat-trim compiled to WASM at w=8).

## 4. Encoder (reuse ours, port to the planned Rust engine)
Port the scaled SHA-256 encoder into the Rust engine (it is listed as "not built yet" in README.md); output DIMACS
plus a variable map. Reference implementations to port from (read them; same scaling rules must be kept):
- `research/levers_1021/s256_scaled_sim/gen_scaled.py`, `gen_w8.py`, `CALIB.md` (scaled model + calibration)
- `research/tools/fast/decide_shape.py` (shape -> case partition) and `colclimb_local.py` (per-bit difference variables)
- Research system's encoder notes: `HashSmash_Library/_sources/research_system/RIVER_1021/tools/sat/README.md`
A shape = active message words + contract + word size; the encoder adds the difference constraints for that shape.

## 5. Controls (run at load, like the five existing ones)
- Known pair at w=8 for a short step count: must return SAT and re-check.
- A shape known impossible at w=8 (take one closed UNSAT case from the knowledge base): must return UNSAT.
- Hash test vectors at w=32 for the plain JS hash. Any control failure -> engine shows "not verified" and blocks stage C.

## 6. Recording (science output)
Append every stage-C run to `public evidence index` (existing format): shape hash, contract, w, verdict, seconds,
solver + version, engine version, seed. Plot seconds vs w per shape; label any extrapolation "trend", never a result.
Flag as ODD: a pass where neighbours wall, an UNSAT that closes much faster than neighbours, a SAT at a row past the
current frontier. ODD shapes go to the top of the server queue.

## 7. Candidate export (stage D)
One JSON per candidate: shape, contract, row reached, cost, stage-C verdicts, encoder version, seed. The server team
runs it at w=32 and posts the verdict back into the knowledge base.

## 8. Wording
This is research on computational cost bounds. Use: research, test, search, bound, shape, candidate.

## 9. Processing what players send back (our side)
1. Collect: every stage-C record and candidate JSON lands in one queue (ANSWERS.tsv + candidates/).
2. Trust nothing from clients: re-check every claimed pair by recomputing the hash; re-run every claimed "impossible"
   at the same w on our engine (or check its DRAT). Records that fail the re-check are dropped and the client flagged.
3. Dedup by shape hash + contract + w; merge counts (how many players, how many seeds agree).
4. Rank candidates: deepest row reached under budget, then most word sizes solved (8/10/12), then lowest cost,
   then ODD flags, then novelty (distance from shapes already closed). Keep many diverse paths, not only the top one.
5. Promote the top K per day to the server for w=32 (6 threads max), with interim posts every 30 min.
6. Feed back: closed shapes and server verdicts go into the knowledge base the game reads, so players see what is
   done and get steered to open ground; ODD shapes get a visible "lead" badge and credit to the finder.

## 10. Grid work and lever learning while people play
A. Every move is an experiment. When a player toggles a word or bit (a lever), record before/after: wall row, cost,
   rank, freedom, stage-C verdicts. Store (shape_before, lever, shape_after, deltas). Over many players this gives each
   lever's measured effect, how often it helps, and which pairs of levers combine or cancel (interaction table).
B. Background grid cells (volunteer compute). While a player is on the page, the Web Worker pulls one small capped job
   from a server-issued queue (a grid cell: shape + contract + w + cap, 10-60 s), runs it, and returns the verdict.
   Only with the player's opt-in toggle; pause when the tab is hidden or on battery.
C. Redundancy: each cell is issued to at least 2 players with different seeds; a verdict counts when they agree and our
   re-check passes. Disagreements are re-issued and flagged.
D. Coverage map: the queue fills the grid systematically (rows x word patterns x contract x w), plus a share of random
   cells, so the map has no blind spots and the lever statistics are not biased toward what players like.
E. Fair comparisons: 10-20% of "Random climb" and "Daily challenge" shapes are assigned by the server (randomised), so
   lever effects can be compared like a controlled experiment, not only from player choices.
F. Outputs, published in the knowledge base and the game: grid heat map (closed / open / ODD per cell), lever cards
   (measured effect, success rate, best partners, worst partners), and per-player credit for cells closed and leads found.

## 11. More science from the website (ideas, ranked by value)
1. Human-guided splitting (Foldit-style): show a hard cell as a puzzle; the player picks which bits/words to split on
   first. Record which human splits close cells fastest -> learn better branching rules for our solvers.
2. Predict before you run: players guess the verdict (found / impossible / unknown) and time before a cell runs. Score
   their calibration; the crowd forecast orders the queue, and good forecasters' picks get priority.
3. Active learning: a small model predicts each cell's verdict and cost from shape features; the queue hands out the
   cells the model is least sure about, so every player run teaches the model the most.
4. Breed shapes: a "combine" button crosses two players' shapes (and mutates bits); the population evolves toward deeper
   rows under budget. Records which combinations of levers survive.
5. Toy ladders for full maps: tiny versions (fewer steps, 4-8-bit words) small enough to map exhaustively. Complete maps
   give scaling laws (how walls and costs move with word size and depth) that we can test at full size.
6. Solver internals as data: from each run keep conflicts, decisions, learned-clause sizes, time to verdict. These
   hardness features say which shapes are close to closing and feed item 3.
7. Peer check queue: players re-run and confirm other players' results (counts toward the 2-agree rule in section 10).
8. "Why I tried this" notes: one optional line per saved shape; mine the notes for ideas and recurring intuitions.
9. Other protocols as separate modes later (Poseidon, BLAKE3, SHA3 toy versions), each with its own grid and cards.
10. Machine timing: each client benchmarks a fixed workload; gives real time-per-operation across hardware to calibrate
    cost estimates.

## 12. "Is this shape new?" check (publication ownership note: tell the player at once whether a shape is already known, so finds are not re-reported as new routes.
- Data: `kit/known_scan_cands.json` (from the research system's row-40 scan: `n` = 419 candidates scanned, `rows` = the
  survivors kept, each with `dw` = the 16 message-word differences as hex, `D` = active message words, `L` = active
  expanded words, `kdim` = freedom). Load it, plus any further `kit/known_*.json` files we add later, into one list.
- Test, for the exported shape (all 2^freedom difference vectors in its span, not only the witness):
  1. EXACT: some known `dw`, shifted by s words (s from -15 to +15, words shifted off the end must be zero), equals the
     player's 16 differences -> label `Known: research scan, candidate #i (shift s)`.
  2. SAME FAMILY: the active-word set D matches after a shift, but the bits differ -> `Related: same family as candidate #i
     (shift s), different bits`.
  3. Otherwise -> `Not in known lists` (this is NOT "new route"; it only means not seen in our lists).
- Show the label in the Inspector next to the shape id, and write it to the export JSON as
  `"known_check": {"label", "candidate", "shift", "lists": [file names + sha256]}`.
- Control at load: the owner's export S3F00.0503 (witness words W8..W12 = 80000000 11002000 80000000 14044aa8 00205000)
  must come back CORE against candidate #0 with shift -1 (core W9..W13; candidate also has W0). If it does not, show
  "known-check not verified". Levels: EXACT > CORE (shape's nonzero words = a consecutive run of the candidate's, candidate
  has extra active words) > SAME FAMILY > not in known lists. (Corrected after reply.md question 29.)

## 13. Echo arrows, hallway and wall hint (publication ownership note: W_t = σ1(W_t−2) + W_t−7 + σ0(W_t−15) + W_t−16, so a difference in word t comes back at t+2, t+7, t+15, t+16
("echoes"). A row is free (zero difference, zero cost, even with real carries) when every one of its four inputs has
zero difference. A wall happens when an echo lands on a row with nothing to cancel it (exact word rule).
1. Echo arrows: for each active word (message or expanded), draw thin arrows to rows t+2, t+7, t+15, t+16 (only rows
   on screen). Colour: green when that arrow is cancelled on the target row by another active input; red when it
   is alone (that red arrow IS the wall reason). Toggle with a key (E). Inspector line on the wall row:
   `Wall: echo of W24 (+15) lands alone`.
2. Hallway stat: the longest run of consecutive free rows directly below the wall (rows whose four inputs all have zero
   difference). Show `Hallway: rows 29-39 (11 rows, free)` in the Inspector and export `"hallway": {"from", "to", "rows"}`.
   Label it free under real arithmetic too (zero-difference inputs give a zero-difference output exactly).
   Use it as a shape score alongside height: long hallway = cheap tail.
3. Wall hint: when the wall row has exactly one uncancelled echo, show `To pass this wall, another active word must
   echo onto row N and cancel it: candidates are W(N-2), W(N-7), W(N-15), W(N-16)` with the ones that are message
   words or already-active words highlighted. This turns every wall into a concrete next move for the player.
Control (corrected): on the owner's S3F00.0503 export the game must show hallway 35-39 (5 free rows), clean rows 29-39 (11), and the wall reason
`echo of W24 (+15)` on row 40.

## 14. Families, shown in the game (owner question 2026-10-23)
- Family = the pattern of lit message-word tiles (W0-W15), ignoring where it starts. Write it as a binary string from
  the first lit tile to the last: W8 W9 W10 W11 W12 -> `F-11111`; W0 + W9..W13 -> `F-1000000001111` (W0, then 8 dark tiles,
  then 5 lit). Shifting the same pattern left or right keeps the family; the row where things happen shifts with it.
- Member = one exact set of bit differences inside a family (the hex words). Many members per family.
- Counts: 32,768 families exist in total (patterns anchored at their first lit tile, 2^15); 120 of them have at most 6 lit
  tiles inside an 8-word window (the grid's range, 1,206 placements).
- Show in the Inspector: `Family F-11111 (shift: starts at W8)` and a family card: members tried, best height, best
  hallway, walls seen, known-list status (section 12). Export `"family": {"id", "start"}`.
- Language rule in the game and our notes: "different family" = a different lit-tile pattern; "same family, new member" =
  same pattern, different bits.

## 15. Open-ended play and frontier finds (CyberAxe 2026-10-23)
- No limits: any of the 32,768 families, any member (bits), any contract, tower to row 64. The grid's 120-family range
  only sets the order of background work, never what a player may try.
- Frontier find: a shape whose height reaches row 40 or more (word rule passes AND a difference witness exists in the
  game's model) is flagged `Frontier find - row N` with a gold badge, kept even if stage C is Unknown, and goes to the
  top of the export queue with the finder's credit attached.
- What we do with a frontier find (our side, report back into the knowledge base within a day):
  1. re-check the word rule and the witness;
  2. real-carry schedule cost and the exact word-status decision (`research/tools/fast/decide_shape.sh`);
  3. per-bit column climb on its first wall (`colclimb_local.sh`);
  4. full-state solver ladder w=8/12/16, then the full-size run on the server if it survives.
  The player sees each step's verdict on the family card.

## 16. Player framing (CyberAxe 2026-10-23)
Players are pattern finders. Their job is to spot shapes, families and oddities that give the research team more
things to test. Write every in-game message that way: "You found a pattern worth testing", "Sent to the research team",
"Your find was tested: <verdict>". The game never implies that a find defeats SHA-256; a frontier find is a lead,
and the team's tests decide what it means.

## 17. Reward system: thousands of human researchers (CyberAxe 2026-10-23)
Why: the space is far larger than any team can cover. Word level alone: 65,535 active-word sets x 48 target rows
(17-64) x 3 contracts x 3 word sizes = 28,311,120 cells; we have run about 8,700 tests across all tracks (~0.03%).
Bit level: 2^512 - 1 message differences (3^512 ~ 2^811 with signed bits). Players exploring odd corners is the point.
Every reward is paid only after our re-check (section 9), so points always mean verified research.
1. Points (XP) for: volunteer cells completed and confirmed (section 10B); first player to try a family (scout bonus,
   32,768 families to claim); frontier finds (row 40+, big bonus, scaled by height); ODD flags later confirmed;
   accurate forecasts (Brier score, section 11.2); peer re-checks; new hallway length records.
2. Credit that lasts: "Discovered by <name>" on the family card; a public Hall of Fame; finders named in the research
   library's acknowledgements and in any write-up that uses their find.
3. Progression that teaches: level 1 word tiles + tower; level 2 echo arrows + hallway; level 3 bit levers; level 4
   breeding; level 5 solver ladder to w=16 and grid volunteering. Each unlock comes with a 60-second tutorial.
4. Achievements: Scout (10 new families), Cartographer (100 closed cells), Oracle (forecast Brier < 0.15 over 50),
   Wall Reader (explain 20 walls with the hint), Hallway Builder (hallway 12+), Frontier (row 40+), Peer (50 re-checks).
5. Loops: daily challenge (section 19 answer), streaks, weekly leaderboards (seasons), teams/guilds that pool cells.
6. Fairness: no points for duplicates (shape_hash), redundancy 2+ for compute credit, rate limits, points revoked if a
   re-check fails. Leaderboards show verified points only.
7. Real-world rewards (money, tokens, prizes) are the owner's decision and must follow local contest/sweepstakes law;
   the game ships with points, badges and named credit only until the owner says otherwise.

## 18. Family on screen (CyberAxe 2026-10-23)
Family = lit message-word pattern ignoring position (§14). The player must SEE it.
1. Family ribbon (Control Deck, under "CLIMB COMPLETE"): a 16-dot strip of the lit pattern, normalised to start at the
   first lit tile, plus its id in run-length form (lit-dark-lit...): W1 + W8..W12 -> `Family 1·6·5`, start W1.
   Colour = family hue (hash of the id -> hue), so the same family always has the same colour, in every session.
2. Lit keys take the family hue (border + glow). Changing family changes the hue of every lit key at once.
3. Family glyph on every key (bottom-left corner; the +n / −n / x badge stays top-right): what pressing it does to the family.
   ★ green  = new family nobody has tried yet (scout bonus)
   ● blue   = family tried by players (tooltip: players, best height, best hallway)
   ◆ gold   = family in the research known lists (tooltip: candidate #, CORE/EXACT)
   ✕ grey   = the result is not a valid shape (e.g. forced zero at once)
   Tooltip: `→ Family 1·6·4 (12 players, best 33)`.
4. Shift ◀ ▶ buttons beside the key grid: slide the whole pattern one word left/right. The family stays the same
   (the ribbon does not change); only the start word and the rows move. This teaches what "same family" means.
5. Family card (Inspector): id, ribbon, members tried, best height, best hallway, walls seen, known-list status;
   "Next new family" button jumps to the nearest ★ key.

## 19. Focus the grid: scan less, learn the same (CyberAxe 2026-10-23)
Do not run all 233,460 cells flat. Use the exact orderings below; each closes many cells with one run.
1. Word rule first (milliseconds, no solver): for each word set compute the highest row the word rule allows. Every cell
   above that row is closed without a run.
2. Rows are nested ONLY for "clean through row r" cells (the grid default; kit v3 `clean: through`): the cell at row r+1 has every constraint of row r plus more. The v2 per-row cells (`clean: exact`) are NOT nested (measured: w=8 iv, W8..W15 zero: row 16 UNSAT, row 17 SAT); label the two kinds differently in RUNS.tsv. So UNSAT at row r closes all rows
   above it, and SAT at row r+1 proves SAT for all rows below. Binary-search the rows per word set (about 5 runs for
   24 rows instead of 24).
3. Contracts are nested: iv ⊂ semi-free-start ⊂ free-start (any iv pair is an sfs pair; any sfs pair is an fs pair).
   Run free-start first; UNSAT there closes all three contracts. Only a SAT goes on to sfs, then iv.
4. Word sizes as a ladder: w=8 first; only word sets that are SAT at 8 are run at 12 (an UNSAT at 8 is a strong, but
   not exact, signal; record it as a predictor and revisit only if the crowd flags the set as ODD).
5. Families, not placements: run each family once at its best placement (the one with the highest word-rule row);
   shifted copies only if that run is SAT or ODD.
6. Known lists and cores are skipped (section 12). Then order the rest by the prediction model's uncertainty (section 11.3).
Derived count: 1,304 word sets (1,206 window sets + 98 known families) x about 6 runs each (binary search on rows at
one contract, one w) is about 8,000 first-pass runs, against 186,768 systematic cells flat - about 23x fewer. The same
rules apply to our own server scans.

## 20. More structure to use, and more science to collect (CyberAxe 2026-10-23)
Structure (exact, makes runs cheaper or closes cells free):
1. One CNF, many cells (incremental solving): neighbouring cells differ by one word or one row. Encode the full
   64-step schedule once with an on/off literal per "word t is zero" and per "clean through row r"; a cell is then a
   set of assumptions on the same solver, and learned clauses carry over from cell to cell. CaDiCaL supports this;
   kit v3 should expose `solveAssume(literals)`. Expect large speedups on the grid versus fresh CNFs.
2. Wall autopsy (UNSAT core): when a cell is UNSAT, ask the solver which assumptions were needed (the failed
   assumptions / core). Show "closed by rows 23, 26 and W11" - the player learns what killed it, and the core often
   closes neighbouring cells too (any cell containing the same core is UNSAT without a run).
3. Signed differences: the predictor uses XOR differences; the real object is modular (+/-) differences, and that is
   exactly the W1 model gap. Add a sign per lit bit in the bit-lever view (v2) and record both XOR and signed weight.
4. Local-collision palette: SHA-2 paths are built from a standard 9-step local collision (one disturbance, eight
   corrections). Offer it as a drop-in block; show any shape as "k local collisions at positions ...". Families then
   have meaning the player can reason about, and the palette is how published paths were designed.
5. Two-block mode (later): a first block's output is a legitimate chaining value, which is how published full
   collisions reach further; our two-block assembler spec exists in the research files. Separate mode, separate grid.
Science to collect:
6. Neutral bits on every found pair: for a SAT pair, count message bits that can flip without breaking the clean rows
   (instant in JS). It measures the free tail directly and is the classic cost lever; record it with the pair.
7. Origin tag on every shape: human / grid / random / bred / daily / shifted. Then compare ODD-rate, frontier-rate and
   model-gap-rate by origin. This answers "does human pattern-finding beat the grid?" with numbers - the owner found the
   W1 gap by hand in minutes; make that measurable and publishable.
8. Time-to-verdict scaling per family across w = 6, 8, 12, 16: fit the growth; families whose hardness grows slowest
   are the ones to push to full size first.
