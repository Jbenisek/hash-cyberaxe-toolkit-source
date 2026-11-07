# Sparse SHA-256 message expansion research

Start with `report/RESEARCH_REPORT.md` and `data/summary.csv`.

**Exact finding:** under the literal cap of at most two differing expanded words at indices >=16, schedules exist through N=40 in both arithmetic models and are impossible at N>=41. Global XOR-linearized minimum weights are 25,44,159,173. Genuine modular minima are not certified; proved intervals are 6..25,6..44,11..120,11..133.

This is a message-expansion study, not a compression-collision generator or a contest submission. Each pair in the files is verified only for the stated schedule properties.

## Files

* `data/results.json`: aggregate results, exact linear witnesses, native bound witnesses, metadata.
* `data/late_supports.csv`: every admissible late support and its exact linear minimum.
* `data/linear_full_supports.csv`: every exact full support S in the XOR model, with counts.
* `data/stopping_N*.csv`: native necessary-support candidates only. These have no header; columns are N,first_late,last_late,support_integer_mask,word_count. Repeated late index means a singleton.
* `certificates/linear_min_infosets.json`: information-set completeness certificates.
* `certificates/*.min.json`: complete 32-dimensional enumerations.
* `certificates/modular_witnesses.json`: full schedules, with all later words recomputed.
* `logs/`: bounded-search and solver records, including UNKNOWN outcomes.

Integers larger than spreadsheet precision are decimal strings in the data feed.

## Reproduce

Python 3.10+ and the standard library suffice for quick checks and the 64-dimensional information-set searches. A C++17 compiler is required for the full rank and enumeration reruns.

    python verify.py
    python verify.py --recompute-supports
    python verify.py --recompute-minima

The last command re-enumerates 22 spaces of 2^32-1 vectors and the three 64-dimensional cases. Its runtime is hardware-dependent. The C++ enumerator uses AVX-512 population count when compiled for a supporting CPU, with a scalar fallback. There is no GPU or network requirement.

The 38-step fixed-mask realization used the system libz3, through a small ctypes wrapper. The returned pair is already present, so Z3 is not needed to check it. Its SAT input and solver output are preserved. No full-path compression check is implied by that SAT result.

CPU times are observations of these executions, not attack-cost estimates or guaranteed reproducibility times. The cached original optimized enumerator is also preserved as `code/min_enum_executed_avx512.cpp`.
