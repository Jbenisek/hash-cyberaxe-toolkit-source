Let R = 16,384 be the representatives of one representative value of X2 (one
value of X2 in eight) and 2,341 the packed words that hold them. Every row is
units (operations, loads and stores counted by the program's machine) times an
upper bound on how often a run executes it; a row with a budget runs at most
that many times, because the algorithm halts with failure when a count reaches
its budget (step 4). The walk is J rounded up to whole values of C0.d1,
1,184,670 * 2^64 pairs.

| Row | How often over a run, at most | Units | Per representative |
| --- | --- | ---: | ---: |
| loop control per value of C0.d1 (bound in words) | 1,184,670 | 16 | 0.000000 |
| loop control per outer step (bound in words) | 2^52.176 | 8 | 0.000000 |
| outer step | 2^52.176 | 260 | 0.000000 |
| table build, 149,797 words per outer step | 2^69.369 | 74 | 0.000001 |
| group: 8 middle steps, mixed words, loop entry | 2^81.176 | 1,250 | 0.076294 |
| representative word, stage A and store of z | 2^92.369 | 48 | 6.858398 |
| representative word, gate test and load of z | 2^92.369 | 10 | 1.428833 |
| representative word, stage 2 | E | 135 | 0.602789 |
| open-gate word: gate word routed, dispatch | G | 31 | 2.323623 |
| open gate: cluster entry and exit | G | 33 | 2.473534 |
| neighbour word, stage A | W | 47 | 31.724992 |
| neighbour word, stage 2 | S | 135 | 22.096795 |
| **total, per representative** | | | **67.585260** |
| **charged, per trial-equivalent** | | | **1.65** |

The charge is the total divided by the 41.02 trial-equivalents of a
representative, 1.647618 to within 3 parts in 10^7, rounded up. The routing is
in the rows: every value that crosses a boundary between pieces is stored and
loaded - z, 2 per representative word; the gate word, 2 per word with an open
gate; per open gate the gate word, the zero, the list position and the
representative stage-2 count, stored at entry and loaded at exit, and the
neighbour stage-2 count, loaded at entry and stored at exit. Only the resident
words and the two counter registers stay in registers between pieces, and
every piece runs within the 16 registers of the machine of 6.5. Group units:
the middle step of the representative value 128, of each of the seven others
122, the mixed words 258, the class loop entry and list start 10. Cluster entry
28 (route out 3, gate budget test 7, neighbour-A budget test 7, neighbour
position 9, j stored 1, neighbour stage-2 count loaded 1), cluster exit 5,
dispatch 30. Stage 2 is charged whole at 135; the split at the cheap test is
not used. List and table loads at the list position cost one load with no
address arithmetic, as in the filed program; the neighbour position is formed
and counted. The two loop-control rows are bounds stated in words in 6.4;
every other row is a machine count of the submitted program. The charge, 1.65
per trial-equivalent, is therefore an upper bound on the cost of the search on
every run. The cost table of the entry this package improves on, which charges
7.7 per trial without clusters and claims 95.7, is Section 12.

- **Lists.** The lists U and V of the cluster layout, 149,797 words each (the
  2,341 representative words, then nine words for each representative holding
  its 63 neighbours), are computed once per run from eta, the sub-class, Y3 and
  the rule: below 2^28 operations, a bound stated in words and not a count.
