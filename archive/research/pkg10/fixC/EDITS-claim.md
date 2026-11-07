# fixC pairs for claim

### C1: fix 2, 5; base line line 20, restrictions[3], last sentence

OLD
```
The algorithm halts with failure when one batch in 32 has run stage 2 or when 2^84 trials that passed the second test have been processed.
```

NEW
```
The algorithm halts with failure when E batches, just under one in 32 of the batches of a run, have run stage 2, when 2^84 trials that passed the second test have been processed, or when one of three budgets on the neighbour path of proof.md Section 6.7 is reached: representatives whose gate opens, neighbour words that go through stage A and neighbour words that enter stage 2, each 1.2 times its measured mean (proof.md Section 6.4, step 4).
```

### C2: fix 1, 2; base line line 21, restrictions[4]

OLD
```
The success probability 0.39 holds only under heuristics H1, H2 and H3.
```

NEW
```
The success probability 0.39 holds only under heuristics H1 to H6.
```

### C3: fix 2; base line line 28, H1 statement

OLD
```
the probability that no trial has this event is at most exp(-1/2) + 0.002.
```

NEW
```
the probability that no trial has this event is at most exp(-1/2) + 0.001.
```

### C4: fix 2; base line line 42, H1 limitations

OLD
```
the success bound needs a factor of at least 92,532,532.
```

NEW
```
the success bound needs a factor of at least 92,379,824.
```

### C5: fix 5; base line line 62, H3 scope

OLD
```
The budget E is 18,725 * J / 32 rounded down, with J = 2^110 / 92,675,904 rounded up; a run has at least J pairs
```

NEW
```
The budget E is 18,725 * J / 32 rounded down, with J = 2^110 / 92,675,904 rounded up, times 64 / 41.02, rounded up, which is the constant RUN_PAIRS of the submitted program, 21,853,299,106,075,760,480,725,513 (proof.md Section 6.4, step 4); a run has at least J pairs
```
