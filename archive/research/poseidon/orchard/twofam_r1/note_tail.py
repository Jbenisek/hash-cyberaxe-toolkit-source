# executed at the end of build_package.py: writes submission-note.md (plain language, at least 5 KiB)
note = """Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): two families of inputs, a success probability that is a theorem, exact finite ledger, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and one partial round) whose chance of success per run is proved by a counting argument and a character-sum bound, not measured.
An earlier entry of ours relied on a sampled success rate; this one does not use any sample for its probability.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree:
   its S-box output is affine in one parameter W. The digest is then a univariate polynomial f(W) of degree 5^7 = 78125. We use two such lines (two choices of the constant coordinate). Each line contains exactly p inputs (one for each W in F_p), and the two lines meet in exactly one input.
   So the union has 2p - 1 inputs.
2. Counting. The digest takes at most p values. At most p - 1 of the 2p - 1 inputs can be the only input with their digest (if p of them were isolated they would use up every value and nothing else could exist). So an input drawn uniformly from the union shares its digest with another input of the union with probability at least p/(2p - 1), which is above one half.
   This holds whatever the polynomials look like.
3. The program draws a uniform input x of the union (a rejection sampler on 256-bit words, at most 128 words; the common input is counted once), computes y = digest(x), builds f_0 - y and f_1 - y by evaluating the digest at 98,304 points of each line and one inverse transform,
   computes W^p mod (f - y) with a low-memory transform schedule, and takes the gcd with W^p - W (classical Euclid). The result is the product of the linear factors for all roots in the field: all inputs of that line with digest y.
   The roots that are x itself are divided out; if something is left, one root is isolated and mapped back to a second input with the same digest.
4. Root isolation is a Cantor-Zassenhaus procedure with a bounded number of tries per level. Its failure probability is bounded with a Weil bound for quadratic-character sums (proof.md, Lemma B): a level of degree d fails with probability at most (2^(1-d) + 2^-100)^t, and with t = ceil(40/(d-1)) tries (one try above degree 40) every level fails with probability below 2^-39.99. At most 15 levels occur, because each level halves the degree. The total is below 2^-36.
5. Success probability: at least p/(2p-1) times (1 - 2^-36) minus 2^-127 for the sampler, which exceeds 0.4999999999. The claim is 0.4999999999. It uses independent uniform random words as the model primitive (as the cost model has), and nothing else.

Numbers. time_log2 %(TIME)s (the worst case of one attempt: both lines run to the end, family 1 isolates a root at the worst degrees), memory %(MEM_BYTES)s bytes (log2 %(MEM_LOG2)s), normalized cost %(SCORE)s, success probability 0.4999999999.
Total charge of the worst case %(WORST)s primitive operations = %(UNITS)s target-compression units (237 primitive operations per unit). A run that finds its root in the first family charges about %(TYPFIRST)s operations; a run through both families without a partner, about %(TYPICAL)s.
%(NCERT)d verified collisions found by this program are included as certificates, each from a separate attempt.

Where the charge comes from (primitive operations, rules in proof.md section 6):
%(TABLE)s

Why the worst case is large. The probability claim has to hold for every value of the digest, including a value that has very many preimages on a line. Then the product of roots has a large degree, and isolating a root costs a number of modular powerings of that degree.
We charge that case, level by level, at derived bounds although it was never observed; the observed runs isolate a root of degree 1 or 2 at a cost of at most about 16,000 operations. The classical gcd is charged at its derived worst case (a normal remainder sequence, about the square of the degree),
which is also what it costs in practice for this input, so that bound is within 1 percent of the observed charge.

What was run and what was derived.
* Run end to end: the main attempt (sampler, two lines, evaluation and interpolation, powering, gcd, deflation, root isolation, back-map, two reference hashes); the certificates are its outputs.
* Run at the sizes of the worst case: the Taylor shift and the powering with exponent (p-1)/2 at every degree of the level schedule (78125, 39062, ... 4), by a calibration program; their charge does not depend on the coefficients.
* Run on synthetic inputs: the whole root-isolation stage on products of random linear factors of degree up to 3000, with the program asserting its own gcd and division charges against the derived bounds.
* Derived: the bounds for the gcd and the division (closed forms in proof.md sections 7 and 11), the count of levels and tries, the failure probabilities.
* Assumed: the charging rules of proof.md section 6 describe the program; the cost of a level is at most 1.02 times the cost measured at the largest degree of that level.

Memory. The largest live set is the powering at degree 78125: the transform buffer (3 x 2^16 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table; tracked peak %(HEAP)s bytes, plus the static image (%(STATIC)s bytes), a stack bound of 65,536 bytes and 4,096 bytes of allocator metadata.

Reasoning narrative.
Context. The previous filing of this family computed the roots of an odd-part polynomial for a random centre on one line and rested its probability on a measured success rate; that is not a bound.
Approach. Replace the random centre by a uniform point of a set larger than the digest range, so that the existence of a partner is a counting fact. That needs a set of 2p - 1 inputs on which the digest is cheap to evaluate as a polynomial in one variable: two lines do.
Trade-offs. The polynomial now has degree 78125 instead of 39062 (no odd-part halving), so the powering is about 2.4 times larger and there are two of them; in exchange the success probability is a theorem. Classical Euclid replaces the half-gcd because its worst case is a closed form.
Implementation. Reused: the finite-field code, the transform engine and the low-memory powering of the earlier entry; new: the two-line setup and their common input, the sampler, the classical gcd with its derived charge, the deflation, the Taylor shift, the root isolation and its tests.
Results. The attempts that were run found collisions; the stage charges agree with the derived bounds (the program asserts this).
Caveats. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption is a sixteen-word register file per transform block; the worst-case root isolation is charged at a derived bound and not observed.
Next steps. The half-gcd with a derived worst case would cut the gcd charge; a sharper handling of values with very many preimages would cut the root-isolation bound, which is the largest term.
"""
tbl = '\n'.join(ledger_rows)
note = note % dict(TIME='%.3f' % time_claim, MEM_BYTES=L(mem_bytes), MEM_LOG2='%.3f' % mem_log2, SCORE='%.3f' % score, WORST=L(worst), UNITS='{:,.1f}'.format(worst / C),
                   TYPICAL=L(typ) if typ else 'n/a', TYPFIRST=L(typ_first) if typ_first else 'n/a', NCERT=N_CERT, TABLE=tbl, HEAP=L(HEAP), STATIC=L(static))
note += "\nWorst case sum: " + WORST_FORMULA + " = " + L(worst) + " operations.\n"
note += "\nRoot isolation (stage F) worst case by level:\n\n" + '\n'.join(tab) + "\n"
assert len(note.encode()) >= 5 * 1024, len(note.encode())
assert all(ord(ch) < 128 for ch in note)
open(os.path.join(HERE, 'submission-note.md'), 'w', newline='\n').write(note)
print('note bytes', len(note.encode()))
