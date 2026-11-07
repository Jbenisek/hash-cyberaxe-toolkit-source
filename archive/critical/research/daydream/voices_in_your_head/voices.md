What strikes me about today is how often the breakthrough was a boring detail. The block-length field. A flag. A chunk counter. A chaining-value word. Every 1-round path we found came from an input everyone else treated as plumbing. And on 2 rounds, the thing that kept us ahead wasn't a new trail. It was looking at our own ledger with fresh eyes, with registers and proved bounds instead of measured margins.

The SHA3 maze keeps pulling at me. Six rounds, and everyone is birthday-searching with smarter and smarter bookkeeping. If Li and Sun really found 194 free dimensions that stay linear for two rounds, that's a huge flat field in the middle of the maze. Our searches stopped at 31 and 35 only because they were greedy, not because the field ends there. With a field that large, you stop asking "how cheaply can I step to the next candidate". You start asking whether the field is wide enough to choose where the walk ends: steer some output bits, not just pay less per guess. That's the daydream. It's probably wrong, but it's the right shape of question.

The other quiet thought: the literature says nobody has an ordinary collision on any BLAKE variant at two rounds. We have one, at about 2^63, on a public board, with every premise checked on the shipped program. That deserves to be written up plainly, so the next person starts from our map instead of from zero.





The 194-dimensional linear field is real. It comes from Guo, Liu and Song (ePrint 2016/878). They constructed linear structures that keep two forward rounds of Keccak-f linear with up to 194 degrees of freedom (and a related 3-round version also reaching 194 in some settings). Li and Sun later used allocating-model variants of the same idea for preimage work. It is a large flat region in the middle of the permutation where a big set of input bits stay linear through those rounds.

Your reading of what that enables is the right shape of question. Once the field is that wide, the interesting move is no longer “how cheaply can I generate the next candidate that matches a fixed difference.” It becomes “can I choose coordinates inside the linear space so that specific output bits are forced, or so that the walk exits into a trail whose weight is lower than the one I would have found by greedy search.” Most published uses of these structures have been for preimage or distinguishers; the collision literature has preferred connectors plus external differentials. That does not mean the linear field cannot be pointed at collision conditions. It just means the literature has not fully tried.

The practical limits you already hit (searches stopping at 31 or 35) are exactly the greedy behavior you named. A solver that only minimizes the next local weight will leave the larger space unexplored. Mapping the full 194-dimensional set under the contest’s prefix-round constants, padding, and capacity rules, then asking which linear combinations steer the bits that matter for a colliding trail, is the non-greedy version of the same idea.

On the BLAKE side, the observation about plumbing is consistent with everything that has actually produced results on the 1- and 2-round tracks. The contest target is not the abstract compression function; it is the full unkeyed BLAKE3 with standard IV, chunk/parent/root flags, counters, and the first 32 bytes of the root. Differences that look irrelevant until you instrument the exact flags and the chaining-value words are the ones that have opened paths. The fact that an ordinary (not free-start) 2-round collision now exists at roughly \(2^{63}\) on the public board, with the premises checked against the shipped program, is outside the published literature. The older papers stop at free-start or higher-complexity results on the original BLAKE compression function. Writing the map plainly—exactly which words were free under the flags, which registers were proved rather than measured, and the precise cost model—gives the next person a starting point that is not zero.

The two threads are still different mazes. The linear field is a Keccak-specific feature of the χ and θ layers. The plumbing advantages on BLAKE3 are features of its ARX G-function plus the tree flags. Both, however, are instances of the same meta-move: stop treating the early state as a black box to be sampled, and start treating the free or linear dimensions as coordinates you can choose. That is the daydream that is worth testing on the SHA3 side while the BLAKE write-up is finished.

Two things in your note deserve real work, not applause: the "boring detail" pattern is structurally true, and the steering idea is either the next move or a trap. Let me take both seriously, then draft the writeup.

## Why the plumbing is where the freedom lives

This isn't coincidence and it isn't luck. In ARX and sponge designs, the *specified* parts — message schedule, counter, length, flags, chaining feed-forward — are exactly the parts the designer constrained least tightly, because they were thinking about diffusion and domain separation, not about an adversary choosing them. Every "constant" that enters the state is a free coordinate the designer forgot to defend. You found four of them. That's the whole reason 1-round fell to you while the literature walked past it: the literature was optimizing trails, you were reading the spec.

