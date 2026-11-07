## 10. Evidence

Everything in this section is evidence produced by us. None of it is an organizer execution, none enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.1 Executed full-scale outcomes at r = 3, 4, 5, and the shipped program at r = 3

| run | degree of F | m | centres tried (in order) | outcome per centre (`deg G`) | successes | operations N (executed) | time_log2 | memory (bytes) | threads, wall |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| r = 3, earlier program | 5^9 | 976,562 | 1 (fixed) | c=1: 1 | 1 | 317,054,280,703 | 30.08182 | 250,386,180 | 1 thread, 3,202.9 s |
| r = 4, earlier program | 5^10 | 4,882,812 | 1, 2 (fixed) | c=1: 0 (no usable root); c=2: 1 | 1 | 3,992,419,235,666 | 33.63159 | 1,231,371,140 | 6 threads, 13,030.2 s |
| r = 5, earlier program | 5^11 | 24,414,062 | 1 (fixed) | c=1: 1 | 1 | 9,205,778,231,873 | 34.73925 | 5,604,188,884 | 13 threads, 22,048.3 s |
| r = 3, the program of Appendix A (`RR=3`, `MAXTR=2`, coin seed 2) | 5^9 | 976,562 | 1 (one coin draw) | coin centre: 2 | 1 | @@R3C_N@@ | @@R3C_T@@ | arena 600,000,000 | 1 thread, @@R3C_WALL@@ |

The first three rows are the executed entries of the same construction with the centres 1, 2, ... in place of coin draws (their operation counts are the instrumented totals of those runs, thread charges included). The last row is the program of Appendix A compiled for `RR = 3` with the arena `ARENA=600000000` and run once; its counters are the figures of section 6.1 (stage rows: A 1,216, B 1,264,885,395, C 342,624,551,886, D 65,471,955,946, E 353,016, F 43,662, G 6,612, H 5,644, I 3,384,436, init 4,212,397, setup 4,910; `RECONCILE ok=1`; heap peak 244,745,792). Its isolation made 3 rounds at degree 2.

Counted together, these five centres gave a usable root at four. The first three runs stop at their first success, so each has exactly one success by construction; the number that informs is how many centres failed before it (0, 1, 0). No estimate and no interval of `rho` is derived from these counts, because none would be a lower bound.

The collisions found (each is a pair of distinct canonical `(nk, rho)` with equal digests at its own round count; the organizer's digest function accepted each of the first three at its round count when it was filed, and the last was checked by the reference implementation and the organizer's digest function of the verifier on our machine):

* r = 3 (centre 1):
  * nk1  = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815
  * rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7
  * nk2  = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567
  * rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8
  * digest (field element) = 0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec, as the organizer's 32 little-endian bytes `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132`
* r = 4 (centre 2):
  * nk1  = 0x25c10b7d8d36b332b4a4ddb92f1f1a3ffa40259b7b77b0ba458ad0be367ab979
  * rho1 = 0x2e568f6667ceaedd4195dbd24a55c365075306af4a5d0931b1707ba0bf7616ea
  * nk2  = 0x2acbf624301319ca0830c5fda78ae08e00d75798f24adf1320401f1a3bc4c580
  * rho2 = 0x162fa98e63ff13622228cd9e3b4d9039124a918f1f11d12718a2a782ed69fb17
  * digest (field element) = 0x3deca6a0b865e914ebcc74484b3cedb56b9f6293338881693e00cbee0c161fa1, as the organizer's 32 little-endian bytes `a11f160ceecb003e6981883393629f6bb5ed3c4b4874cceb14e965b8a0a6ec3d`
* r = 5 (centre 1):
  * nk1  = 0x35aefd661e07cec063071e6f92f2bbcfd6bbc794bc99be91c008fed0a2a5ebb5
  * rho1 = 0x3dd4caae629bb08efa85dd470f72f2fc183cf026de9cd1aa356e147f058a0090
  * nk2  = 0x242b99e697375e309d54e5db54c215cb6526b420e7ff760eec690a5fb189c764
  * rho2 = 0x2e9a4cf95fce4bbf8ebe8eb72485446ceca86268a6c2305f70d4460179334e37
  * digest (field element) = 0x2425532a0c6af3e7c0864ce59d3b1ddbd62ea79ba594c3305f8fbacf7c184249, as the organizer's 32 little-endian bytes `4942187ccfba8f5f30c394a59ba72ed6db1d3b9de54c86c0e7f36a0c2a532524`
* r = 3, the program of Appendix A (coin centre 0x3aa122248eb83041d848299af50dbd3ba917f8e886a08d71ba6d17d2456ffdf9):
  * nk1  = 0x3c4df916c81662b865a6670025e76178a0c57900cf7c3af3eb82337945943515
  * rho1 = 0x35fcfd562716cbba7a61c936cc4c08030d2a008ab6221caf4689c71eae1e0b36
  * nk2  = 0x148e77c71732f8bda84e47367ac1fbffa8dc4dfa25281007012f225f87511999
  * rho2 = 0x245ec81818f89e67e3c2d885f5af71757f1f34bc889a3f85888c17eca477c254
  * digest (field element) = 0x084cd34ed9f671d4bc9e791404edb59cdccdcd7ed80b243584356a620bd3cd0e

### 10.2 The experiment declared in `experiments/manifest.json`

One experiment, `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r@@R@@-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so the pair is accepted only when that copy agrees with the target. It is not offered as a test of `H-GEOM-w@@W@@`, of the cost or of the success probability; those rest on sections 6, 7 and 9.

@@EXECUTOR_STATUS_SENTENCE@@

### 10.3 What this evidence cannot show, and why there is no executed run at r = @@R@@

The premise `H-GEOM-w@@W@@` is about curves of degree about `5^@@DEXP@@` over a 255-bit field. It cannot be tested at that size: one trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@, and the degree grows by a factor of 5 with every round. The executed centres at r = 3, 4, 5 show that the construction produces collisions at those degrees and that usable roots appeared at four of the five centres tried; they show nothing about the two moments of section 9.2 at r = @@R@@ and they are not a sample. The experiment of 10.2 is a reduced event on the digest. The claim is the premise, with the reduction of section 9.2.

