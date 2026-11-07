# L002 partial summary

As of 2026-10-27 20:24 MDT, item 4 remains complete (21 terminal rows: 8 `UNSAT`, 13 `UNDECIDED`, 0 `SAT`). PM's priority sparse42 run (item 2) completed six one-lane full-state checks; all six are `UNSATISFIABLE`. Item 5 is bounded by that same run: no dense 42+ candidate survived for a separate descent timing.

Item 1 is stopped after the required positive control because the supplied witness JSON uses lower-case `m1/m2`, which the tool does not accept; the exact traceback is in `positive_control_error.txt`. Item 3 has supplied files but still lacks an approved pin/solve command. Therefore this is a partial handoff and **not** an `L002 DONE` result.
