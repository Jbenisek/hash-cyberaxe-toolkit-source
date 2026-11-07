# Run record

The individual scripts were executed during this research pass. Then `python check_all.py` replayed the native checks, quintic chart, exhaustive toy, extra checks and document generation successfully. That replay logged 10.794763669999611 wall-seconds in reports/check_all_run.log. This is execution/replay time, not total research/review time and not a cryptanalytic work estimate. The later grid consolidation does not rerun search.

The data_run.log and low_round_run.log are earlier successful runs. Timings differ between runs. Authoritative final benchmark inputs are data/benchmark.csv; the workbook was refreshed from that file before export. All counts and algebraic outputs are deterministic for the saved seed.

Only 3 permutation and 11 hash vectors were checked, for 14 official vector tests. The proposed PR's separate claim of 22 vector checks is not this package's executed coverage.

Workbook: 24 sheets; no formula errors found in the final scan; dashboard preview inspected. Optional build_workbook.py requires artifact_tool and recreates the populated workbook, while native mathematical reproduction does not use it.

Local file manifest hashes do not authenticate an upstream repository checkout. The constants are independently regenerated from the pinned official generator and checked against the transcribed official vectors. A full literal comparison against all192 upstream fp.rs constants was not performed in this pass.
