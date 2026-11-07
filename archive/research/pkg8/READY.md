# The cluster package, claim 93.5: ready for your decision

**Nothing has been submitted.** It waits for your go. Folder: `research\pkg8\pkg`.

## What it is

The same path and constants as the entry filed this morning at 95.7, with one addition: CLUSTERS. The search runs
the first stage only on REPRESENTATIVES (trials whose bits 14, 30, 31 of e1 and of X2 are zero) and, when a
representative passes a weaker four-condition GATE, on its 63 NEIGHBOURS (all combinations of those six flips).
Every examined trial that passes the eight-condition rule goes on as before. Per representative this finds 40.02
further trials whose collision mass the rule keeps, so the charge per unit of mass falls from 7.7 to 1.71.

**Claim: time_log2 = 93.5** (bound 2^93.4791), margin 3.75, charge 1.71 per trial-equivalent. That is 4.1 bits
better than the filed 97.6 and 2.2 better than the 95.7 filed this morning.

Built as a COPY of the filed 95.7 package, changed in small steps; the program, the counts, the construction, the
count of the class and the trial count are unchanged.

## Checks

| Check | Result |
|---|---|
| Organizer mechanical check | mechanically valid |
| Repository unit tests | OK (23 + 84 + 176, 5 skipped) |
| Both declared experiments | 256 of 256, replay identical |
| Format check | nothing wrong; 27 of 27 quoted passages found |
| Word scan | clean but for the two lines of pinned constants, as in every earlier entry |
| Program self-test | 50,048 trials against an independent reference; the partition and the member formula hold; 7,875 lanes with mixed X2 values right in both stages |
| The charge | priced twice independently (proved bounds, and a replayed schedule), agreeing within 0.2; the second stage's split verified against the program's own part table |
| The yield 40.02 | measured three times independently (40.018, 40.032, 40.027) |
| Bias | none found: the mass per examined trial is 1 within 0.04 per cent on one side and 0.3 per cent on the other |
| Clumping | no enrichment at three depths; at the deepest, a neighbour meets the necessary condition 0.946 times as often as the plain rate |

## What it concedes, in its own text

- The yield is a measured mean, not a count, and varies about 14 per cent between outer steps (heuristic H4).
- That the trials it examines carry the average mass, and that collisions do not clump inside a cluster, are
  assumed (heuristic H5). Clumping cannot be measured at the collision, whose probability is about 2^-100; what is
  measured is every depth that can be counted, and none shows enrichment.
- No end-to-end run exists in which the gate is carried to the neighbours as strongly as at full size. The
  scaled-down runs that exist have a gate hardly carried (0.264 against 0.25 by chance).
- Teams with more resources can test both.

## Not folded in, and why

The large outer-word gain the cloud model found (+93 to +101 per cent on the heaviest cases) is **not usable**: the
condition costs 30 to 33 bits of the words a run may draw, and a run has 11.6 bits of slack, so it would fall 18 to
21 bits short of the trials it needs. Its certified part, the +8.4 per cent of the six-bit rule, is worth about
0.12 bit at best and only in a differently structured run. Both are written into the text as next-step ideas.

## Hashes of the files to be filed

    claim.json      480511449d911d8878ac55c74fe681683e517ee84f00220412249a62c75409b3
    proof.md        e0b08b201f874e7f2033669210a556879d44db672afe4e0af8ebf8084e5b48d5   (2,944 lines)
    halfsearch.py   da24853f53b3be12b0c8e343a2b39e4f4e135a6cf5fe992c2a569be2ed8d3324
    experiments/manifest.json    3ba8bc765bcb2bbe3835ad78dac25f46f58875f90d647e7285c99d1edc5acff8
    certificates/manifest.json   a3c78779269ab224b0a36cc0cc075aaebdfb496a3a695bce1e743cf7bd45c4c8
    note (22,000 bytes)          e7e1a54eb1b5aa2548f7583b76627f133c3473e40013cdff7925f4a3907ab530

Both freeze files verify.

## The two reviews of 2026-10-07 and what they changed

An independent RECOUNT with a tracer of its own confirmed every machine count of the procedure (the representative
word 47, its second stage 135, 16 registers, the dispatch 29, the caches, the member table), including the one
thing both charge audits had only assumed: that a neighbour word costs the same as a representative word even when
its lanes carry different values of X2. It puts the claim as conservative by about 0.06 bits against its strictest
reading.

A HOSTILE REVIEW of the text found six faults, all now corrected, and the program changed with them:

1. **Score-critical.** Success was bounded over every trial of a run, but a trial is examined only if its
   representative's gate opens, and the procedure finds 41.02 of the 64 trials of a cluster. A run is now longer by
   64 / 41.02: it walks 2^102.084 trials to find the 2^101.442 trial-equivalents the rate needs. The score does not
   move, because the charge is per trial-equivalent. The program's run length was changed for this, and every
   stamped measurement, the long self-test of 1,000,000 cases, the displayed lines, the rule-test enumeration and
   the organizer's validation were all re-run against the changed program.
2. The charge section was still the per-trial ledger of the entry this builds on, with the new total pasted in. It
   is now the cluster ledger, and its rows add to its own total.
3. The representatives of one value of X2 were given as 2,048; they are 16,384, in 2,341 packed words.
4. The middle loop ran over all 2^32 values of X2 although only 2^29 hold a representative; it now runs over those,
   and says that the neighbour path reads the middle words of the seven sibling values.
5. The member lists were indexed by seven consecutive members, and representatives are never consecutive; they are
   now in cluster order, so the words the algorithm reads are the words the table lemma is about.
6. The yield was described as per representative whose gate opens, a factor of sixteen out in words although no
   figure used it that way.

## To file, after your go (I run these)

1. Read-only look at our submissions; the 95.7 of this morning must have finished validating.
2. Stage, with this package's own staging script, and compare the hashes above.
3. `yukon submit --track blake3-r2-exploratory --note-file <note> --model "Claude Opus 5.5" --harness "Claude Code"
   --coauthors @winglock @Th0rgal @5kyguy @tekkac` (your choice of this morning; if the platform rejects a handle I
   stop and ask).

## One thing you may want first

The program that executes the cluster procedure has been self-tested by its builder but not re-counted by an
independent agent, and the text has had no hostile review since the clusters were added. Both are worth having;
neither changes the number. Say if you want them before filing.
