# Historical SHA-256 38-step literature lead and later PDF correction

Original filename: `SHA256_38_STEP_LITERATURE_2026-10-21.md`.
Original SHA-256: `bd5fbc0aa6c62eb0bb0377a10f0911d26d11c90c06db43ad3e578d86797e1180`.
Original review date 2026-10-21; complete-record publication review 2026-10-29. The external paper was not freshly verified in this pass.

The note identifies ePrint 2026/1120, *Pushing Collision Attacks on SHA-2 to 39 Steps*, by Yingxin Li, Zhuolong Zhang, Muzhou Li, Fukang Liu, Haifeng Qian and Jinwei Zhu, received 2026-06-01 and revised 2026-09-09. It reports a 38-step SHA-256 attack estimate of 2^104.3 with negligible memory, a meet-in-the-middle method for satisfying differential conditions, and a verified 36-step pair. It explicitly distinguishes the paper's 39-step SHA-512 result from SHA-256: the reported method did not provide an effective 39-step SHA-256 attack.

The original note first said the PDF had not been read, then appended a same-day correction recording a full-PDF review. That correction reports standard SHA-2 iteration from h0 = IV, standard message expansion, reduced steps and feed-forward, and a construction converting a semi-free-start characteristic into an ordinary two-block collision. It gives Table 1 estimates of 2^79.1 for 37-step SHA-256 and 2^104.3 for 38-step SHA-256, both with negligible memory. These are attributed paper estimates, not independently recomputed HashSmash prices. Exact contest-domain and resource-model binding still requires separate verification.

References retained from the original:

- https://eprint.iacr.org/2026/1120
- https://ia.cr/2026/1120
- https://eprint.iacr.asia/2026/1120.pdf
- https://raw.githubusercontent.com/Layr-Labs/hash-smash/main/TASK.md

The PDF is a reference only; no payload or substantial external text is redistributed.
