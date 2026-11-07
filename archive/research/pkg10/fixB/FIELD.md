Replacement for the bullet "preprocessing_log2" under "Field meanings" in
Section 10 of proof.md (old lines 2292 to 2295):

- preprocessing_log2 = 80 bounds the selection procedure SEL of Section 9 by
  2^80 target-compression units (fewer than 2^88.45 primitive operations).
  Every search of SEL runs over a stated range and every program run in it
  halts at a stated cap, so this is a bound by construction; that SEL returns
  the stored constants rests on the participant's records (Sections 8, 9).
