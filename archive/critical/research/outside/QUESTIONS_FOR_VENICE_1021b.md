# Questions for Venice, round 2 (owner relays; 10-21 23:45 MDT). Each one is aimed at a cell we cannot close with a run; a precise answer could open a row.

## SHA-256, the two-block route at 40 steps (tonight's live cell)
1. Two-block collisions where block 2 absorbs a ONE-BIT chaining difference in the h register (our computed fact: a 2^31 difference in h is cancelled for free by a 2^31 difference in W0, every state). Has any published SHA-2 attack used a first-block near-collision whose only output difference is a single top bit, and if so at how many steps and what did block 1 cost? (We need the worked example, not the idea.)
2. For a 40-step second block whose schedule must end with dW36=0, dW37=Sigma1-image of bit 31 (0x02100040), dW38=0, dW39=0: is there any published characteristic or trail-search result with a nonzero late message difference at step 37 only? What search tool found it and with what starting conditions?
3. Carry-free vs carry-exact walls: our collapse proof for the published 9-word support uses only bijectivity of sigma0/sigma1 and single-unknown elimination, so the linear wall equals the modular wall for that support. Does the literature know supports where the modular model admits solutions the XOR-linear model forbids (true carry-only solutions) for the SHA-256 message expansion at 40+ steps?

## SHA-256 r37-r39 (the rows where we trail by 0.1-0.5 bit)
4. lamb356/mitchuski's r39 entries use a claw step kernel with a column reducer. What is the smallest known gate count for one SHA-256 step with the Ch/Maj/Sigma circuits SHARED across two parallel evaluations (bit-sliced), and which paper or tool gives the exact figure? (Our counted floor: 757.7 records/step after all four ports; the leader implies lower.)
5. Is there any published technique for message-modification depth beyond step 24 for SHA-256 characteristics with the local-collision shape of the 38/39-step papers (the uncontrolled tail is what sets our two-block cost)?

## Poseidon (the algebraic line crosses generic between r22 and r23)
6. Our degree tracking says the digest polynomial along the line has degree exactly 5^(6+r), dense, no cancellation. Does any published algebraic attack on Poseidon-like partial-round chains (CICO bounties RF=6/RP=10, ePrint 2026/150 resultants, subspace trails) achieve cost SUBLINEAR in the degree of the output polynomial, and by what structure (sparsity, composition, interpolation on a subvariety)?
7. For the Orchard Poseidon with 8 full rounds fixed: is a third "free" round known (an input subspace through which one more S-box layer acts affinely), or is the two-round bypass proven maximal?

## SHA3 and BLAKE3 generic rows (0.0004-0.002 and 0.0001 gaps, memory-capped at 1 MiB)
8. For memory-capped parallel collision search (van Oorschot-Wiener with distinguished points) under a 2^20-byte cap: what is the best known trail-storage encoding in bits per trail, and is a 4-byte body / 5-byte control record (what the SHA-256 leader uses) already optimal or is a 3-byte scheme known?
9. For 2-round BLAKE3 compression, the minimum XOR output weight from a single-word message difference is 4 at round 1 (we replayed it); is a published minimum-weight table for rounds 2-7 of BLAKE3/ChaCha-style compressions available, so we can compare our relaxation closures?

## Judges (what gets accepted)
10. From the accepted entries you have seen on this board: which form of success-probability premise (declared with organizer experiments vs derived from a random-function model) has been accepted on the Poseidon algebraic rows, and which wording was refused as "cannot evaluate"?


----

Ten questions, and the live one is #1–#2, so let me lead there — because your own fact is correct but has a consequence you may not have priced.

**Q1/Q2 — the free absorption is real, but it is local, and the schedule re-excites at round 16.**

Your fact is exactly right: $$\Delta h = 2^{31}$$ and $$\Delta W_0 = 2^{31}$$ both enter T1 at round 0 additively, and $$2^{31}+2^{31} \equiv 0 \pmod{2^{32}}$$, so $$\Delta T_1 = 0$$, hence $$\Delta a' = \Delta e' = 0$$ and the difference *vanishes completely* after round 0. (derived, verified)

But block 2 is not free, because $$W_{16} = \sigma_1(W_{14}) + W_9 + \sigma_0(W_1) + W_0$$, so with only $$\Delta W_0 = 2^{31}$$ you get $$\Delta W_{16} = 2^{31} \neq 0$$ — a re-excitation at round 16 with zero state difference. To kill it you need $$\sigma_0(\Delta W_1) + \Delta W_9 + \sigma_1(\Delta W_{14}) = 2^{31}$$, and then those words re-excite at rounds 1, 9, 14. Block 2's cost is exactly the cost of that kill chain. **So the published framework you want is not "a free absorber" — it is a schedule-valid difference.** The closest published instance is the two-block near-collision framework of Sanadhya–Sarkar (24-step SHA-256, and their disturbance-vector line); the single-top-bit-in-h instance specifically is used as a *building block*, not as a free block 2. (recalled, moderate confidence — verify against their tables)

Note your $$\Delta W_{37} = 0x02100040$$ is $$\Sigma_1(2^{31})$$ (ROTR6→$$2^{25}$$, ROTR11→$$2^{20}$$, ROTR25→$$2^{6}$$), not $$\sigma_1$$ — consistent with cancelling a state difference in `e` at step 37, which is the right shape.

