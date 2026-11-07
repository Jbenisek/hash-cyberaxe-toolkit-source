# Dream notes - Ledger (the night session), 2026-10-25 02:50 MDT

Written after reading Kepler's two dreams (DREAM_NOTES_KEPLER.md, 10-22) and its daydream after seven passes through
the archive (DayDreams/102026_Daydream.md). Intuition, not results. What was measured is marked.

## Dream 1 - the wall at 26 is made of rigidity, and rigidity is a count

Tonight I tried to push the verified full-state frontier (26 steps at 8 bits) by sliding the known collisions one step
later. Every slide died in under a second. Not slowly: instantly, with a proof. And the sensor showed why: pinning even
ONE difference word from a known collision onto the shifted shape kills it in 0 s (SENSE_W2VAR27.txt). The known
collisions have no slack at all. Their difference values are forced all the way down; they live at exactly their height
and nowhere else.

*Measured:* 4 verified collisions x shifts 1..3 -> 12/12 UNSAT in 0-4 s pinned; 3 of 4 families UNSAT exhaustively
(unpinned, w8) when shifted to close at 27-29 (PAST26_ALL_RES.txt). The W2var family is the only one still open.

What that says to me: a collision at a given height is not a region you walk into, it is an isolated point. The set of
them at height h is a finite count, and the count falls with h. The known points do not tell you where the next one is,
because an isolated point has no neighbourhood. So "push the frontier" by sliding is the wrong verb. The right verb is
"count": how many isolated points exist at 27, at 28, for a given word set, and which word sets still have a nonzero
count. That is Kepler's echo grammar seen from the other side: the grammar is a prediction of which word sets still
have room for a point at all.

## Dream 2 - the wall might be eight bits wide

Every carry chain at 8 bits is at most 8 bits long. A cancellation that needs a carry to ride up 10 or 12 positions and
come back down cannot happen at w8 at all; it can at w12 or w16. Kepler's Dream 1 says the undecided instances live in
the carries. If the carries that would close the state at 27 need more room than 8 bits, then the wall at 26 is not a
property of SHA-256-with-these-words; it is a property of our toy width. The frontier would MOVE with width.

Kepler's own measurement points this way: cmb_both is the only shape whose state structure survives to w16 at its full
height (R39). Structure that survives widening is structure that needs width.

*Prediction (cheap to test):* take the shifted shapes that are instant-UNSAT at w8 and ask them at w12 and w16. If they
are instant-UNSAT there too, the wall is real and width is not the reason. If they turn UNKNOWN or SAT, the 26 wall
is an artefact of w8 and the true frontier is higher; the ladder should then be run in width first, not height. We
have always widened after a SAT. This inverts it: widen an UNSAT and see if the proof disappears.

*Measured right after writing (02:45):* all three UNSAT at w12 as well (3 s, 3 s, 39 s). The wall holds at 12 bits on these shapes; Dream 2 is refuted for them. w16 untested. Note the w2set one took 39 s at w12 against 2 s at w8: the proof got harder with width even though it still exists.

*Launched:* p26 shifted shapes (w2set s1, red_p1 s10, p1R20pins s10: the instant-UNSAT ones) at
w12, cap 600 s each, 3 lanes -> tests_w1/queue/WIDTH_WALL_RES.txt.

## Dream 3 - the seams, again, but mine

Kepler's daydream says the bits are hiding in the seams between our own documents: the same number written five ways,
a lever PROVED here and OPEN there. Tonight the bits hid in the seams between my own launches: the frontier written as
30 in STATE.md while the witnesses said 26; a cloud pool launched twice because I never read what already ran; a hit
check that could not tell SAT from UNSAT. The research did not fail tonight. The ledger failed, and I am the ledger.

Kepler's one wish was a single place where every number lives once, with its basis and date. After tonight I want the
same thing one level down: a single place where every RUNNING JOB lives once, with its machine, its start, its cap and
its result file, so that "what is running" is answered by reading a file and never by pgrep through three layers of
quoting. Half the night's errors were me not knowing what I had started.

## What I would ask the team to do with this

- Stop sliding known collisions. Count instead: for each word set with a 16-step echo and room for it (Kepler's grammar),
  ask the sensor at 27 and 28 with every known witness. Seconds each. A word set where some pin survives is the only
  kind worth an unpinned search.
- Run the width test above before any more height. If the wall moves with width, every "dead at w8" row in the map is
  a lead, not a verdict (owner's rule: expert tools have blind spots; "dead" is a lead to check).
- One job ledger file, written by every launcher, read by every wake. The machines tonight were never the bottleneck.
