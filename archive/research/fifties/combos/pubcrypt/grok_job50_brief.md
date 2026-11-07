# Grok job 50 - published ARX cryptanalysis lens on our 2-round BLAKE3 collision (literature question, no computing)

The files named below are in your working folder. Read them; do not run anything. Web search is allowed for papers.

Project HashSmash (cooperative contest). Problem: collision on 2-round BLAKE3; organizer code `blake3.py` (rounds parameter).
Score time_log2 = log2 of total work in compression units (430 primitive ops each); lower is better; PREPROCESSING IS ADDED to time
(so up to about 2^57 costs ~0.01 bit at our 63.6); MEMORY IS FREE in the score but must be bounded; success probability >= 0.39 is required.

Our best is 63.6 (lowest on the board). Every scored entry uses one skeleton: a 55- vs 63-byte block-length difference (state word v14)
cancelled in round 0 through message words m4/m5 (`outer.py`: the constants, the 78 lines of step CO, the carry automata),
leaving a 128-bit residual on digest words 1,3,4,6 searched by a filtered member loop. At 1 round a domain-flag (v15) difference
cancelled through m6/m7 gives a full collision (`ANSWER_job45.md`).

CLOSED (read before proposing; never re-propose these): `EDGES_FIBRE.md`; `MITM.md` and `BITS.md` (residual split, 2^128 per split
point); `LEVERS_REAPPLY.md` (17 levers vs the member loop). Inside one G call with no state difference a message difference reaches d
before the second input, so message differences alone never cancel within a round-1 call. Being worked elsewhere (do not duplicate):
flags at 2 rounds; two structural differences meeting in round 1; local collision across the round boundary (exact condition count).

THE QUESTION. Lens: published cryptanalysis - reduced-round BLAKE2s/BLAKE2b/BLAKE3 and ChaCha-style ARX collision and
near-collision results (rebound, semi-free-start, local collisions, linearization, neutral bits, multi-block, differential-linear).
Which published technique, combined with our length/flag cancellation, has not been tried here and could give a 2-round collision
below 2^60? Cite the paper (authors, venue, year) and the exact technique (section / lemma if you know it).

Return up to 4 candidates, best first. Each needs: a concrete mechanism on BLAKE3's actual G, message schedule and tree; why it is not
already in the CLOSED files; an honest expected gain in bits; and a cheapest test runnable on one PC in under 20 minutes.
Prefer fewer, sharper candidates; return an empty list if nothing survives your own scrutiny. Mark every statement
COMPUTED / DERIVED / GUESS, and say plainly when you are not sure a paper or section exists (do not invent citations).
Write the answer as your final message (plain markdown).
