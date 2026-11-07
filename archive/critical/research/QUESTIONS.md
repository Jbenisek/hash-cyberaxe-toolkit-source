# The question grid - the owner's questions, asked at every lever and every stage

Built 2026-10-11 from the owner's own questions and what they taught us. Use it like the technique grid: at each STAGE, walk the
questions; each answer must be a number, a file or an action, never "probably". Add new questions as the owner asks them.

## Stage 1 - Idea (before spending anything)
| Question | Why (what it caught) | Action |
|---|---|---|
| Is this a new PATH or a re-pricing? | Promotion goes to techniques; junk filings close edges | Distinct path -> its own entry; re-pricing -> fold into the line's next package |
| What would a home run / leap look like here? | Lean trims are tenths; leaps need structure (blake3 40s) | Name the structural change and its bit size before building |
| What parts of the sphere are we missing? (aliens, macro, micro, inverted, shapes...) | Lenses get lost across contexts | Check research/LENSES.md; empty lens x track cells are candidates |
| Has anything we learned on ANOTHER hash been tested here? | XOR-forms, two-block framework, measured averages transfer (or close fast) | Run the transfer check; record WIN/KILL |
| Did I dismiss this by ARGUMENT at today's speeds? ("are you sure it's not worth it") | Rivals win 0.05s with fast tests; arguments were wrong | Run a <= 1 h test with a control and quote the number |
| In a DENSE area: what boring details does everyone copy without recounting? (owner 10-12: "a dense area should tell you a lot of boring details everyone overlooks") | The hidden W9 condition sat in rows 9-10; every r37 filing copies |F6|, |F7|, |G|, 22,976 classes, g from earlier proofs | Recount every copied number with our own code; list every implicit condition the cells imply but no table prints (research/retest/dense_boring/) |
| Does every PRINTED condition / number hold on the published witness? (owner 10-12: "notice how the AI repeated a book misprint... imagine how many more") | Two paper errata found only by checking the real pair (A16->A15[29] r37; W25[9]->W25[6] r38); models and teams copied them | Check every printed condition of every source table on its published pair BEFORE using it; list violations as errata; check which rivals copied them (research/retest/errata_audit/) |
| Is it in the mill tailings? (an old KILL that today's leaner ledger flips) | 440 kills re-priced -> blake3 -0.047 | Re-price old kills before calling a line exhausted |
| What does the trash say? (near-misses, discarded pairs) | Bias in discards = better rate than charged | Mine discards with controls and split samples |
| Is it in the pre-contest research or the archive already? | A week of ideas applied only to blake3 | Check old research + research/tighten/ARCHIVE_DIGEST.md |
| Is any 2^-k filter really a MATCH? (birthday lens: f(A)=g(B) over independent inputs -> two lists of 2^(k/2)) | Owner 10-12: "think about brute force birthdays"; the r37 leader's row-16 table is one | List every sampled stage; check separability (no expansion coupling); price lists + match + memory under S |
| What do the boring edges look like? (rules, rounding, success, memory, padding, final step) | Rules edges gave the memory-rule packages | Read the organizer docs for the stage; list traps and levers |

## Stage 2 - Measure
| Question | Why | Action |
|---|---|---|
| Measured or copied? ("measure what others copy") | 2^60 allowance, MU 0.0117 vs 0.0044 | Replace conventions by preregistered measurements |
| Is the measurement preregistered, with fresh seeds and a control? | Judges and our own artifacts (Haiku clustering, 4x units bug) | Write the prereg first; pick on one half, score on the other |
| Is the unit right? (F/s in Python vs C, 2^81 vs 2^83) | Two false wins tonight | Recompute every rate on the C reference; check units |
| Could the GPU do this? | GPU idle is waste | Port to CUDA when > 2^30 samples |
| Did we COUNT EVERY CASE, or extrapolate from a few? ("experts count 1+1mil, 1+2mil and never count all the numbers") | Every expert number that failed tonight was a skipped count (2^60, 75 conditions, product models); every number that held was exhaustive | Enumerate exhaustively where the space allows (2^32 per word is fine); otherwise an exact automaton checked against brute force at small widths; sampling only with a stated interval |
| Is the same quantity written the same way everywhere? ("1 + three" vs "1 plus tree") | Units and notation changed answers: 2^81 vs 2^83, Python vs C rates, a compare counted 2 or 3 | Normalise units and operation definitions before comparing any two numbers |
| Which CONVENTIONS does this score rest on, and are they measured? (the alien view: the function does not care about our units) | Every convention is a lever or a risk: 2^60 allowance, MU, pair budget delta | Check each: allowance assumptions, success-threshold margin, operation-unit definitions, setup amortization, memory vs time, early-abort factors, gate probabilities, late-choice multiplicity, solver-timeout semantics |
| Which other levers touch the same rows or words (directly or via the message expansion, e.g. W24 = s1(W22)+...)? Joint or product? | Owner 10-12: "22 and 24 are connected - check them against each other in a grid"; W22/W23 artifact | research/retest/interaction_grid/GRID.md; measure joint vs product on consistent messages before stacking gains |
| Does a smaller-looking count make the PAID route cheaper? | A lower U that worsens the gate or loses late choices still loses | Price the full cost formula (setup + generation x 2^U / late choices), never one term |

## Stage 3 - Build
| Question | Why | Action |
|---|---|---|
| Exact count or best provable case - never a safe bound? | Th0rgal shaved our bounds in 15 min | BUILD_RULES.md rule 1; CHECKLIST.md |
| Are we running lean or overdoing it? | Owner watches cost and speed | Cheap models, bounded runs, no duplicate work |
| Does it pass the checker? | Labels, deps format, ledger/claim mismatch caught | python research/launch/prefile_check.py <pkg> = ALL PASS |
| Is every AI and every base entry credited? | Disclosure + credit rules | AI tools by name; dependencies as objects with full ids |
| Under the memory rule, does this still lead? | Table packages fall from 71 to 131 | Compute S = time + max(0, log2 bytes - 20) for every package |

## Stage 4 - File
| Question | Why | Action |
|---|---|---|
| Does it lead (or is it a distinct path)? Is a retry worth it? | Retries are NOT limited (owner 10-12: '2 of 2 was just to know what is going on; we can retry over and over'); file when it leads or opens a path | File only entries that lead or open a path |
| File it anyway so someone can't next to us? | Gate accepts distinct methods above best | Distinct paths go out even when not lowest |
| Backup first? Is the backup lean? | SOP; backups had grown to 8 GB | backup-project.ps1; frozen history in cold storage |
| Is the rule change ready? (what files the minute submissions reopen) | Re-score window | research/MERGE_FILING_PLAN.md |

## Stage 5 - After
| Question | Why | Action |
|---|---|---|
| Why did it fail? (read the dossier, fix only what it names) | 5a08fffa SEL ruling -> pinned SEL -> lead | fetch_ruling.sh; never refile unchanged |
| HOW did it die, and what does that say about its neighbours? (owner 10-12: "if something is so dead, does that tell us about what is around it?") | A hard kill is a wall on the map: the r38 phi^-1 kill showed W9 validity sits on the same bits as the carries -> the valid set itself may be structured and enumerable from the other side; tonight every "free message bit" died on the expansion, every live gain came from cells stricter than the event | For each KILL record the mechanism (which coupling killed it), then test the reverse side and the nearest square that the mechanism does NOT touch |
| Who shaved us and how? What can we learn from their shave? | Their trims become our checklist | Leader watcher + audit within minutes |
| Is Luna / Grok / Astra / the cloud on the most valuable job? | Luna idled on D131; Grok cloud is 2 cores | Check queues; math to cloud, compute local, counting to cheap agents |
| What can each partner try that's a home run? | Grok cloud kicked [redacted unsafe language] with exact analysis | Keep a ready ask per partner |
| Update the handoff, the credits, the registers | Context resets lose everything else | HANDOFF, ai_credits, LEVERS, LENSES, QUESTIONS |

- [10-13 Primitive, PR858 + judge 83a119de] MEASURE/BUILD: what is the peak memory of this lever INCLUDING preprocessing (char search, Step-1, dev, precompute, advice, libc/allocator)? Does it keep the entry <= 2^20 or what does it cost in score (time + max(0, log2 mem - 20))?
- [10-15 Primitive, rulings 1cd0dd3b/5790b7ac/606bcba0] BUILD/FILE: is every NUMERIC bound in the success proof a PROVEN bound (upper Darboux sums, closed forms - never a midpoint/numerical integral presented as a bound)? Is any distribution law ("K is Poisson", "count is binomial") claimed EXACTLY - is it proved from the construction, dominated by a proven law, or declared as a premise with scope?
- [10-15, ruling 4086e210] FILE: do the claim.json heuristic scope numbers equal the proof's numbers for the SAME quantity (no template field reused for a different size)?
- [10-15, 98b1c2c4] FILE: does the organizer's experiment runner work for this family at all (Poseidon: digest(b"") bug -> declare no experiments)? Check a sibling that passed.
- [10-15, lanes widened to full rounds] IDEA: which per-round frontier rows are EMPTY, and which do we lead? Is the program under 1 MiB at this round count - if not, a rolled round body? Is the algebraic/structured attack still cheaper than generic here (Poseidon r6: ~53.9 vs ~127)?
- [10-15 CLI] FILE: is any dependency id younger than ~5 min (submit says 'not found')? Is the note >= 5 KiB?
- [10-15 owner] AFTER: what did this ruling teach that applies to every sibling entry sharing the same text - prepare all fixes, refile each line only when its own ruling names the issue.
- [10-19 symmetry] PROVE/MEASURE: does a BLAKE3 permutation-fixed base message produce a genuine short cycle of the full pair map, rather than only a repeated difference? Test full-state autocorrelation and replay every candidate spike; do not treat Delta-Ch/MAJ or mixed add/XOR differences as autonomous.

- [10-15 grid walk] IDEA: at which round does each filed structured line cross generic ~125.0 (127.009 Poseidon), and how many bits remain at the last winning row (SHA-256 r39: 0.143; SHA3 r8 extrap 0.22; Poseidon: memory not time is the limit, 213 GB at r7)? Cells GW1015-*; questions_1015/GRID_WALK.md.
- [10-15 grid walk] MEASURE: does our C(r) per family/round equal the organizer's printed constant, and is a row's normalised time constant across rounds in our filings (blake3 slope +0.0011 bit/round)?
- [10-15 grid walk] IDEA: score counts memory 1:1 with time; does a streamed/chunked algebraic variant (4x less memory, ~2x time) make Poseidon r8/r9 executable and still < 127?
- [10-15 grid walk] AFTER: which rivals hold which per-round rows (API shows currentBestScore=null and no frontier list)? Read the pareto repos' PR pages once for the new rounds.
