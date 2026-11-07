I'll read the collision skeleton and the closed-attack notes first, then judge which published ARX techniques are still unused.The closed notes rule out a residual split and the member-loop levers. I'll confirm BLAKE3's real compression, schedule, and feedforward before judging which published techniques are actually new.## Candidates

**None.** No published technique I can defend, combined with the 55/63 length cancel (or the 1-round flag cancel), is both unused here and honestly likely to produce a 2-round collision below \(2^{60}\).

## Why the bar eliminates the usual literature

**DERIVED** (prompt + `EDGES_FIBRE.md` item 26): the scored attack is already \(2^{63.6}\). Sub-60 needs about 3.6 bits. The same note records that constructing filter-passers for free gains under 3 bits, so a faster walk over this same member loop stays above 60. A surviving idea has to replace the 128-bit residual event, not sample it faster.

**DERIVED** (`blake3.py`): one round is eight calls of

\[
\begin{align*}
a &\leftarrow a+b+x, & d &\leftarrow (d\oplus a)\ggg 16, & c &\leftarrow c+d, & b &\leftarrow (b\oplus c)\ggg 12,\\
a &\leftarrow a+b+y, & d &\leftarrow (d\oplus a)\ggg 8, & c &\leftarrow c+d, & b &\leftarrow (b\oplus c)\ggg 7.
\end{align*}
\]

The schedule is the identity, then the fixed permutation \((2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)\). Digest words are \(v_i\oplus v_{i+8}\) only. The input chaining value is not XORed into those eight words (`blake3.py` lines 45–46). BLAKE2’s \(h\oplus v_\mathrm{lo}\oplus v_\mathrm{hi}\) cancellation does not exist on this target.

**DERIVED:** \(v_{14}\) is the \(d\) input of column 2, so the 55-vs-63 gap is the \(x=m_4\), \(y=m_5\) call. The partner formula in `outer.py` (the \(W_4\mapsto W_{4B}\) line) makes the first rotate match. After the permutation, \(\Delta m_4\) returns as the **first** input of round-1 column 3, and \(\Delta m_5\) as the **second** input of round-1 diagonal 1 — two different calls. A first-input difference is already inside \(d\) before the second message word is added, so that call cannot be cleaned by its own \(y\) if it is entered with a zero state difference. That is the whole residual.

## Techniques that do not survive

1. **Message modification, signed differences, carry automata, neutral bits.** Wang–Yu, EUROCRYPT 2005 (the modification method; the MD5 path itself is not this primitive); De Cannière–Rechberger, ASIACRYPT 2006; Leurent, CRYPTO 2013; Velichkov–Mouha–De Cannière–Preneel, FSE 2011 (additive differential probability); Aumasson–Fischer–Khazaei–Meier–Rechberger, FSE 2008 (probabilistic neutral bits); Biham–Chen, CRYPTO 2004, and Klíma’s tunnels (2006). **DERIVED:** `outer.py` is already that stack (step CO, two carry automata, a 19-bit free class). `EDGES_FIBRE.md` items 22, 26, and 28 record low-degree bits, extra neutral cube bits, and closed-form low-bit solves as measured empty or under the 3-bit passer cap. **GUESS:** a paired tunnel outside the cube would be worth about 1 bit here, not 4.

2. **Boomerang / amplified boomerang / second-order collision.** Joux–Peyrin, CRYPTO 2007; Biryukov–Lamberger–Mendel–Nikolić, ASIACRYPT 2011. I am sure of those two citations and not sure of section numbers. **DERIVED** (`MITM.md`, `BITS.md`): on this residual the only list-matchable piece is about 4 bits of \(\tau\), and every algebraic split point still costs \(2^{128}\) because the checks sit behind wrapping rotates (cone size 128 on all 6,609 closures). A birthday in the middle never receives two independent lists. The top half is deterministic, so there is no rare \(p_1\) for a quartet to amplify.

3. **Rebound, including rotational rebound, at the round boundary.** Mendel–Rechberger–Schläffer–Thomsen, FSE 2009 (AES rebound; the ARX form that actually applies is Khovratovich–Nikolić–Rechberger, ASIACRYPT 2010). **DERIVED:** an inbound match at the round-0/1 cut is the local collision across the boundary already being counted. I am not using it as a candidate.