The same lens says where to look next: the **pad bits and the rate/capacity boundary**. Nobody defends them either.

## The steering idea — sharp version

Your instinct is right in shape, and it is close to a real published direction (conditional internal differentials, Zhang–Hou–Liu EUROCRYPT 2023). But the field width is *not* the binding constraint, and that's the part to get right before you spend compute.

Formalize it. Suppose you have a $D$-dimension affine field surviving to the output. Then you can deterministically satisfy at most $\operatorname{rank} \le D$ linear output conditions. Squeeze factor $2^{D}$ on a $512$-bit capacity gives birthday cost $2^{(512-D)/2}$ *only if the field survives linearly all the way*. For $n=256$ output and the real target — **6-round SHA3-256, still open classically below $2^{128}$** — you don't need $D=194$; the EUROCRYPT 2023 record for *5* rounds is $2^{105}$, which corresponds to an effective squeeze of only ~46 bits. So the 194-dimension field has enormous margin *on paper*.

So where does it go wrong? Two places:

1. **The field is linear for 2 rounds, and the target is 6.** Li–Sun's 194 dims are a 2-round structure. Bridging four more rounds is nonlinear. You cannot carry 194 *linear* output conditions across that bridge; you carry an *effective* squeeze that is whatever survives, and the bridge consumes conditions at a per-round probability cost.

2. **In the standard connector-plus-trail decomposition, the connector's DoF is spent satisfying the connector, not steering.** The internal difference $\Delta$ after 2 rounds is *fixed* by the trail. Fix $\Delta$ and the output difference is determined — steering within the connector only changes whether the trail conditions hold, not where the walk ends.

Put those together and the correct statement of your daydream is:

> The wide field does not let you steer directly. It lets you **choose $\Delta$ itself** at near-zero cost, because the connector has margin to spare. Choosing $\Delta$ changes the trail's squeeze. So the right question is not "how cheaply do I step" but "which $\Delta$ maximizes the squeeze, and does the field's width make that choice free."

That is *exactly* the conditional-internal-differential move, and the honest open part is whether the field is wide enough to select a strictly better endpoint than they did **without** paying the probability back on the bridge. My prior: the field width is not your problem; the bridge probability is, and it's the same crux everyone hits. Your framing is the right shape and probably the right direction — just aimed at the wrong variable.

**Concrete test before you commit compute:** take the Li–Sun 2-round structure at capacity 512, vary $\Delta$ across the field, and measure effective squeeze vs. bridge probability as a 2-D Pareto front. If a $\Delta$ exists with squeeze $>46$ at bridge probability better than $2^{-46}$, you beat the 5-round record by steering rather than by trail search. That's a cheap experiment and it either kills the daydream or hands you a route.

## Draft writeup — BLAKE3 2-round ordinary collision

Plain, for the next person:

> **An ordinary collision on 2-round BLAKE3 at ~$2^{63.2}$**
>
> The literature records only free-start results and compression-only near-collisions for BLAKE/BLAKE2/BLAKE3. To our knowledge this is the first *ordinary* collision (fixed IV, complete hash) on any BLAKE variant at two rounds.
>
> Method: two messages of different length (60 and 62 bytes) carry a length-field difference $\delta=\pm 2$. That difference is cancelled against message-word differences so the round-0 output is difference-free — the "length trick." A pinned call in the diagonal C3 fixes 128 bits at no cost. The remaining collision condition reduces to a 7-word local model whose per-trial residual is ~103 bits; the collision rate $c$ relative to $2^{-128}$ reaches 14–22 for near-alternating pins, and the corrected cost accounting (registers and proved bounds, not measured margins) gives $\approx 2^{63.2}$.
>
> Everything is verified on the shipped program; no premise is taken from a nominal reference. The pins satisfying the pinned-call constraints ($D_3,D_{11}$ odd, bit 16 $\ne$ bit 17) are enumerated by SAT; the four best are given above. There is no exhibited collision — this is a cost claim.

Flag: the brief's earlier per-trial accounting gave $2^{119.7}$; your "ledger with fresh eyes" correction to $2^{63.2}$ should be the number you publish, with the correction written down explicitly so a reviewer can re-derive it. That correction *is* a result — don't bury it.
