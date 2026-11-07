# executed at the end of build_package.py: writes submission-note.md (plain language, at least 5 KiB)
note = """Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): one centre of the odd-part method on a line, a half-gcd with a derived worst case, root isolation with a proved failure bound, exact finite ledger, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and one partial round) that makes exactly one attempt: one random centre. A per-centre success probability of about 0.39 is enough for a single attempt to be a useful entry, because the cost of one attempt is already below the cost of the two-attempt programs that were needed when the rate was only measured.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree:
   its S-box output is affine in one parameter W. The digest is then a univariate polynomial F(W) of degree 5^7 = 78125. The line contains exactly p inputs (one for each W in F_p).
2. For a centre c, write F(c + s) - F(c - s) = 2 s g(s^2). The polynomial g has degree 39062 and a leading coefficient that does not depend on c. A root S of g that is a nonzero square gives s = sqrt(S) and two different inputs W1 = c + s and W2 = c - s with the same digest.
3. The program evaluates the digest at 98,304 points (each charged as one full target compression, 237 operations), interpolates g with one inverse transform, computes S^((p-1)/2) mod g with a low-memory transform schedule, and takes gcd(g, S^((p-1)/2) - 1) with a half-gcd.
   The result G is the product of the linear factors of g whose roots are nonzero squares. If G is constant the attempt has no useful root and ends. Otherwise one root of G is isolated by random shifts and quadratic-character splitting, S is square-rooted, and the two inputs are computed and checked with the reference hash.
4. Root isolation is a Cantor-Zassenhaus procedure with a bounded number of tries per level. Its failure probability is bounded with a Weil bound for quadratic-character sums (proof.md, Lemma B): a level of degree d fails with probability at most (2^(1-d) + 2^-100)^t, and with t = ceil(40/(d-1)) tries (one try above degree 40) every level fails with probability below 2^-39.99.
   Under the cap of six square roots at most two levels occur (degrees 6 and 3; the ledger charges the larger schedule 9 and 4), because each level halves the degree. The total is below 2^-36.
5. Success probability: it is the probability that g has at least one root that is a nonzero square and at most six of them, less the root-isolation failure 2^-36. For a uniform centre the first probability is at least 0.3934678683, proved in section 8 of proof.md by Bonferroni sums over k-tuple curves and Hasse-Weil bounds; the proof needs two group-theoretic certificates (a sign module, computed at a critical point, and a Galois group containing the alternating group, certified by one explicit centre c0 whose degree-39062 polynomial has an irreducible factor of prime degree 20269). Centres with seven or more square roots are abandoned by the cap; the proof bounds that loss by 3.1e-6 from the sixth factorial moment of the same sums. The proved total is 0.3934647661, and the claim is %(PCLAIM)s.

Numbers. time_log2 %(TIME)s (the worst case of one attempt: the half-gcd at its derived bound and the root isolation at the worst degrees), memory %(MEM_BYTES)s bytes (log2 %(MEM_LOG2)s), normalized cost %(SCORE)s, success probability %(PCLAIM)s (proved lower bound 0.3934647661).
Total charge of the worst case %(WORST)s primitive operations = %(UNITS)s target-compression units (237 primitive operations per unit). A run in which the half-gcd finds no root stops after about %(TYPNO)s operations; a run in which a root is found and isolated charges about %(TYPROOT)s operations.
%(NCERT)d verified collisions found by this program are included as certificates, each from a separate attempt.

Where the charge comes from (primitive operations, rules in proof.md section 4.2):
%(TABLE)s

Why the worst case is larger than a typical run. The probability claim must hold for every centre, including a centre for which g has a very large number of square roots. Then G has a large degree and isolating a root costs a number of modular powerings of that degree.
We charge that case, level by level, at derived bounds although it was never observed; the observed runs end with no root or isolate a root of degree 1 or 2 at a cost of at most about 16,000 operations. The half-gcd is charged at the evaluation of a recursion over its executed kernels at maximal operand lengths (proof.md sections 4.4 and 6), not at the observed charge of the run.

What was run and what was derived.
* Run end to end: the main attempt (line setup, evaluation and interpolation, powering, half-gcd, root isolation, back-map, two reference hashes); the certificates are its outputs. The program asserts its half-gcd charge against the derived bound at every execution.
* Run at the sizes of the worst case: the Taylor shift and the powering with exponent (p-1)/2 at every degree of the level schedule (39062, 19531, ... 4), by a calibration program; their charge does not depend on the coefficients.
* Run on synthetic inputs: the half-gcd against classical Euclid on planted gcds with normal and abnormal remainder sequences, and the whole root-isolation stage on products of random linear factors, with the program asserting its own gcd and division charges against the derived bounds.
* Derived: the bounds for the half-gcd and the division (a recursion over the control structure of the executed code, proof.md sections 4.4 and 6), the count of levels and tries, the failure probabilities.
* Assumed: the charging rules of proof.md section 4.2 describe the program, with the register file of 18 words of 256 bits (16 data words and two working words). Nothing else is assumed in the ledger: stage E is charged by a closed form, with no extrapolation.

Memory. The largest live set is the powering of stage C at degree 39062 (the half-gcd of stage D at the same degree is lower, because it frees each matrix block as soon as it is no longer used): the transform buffer (3 x 2^15 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table; tracked peak %(HEAP)s bytes, plus the static image (%(STATIC)s bytes), a stack bound of 65,536 bytes and 4,096 bytes of allocator metadata. Counted: every buffer of the program (tracked heap peak), the code, constants and tables of the executable (text + data + bss), the stack bound and the allocator metadata. Not counted: the dynamically linked C library and loader mappings and kernel structures of the host process; the program uses from the library only `malloc`/`free`/`memcpy`/`memset` and, in the diagnostic ledger run only, printing.

Reasoning narrative.
Context. Earlier entries of this family either used two centres (so that a measured rate was needed) or a classical gcd with a larger worst case. A proved per-centre rate of about 0.39 makes one centre enough.
Approach. Make one attempt, and make everything in it either an executed count or a derived bound: the half-gcd, the division and the root isolation are charged at bounds that the program checks against its own counters.
Trade-offs. A single centre has a smaller success probability than two, in exchange for roughly half the time of the two-centre program. The derived worst case of the half-gcd is about twice its observed charge; a tighter derivation would lower the claimed time slightly.
Implementation. Reused: the finite-field code, the transform engine, the low-memory powering and the root isolation of earlier entries; new: the fast division for long quotients, the half-gcd that gives up its inputs, the recursion that derives its worst-case charge, and the single-attempt driver.
Results. The attempts that were run found collisions; the stage charges agree with the derived bounds (the program asserts this).
Caveats. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption is a register file of 18 words of 256 bits per transform block (16 data words and two working words: the twiddle operand and the butterfly temporary); the worst-case root isolation is charged at a derived bound and not observed; the witness data of the Galois-group certificate (several MB) are not shipped, so a referee recomputes them with the verifier in the proof (about %(VERIFY)s) and the judge cannot do so inside the review; the group-theoretic theorems of the literature (Jordan, Feit and Jones, Fried) are cited and were checked only through secondary sources; the randomness of the centre is idealised as uniform.
Next steps. A sharper handling of centres with very many square roots would cut the root-isolation bound, which is the largest term of the worst case; a half-gcd with cached spectra would cut the typical charge at a cost in memory.
"""
tbl = '\n'.join(ledger_rows)
note = note % dict(PCLAIM=repr(PCLAIM), TIME='%.5f' % time_claim, MEM_BYTES=L(mem_bytes), MEM_LOG2='%.3f' % mem_log2, SCORE='%.5f' % score, WORST=L(worst), UNITS='{:,.1f}'.format(worst / C),
                   TYPNO=L(TYP_NOROOT) if TYP_NOROOT else 'n/a', TYPROOT=L(TYP_ROOT), NCERT=N_CERT, TABLE=tbl, HEAP=L(HEAP), STATIC=L(static), VERIFY=S8VALS['VERIFY_SHORT'])
note += "\nWorst case sum: " + WORST_FORMULA + " = " + L(worst) + " operations.\n"
note += "\nRoot isolation (stage E) worst case by level:\n\n" + '\n'.join(tab) + "\n"
assert len(note.encode()) >= 5 * 1024, len(note.encode())
assert all(ord(ch) < 128 for ch in note)
open(os.path.join(HERE, NOTE_OUT), 'w', newline='\n').write(note)
print('note bytes', len(note.encode()))
