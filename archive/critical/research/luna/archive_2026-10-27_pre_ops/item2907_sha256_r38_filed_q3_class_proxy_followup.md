# Item 2907 — r38 filed q3 class-proxy follow-up

Date: 2026-10-19
Status: COMPUTED/DIAGNOSTIC only; no q3 or score credit.

## Question

Item 2906 used 16 source-level SMC replicates for the embedded 512-variant
table and one representative from each of the 90 filed classes.  This follow-up
adds 32 fresh deterministic replicates to each pool, using the checked-in
`a0lean38.py` estimator unchanged.  It is still not the uniform 345,600-member
filed-family law: the first pool has 512 embedded variants and the second has
one representative per class.

## Results

| pool | replicates | pooled linear-mean `log2` | verified pairs | failed checks |
|---|---:|---:|---:|---:|
| embedded table (512) | 32 | -97.42466863388599 | 292 | 0 |
| one representative / class (90) | 32 | -97.67943460613273 | 299 | 0 |
| follow-up difference (class minus table) | 32 vs 32 | **-0.25476597224674435 bits** | — | — |

Combining item 2906's 16 replicates with this follow-up by linear pooling gives

```text
table512  = -97.57235630614447
rep90     = -97.74380502755886
class - table = -0.17144872141439818 bits.
```

The sign reverses item 2906's 16-replicate result (+0.04080636969790419
bits), which was table512 `-97.92266726589109` versus rep90
`-97.88186089619319`.  The source-level proxy is therefore dominated by
SMC/lineage noise at this sample size, not evidence of a stable class effect.

## Ruling

This panel does **not** decide the filed-family transfer threshold.  The exact
arithmetic still requires the true 90-class, 3,840-member-per-class q3 law to
reach `-97.590324052568` for a +0.1-bit row, while the owned-source proxy is
not that law.  The two panels have zero rebuild failures (591 verified pairs
in total), but their opposite signs require a real filed-family measurement or
a proof; no alert and no score credit are warranted.

Evidence script: `research/luna/r38_filed_q3_class_proxy_1019b.py`.