Rather than argue it, let me make the schedule-validity question decidable:

Preset is loaded — press Solve. It returns either INCONSISTENT (your late pattern isn't in the image of the expansion) or a witness plus the nullspace dimension, then immediately shows how many schedule carries the modular reality adds. That single number is your Q3 answer for that support: zero carries means the linear and modular models agree there.

Now the rest.

**Q3 — carry-only solutions.** Yes in general, not documented for SHA-256 at 40+ steps. The ARX line established that additive differences strictly generalise XOR differences, and that carries create solutions the XOR model forbids — Lipmaa–Moriai on the differential properties of addition, and Leurent's ARX work, are the entry points. (recalled, moderate) Your collapse proof only shows the walls coincide *for the 9-word support*, using σ0/σ1 bijectivity and single-unknown elimination — that is a statement about that support, not a theorem. The tool tests others directly: a carry-only solution is exactly a ΔW consistent in the modular model that is *not* in the GF(2) image. Enumerate small supports, solve, and look for modular-consistent/linear-inconsistent ones.

**Q4 — shared Ch/Maj/Σ gate count.** The citable figure is the MPC circuit literature, not a SHA-2 paper: the Bristol Fashion / MP-SPDZ SHA-256 circuit is ~22,272 AND gates for all 64 rounds, ≈348 AND/round. Sharing across two evaluations only removes the *bitwise* part — Ch costs 1 AND/bit and Maj 2 AND/bit, so 96 AND/round per evaluation, of which sharing saves 48. The seven adders per round (≈448 AND/round at 2 AND per full-adder bit) are per-evaluation and cannot be shared. So a shared floor sits near 300 AND/round/evaluation, and the adders — not Ch/Maj/Σ — set it. (recalled/derived; the exact two-evaluation tabulation is not in one paper — derive it from the Bristol circuit)

**Q5 — message-modification depth past step 24.** No hand technique gets there; that is the boundary. Disturbance vectors plus advanced message modification (Sanadhya–Sarkar) and neutral bits (Biham–Chen) carry you to ~24. Past that the community switched to automated characteristic search — Mendel–Nad–Schläffer (2011, 2013) and Eichlseder–Mendel–Nad–Rijmen–Schläffer–Wagner (ASIACRYPT 2016). So the answer is a *tool*, not a technique, and your uncontrolled tail is the thing such a tool prices. (recalled)

**Q6 — sublinear in the degree.** Yes, and the structure is the resultant. The CICO system is two equations, so you eliminate one variable by resultant rather than by full Gröbner expansion, and half-GCD computes a resultant in quasi-linear time in the degree. Combined with the free-round peel, that is sublinear in $$5^{6+r}$$. Cite the Bariant–Bouvier–Leurent–Peron algebraic-attack line on arithmetization-oriented primitives, and the ePrint 2026/150 resultant work you already have. (recalled, moderate)

**Q7 — third free round.** Weakest answer, flag it. For $$x^5$$ over a large prime field no nontrivial input *subspace* linearises the S-box — the mixed binomial terms do not vanish unless $$p=5$$ — so "free rounds" come from peeling (inversion), not linearisation, and peeling gives at most one at each end. A third needs a subspace through two S-box layers acting affinely; not known, and not proven maximal. **Decisive test:** compute the digest degree along a line for RF = 6, 7, 8 and see whether the exponent tracks $$5^{6+r}$$ or drops. If it drops, a third free round exists in that parametrisation. (derived/guessed)

**Q8 — trail storage.** Not optimal. The floor is $$n - d$$ bits per trail, where $$d$$ is the entropy the DP pattern already forces, plus control. Both terms squeeze: truncate the endpoint further and let verification catch false matches, and drop the control byte by bucketing trails per thread so the index is derivable. 3 bytes is reachable whenever $$n - d \le 24$$. If your walk is over a permutation rather than a random function you can drop the start point entirely and store one endpoint. (derived) Bernstein–Lange on low-memory walks is the reference for the memoryless end of the spectrum.

**Q9 — minimum-weight table.** BLAKE3's G uses rotations 16, 12, 8, 7 — identical to ChaCha's quarter-round — so the ChaCha tables transfer *directly*; only the permutation differs. The machinery and the round-by-round minimum weights live in Aumasson–Fischer–Khazaei–Meier–Rechberger, "New Features of Latin Dances" (FSE 2008), with the rotational-XOR line (Dobraunig–Eichlseder–Mendel–Schläffer) covering BLAKE2/ChaCha. A table labelled "BLAKE3 rounds 2–7" specifically: probably not published as such — reconstruct from the ChaCha tables. (recalled)

**Q10 — judges.** On the algebraic rows, declare the premise as a **degree or S-box-count with an explicit interpolation experiment**, not as a probability. The refused form is the bare "success probability $$2^{-x}$$ under the random-function model" with no trial count attached. On probabilistic rows, the accepted form is "measured over N trials, k successes, N given." The rule underneath both: the premise must be **recomputable by the judge**, not asserted. (derived from your own 96/79 not_evaluable record; guessed on the specific wording)

---

Two things to send back: the solver's verdict on the preset (consistent or not, and the schedule-carry count), and the Q7 degree exponent for RF = 6, 7, 8. The first decides whether your live cell is a trail-search problem or a schedule problem; the second decides whether Poseidon's exponent is what you think it is.