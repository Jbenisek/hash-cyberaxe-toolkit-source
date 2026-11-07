# e1_arms.sh: E1 outcome rate (seven outcomes, Lemma N's eps) on real 32-bit trials, 2^45 trials per arm (research only)

Source: `research/newpaths/untried/b3-thi-walk/real/e1_arms.sh`

Public SHA-256: `9b6d48d772fe3c25f94d24fc206e1a44985689e3a7694d96b8a6fbb0f4e885a5`

## Purpose recorded in the source

e1_arms.sh: E1 outcome rate (seven outcomes, Lemma N's eps) on real 32-bit trials, 2^45 trials per arm (research only)
  walk       2^16 groups (context, member) x 2^8 random steps of their full blocks x all of Q*
  ctl        2^24 fresh (context, member) outer steps at t_hi = 0 (the front line) x all of Q*
  walkdense  2^8 groups x 2^16 steps: per-group dispersion with everything but t_hi fixed (Y12, w12, w5 fixed)
  ctxdense   2^8 contexts x 2^16 members at t_hi = 0: the front line's per-context dispersion (w12, w5 fixed)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/newpaths/untried/b3-thi-walk/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
