# g1feas

Source: `research/newpaths/counter_next/knobs/g1feas.py`

Public SHA-256: `632d5af25c922e100228b2dbe7d0efcb8885c8b4bd5330311bef0d74b26a20c3`

## Purpose recorded in the source

g1feas.py (counter_next/knobs; research only): an outer-step filter for the EXISTING cube program.

In the counter arrangement Y9 is fixed per outer step, and a success with outcome j needs
g1 ^ g1' = ROL(tau_j ^ ROR(tau_j, 1), 12) with g1 = Y9 + h1, h1' = h1 ^ eta.  If no h1 at all meets that for any
of the seven beta* outcomes, the outer step cannot succeed and its 2^21-trial cube loop can be skipped.
This measures the share of uniform Y9 for which the condition is feasible for at least one beta* outcome (exact
carry-pair automaton per Y9), and checks the claim 'infeasible => no success' on the exact counts' own terms:
the outcomes' E3 counts N_j are sums over Y9, so their whole mass lies on feasible Y9 (DERIVED).
usage: python -B g1feas.py NY9 SEED

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "e3dfs",
  "math",
  "random",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
