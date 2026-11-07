# Fixed-IV relaxed schedules are not ordinary semi-free-start collisions

Original filename: `SHA256_SCHEDULE_COMPLIANCE_RESEARCH_2026-10-21.md`.
Original SHA-256: `f7aee28b2a3b04fdc61a4c5212e86d9806c1e11ea993667637b4e22e8fed7fb8`.
Historical inspection 2026-10-21; full archival review 2026-10-29. External claims and files have not been newly verified or executed here.

The historical note describes a report by Robert Viragh / State of Utopia and its released SAT-tail script. As recorded, the script fixes both computations to the standard SHA-256 IV, models all 64 compression steps and feed-forward, leaves W[57] through W[61] unconstrained by the message expansion, and enforces W[62] and W[63] after that gap. It describes 43 of the 48 expansion equations as enforced, using the label sr=59. The record itself reports that full schedule compliance remains open.

Editorial correction: the original note conflates this with semi-free-start (SFS). These are distinct relaxations. An ordinary semi-free-start collision permits a chosen common starting chaining value while keeping the target's schedule. The object described here instead retains the standard IV but relaxes five schedule equations. It must be called a **fixed-IV, relaxed-message-schedule collision claim**, not an ordinary SFS collision and not an ordinary full SHA-256 collision. The external report's title is not a substitute for the actual equations.

Why it matters: arbitrary expanded words need not come from any pair of 16-word message blocks. A full-round output equality in the relaxed model proves no standard-message collision unless all omitted recurrence equations are restored and the resulting complete messages independently checked. The archival note reports no independent reproduction or peer-review validation.

Historical references, not copies:

- https://stateofutopia.com/papers/2/we-broke-92-percent-of-sha-256.html
- https://stateofutopia.com/papers/2/sat_tail_sr59.py.txt
- https://stateofutopia.com/papers/2/we-broke-92-percent-of-sha-256.pdf
- https://github.com/Kristian5013/sha256-cas/blob/main/REPORT.md
- https://raw.githubusercontent.com/Layr-Labs/hash-smash/main/TASK.md
- https://raw.githubusercontent.com/Layr-Labs/hash-smash/main/docs/JUDGE_LANES.md

The PDF is referenced only; no payload is staged.