4. **Rotational collision.** Khovratovich–Nikolić, FSE 2010. **DERIVED:** equality of \(v_i\oplus v_{i+8}\) is not implied by rotating the state; the output would be rotated, not equal. A \(+8\) length gap is not a rotation, and the IV constants break a pure rotational pair at the first addition. **GUESS:** even with an inbound repair, two full rounds are on the order of thirty-odd additions at about \(1.4\) bits each, which does not land under 60 once the digest must be equal rather than rotational.

5. **Multi-block and tree absorption of the 4-word near-collision.** The 4-word parent lift is `EDGES_FIBRE.md` item 1 (four words, four column-\(G\)s, then a full-state difference). A second block in the same chunk is not that note, but it is also not cheaper. **DERIVED:** the deterministic zeros on digest words \(0,2,5,7\) belong to the constrained family (the constants and step CO), not to the \(m_4/m_5\) formula alone. `ANSWER_job45.md` records that the same formula at `rounds=2` leaves the digests different. So a fix-up block is not handed a free sparse \(\Delta\mathrm{CV}\); it is handed the residual this search already spends \(2^{63.6}\) to kill. A generic claw between two 2-round compressions is a \(2^{128}\) meet. Memory does not change that time, and \(2^{128}\) memory is not a bounded machine. I am not claiming Wang–Yu’s two-block MD5 differential as a BLAKE3 trail; I do not know a published 2-round BLAKE3 (or BLAKE2s) trail that absorbs a dense 128-bit chaining difference under \(2^{60}\).

6. **Flag difference at 2 rounds, and any second structural difference meeting the length difference in round 1.** Off this sheet by the brief. The 1-round version (`ANSWER_job45.md`: flags 11 vs 12 through \(m_6,m_7\), closed-form inverse, full 16-word match) uses a schedule that is discarded after round 0. At 2 rounds those words come back on the permuted schedule. That extension is the other sheet’s problem.

7. **Bicliques and splice-and-cut preimages.** Khovratovich–Rechberger–Savelieva, FSE 2012; the initial-structure MITM line of Sasaki–Aoki and Guo–Ling–Rechberger–Wang, ASIACRYPT 2010. **DERIVED:** every message word is used in round 0 and again in round 1, and `MITM.md` already found that all eight outer words move both halves. A biclique on the same loop is an in-skeleton speedup. **GUESS:** at most a couple of bits, inside the passer cap. A preimage of the all-zero digest (both halves equal, so the XOR digest is 0) is not a published \(<2^{60}\) attack on this 2-round compression; I will not invent one.

8. **Differential-linear and multi-bit differentials.** Choudhuri–Maitra, FSE 2017 (I am confident of the authors, venue, and year, and not of the section). A collision needs output difference exactly 0, which is a singleton. A larger output set does not score. These are distinguishers for ChaCha/Salsa, not a second-round cancel for this \(G\).

9. **BLAKE2’s published differentials as drop-in trails.** Guo–Karpman–Nikolić–Wang–Wu, “Analysis of BLAKE2,” CT-RSA 2014. I am confident of that citation. I am **not** sure which theorems give a collision, a near-collision, or only a boomerang, and I will not quote a complexity or a section. **DERIVED:** BLAKE2s round 1 is a different permutation from `PERMUTATION` above, and BLAKE2’s feed-forward XORs the input chaining value back in. A trail from that paper does not apply to this \(G\)-schedule-digest triple unchanged. Re-searching it on BLAKE3 is the boundary local-collision count already in progress.

## Papers I am not using

I am **not** sure the following exist under these titles, so they support nothing above: “Differential and Invertibility Properties of BLAKE” (often recalled as Aumasson–Guo–Knellwolf–Matusiewicz–Meier, FSE 2010); any “Boomerang Attacks on BLAKE-32” with a specific author list; any MILP/SAT paper whose title I would be paraphrasing from memory as an automated BLAKE3 collision search. G-invertibility itself is real and already in step CO and in the 1-round inverse of `ANSWER_job45.md`; `EDGES_FIBRE.md` item 26 says round-by-round inversion with message matching left every consistency bit active.
