# Step COUNT: the sub-class and the first-stage rule, counted with our own counter

Research note of `research/pkg7/count`, 2026-10-06 (runs 20:52 to 21:30). The package is a DRAFT. Nothing here is
filed, staged or submitted; no `yukon` command was run, no network was used, `.key` was not read, the GPU was not used.
Paths are relative to the workspace root unless they have no folder (then they are in this folder).
Files of GPT Sol 6.1 (`astra-jobs/server_tasks_2026-10-06/gpt_sol_answer_K.md`, `_L.md`, `_M.md` and their CSV
files) were read as data to compare with. No figure below is taken from them.

## 0. Result

1. **Every outside figure reproduces exactly.** With our counter, pin H8, class eta 830303cf:
   - cube k = 15 (mask 07ef8303, value 030c0303, 131,072 members): R = 194382080300609/1048576 = **185,377,197.55**;
   - inside it: six conditions keep 3109942325834715/16777216 = **185,367,007.60**, seven keep
     6219882655062379/33554432 = **185,366,948.10**, eight keep 6219586146887739/33554432 = **185,358,111.47**;
   - cube k = 17 (mask 07ef831b, value 030c031b, 32,768 members): R = 390412035178855/2097152 = 186,162,965.38;
     six 186,151,462.10, seven 186,151,422.06, eight **186,142,708.93**;
   - full class: R = 85074516985129/524288 = 162,266,763.66; the six conditions h16 = 0, h17 = 0, h0 = 0, h1 = 1,
     h2 XOR h10 = 1, h3 XOR h11 = 1 keep 5443991608233427/33554432 = **162,243,592.98**.
   21 exact fractions (3 totals; 17 rule masses, the old-six baselines and the nine-condition sets among them;
   1 conservative count), the R of every beta (53 + 51 + 60, and the 60 rows of `gpt_sol_beta_M_A15.csv`) and
   3,243 per-outcome integers (1,081 outcomes) were compared with Sol's files: **0 differ**. 17 printed decimals
   of the answers K, M and of the task text: the same to the last printed digit (`cmp_digits.txt`).
2. **The conservative count** (every outcome that has a violating solution dropped whole) is new here; Sol gives none
   for the cubes. Inside the cubes it is almost the exact mass: eight conditions, k = 15:
   12147454997539/65536 = **185,355,453.45** (2,658 below the exact 185,358,111.47); k = 17: 186,139,837.69.
3. **The eight-condition rule is a rule for the cube only.** On the full class the same eight conditions keep
   76,072,772.68 (47 percent) and the conservative count is 0: P = 0 holds on about half of the mass of the class.
4. **Recommended: cube k = 15 with the eight conditions** (section 7): kept 185,358,111.47 exact (185,355,453.45
   conservative), f = kept / 3.75 = 49,428,830 = 2^25.5588, time_log2 **95.81** with the counts of
   `research/pkg7_program/COST.txt` and the entry budget 2^-5, IF the eight-condition test costs no more than the
   program's rule-6 test (stage A 53). That is not counted. With this helper's estimate of the test (stage A 63)
   it is 96.04; with the tightened batch of `research/pkg7_prep/opt` 95.45 (as given) or 95.79 (estimate).
   k = 17 is 0.006 lower in every row and has a quarter of the members.

## 1. What was built

`research/h8/rule_exact` (finished at 19:38, see its `RULE_EXACT.md`) has the exact counter for a rule on h1:
`pair_calc_rule.c` with `n3r.inc`, on top of the unchanged `research/night/main/n3x.inc`, `research/r2_e3count.c`
and the outcome search of `research/h8/counts/pair_calc_batch.c`. Its two side-3 functions already take a pair
(extra fixed bits of e1, their values); the calculator passed 0, 0. This folder adds the cube and nothing else:

| file | what it is |
|---|---|
| `r2_e3count.c`, `n3x.inc`, `pair_calc_batch.c`, `n3r.inc`, `pair_calc_rule.c`, `rule_tab.py` | copies from `research/h8/rule_exact`, byte for byte (`sources.sha`: six of six hashes equal; the first two equal the originals in `research/` and `research/night/main/`) |
| `mk_sub.py` -> `pair_calc_sub.c` | the calculator with the option `-cube MASK VALUE`: 7 replacements, 23 lines differ from `pair_calc_rule.c`; the cube must contain the class mask and agree with the class value, or the program stops |
| `sub_bf.c` | complete enumeration at 8-bit words with cubes and with three-bit parities (section 3) |
| `sub_tab.py` | exact tables (Python fractions) and the comparison with Sol's files; rules are matched as affine sets (reduced row echelon form), so two lists of conditions for the same set of h1 count as the same rule |
| `cmp_digits.py`, `cmp_orig.py`, `cost.py`, `mk_tables.py` | printed decimals; the original calculator; the cost table; the tables of section 4 |
| `c00_env.sh` .. `c10_pending.sh` | the commands (section 9) |

All counts are integers (unsigned 128 bit in C, Python integers and fractions for products and sums). No floating
point is on the path of a figure quoted as a fraction. The 60 betas are the list of `research/h8/rule_exact`
(`h8_betas_pos.txt`, the betas that carry mass in the full class); a cube is a subset of the class, so a beta
without mass in the class has none in a cube.

## 2. The rules as bit conditions on h1

h1 is the first-half d value of the side-3 call on message A; bit 0 is the lowest bit. A condition is written
`MASK:V`, "the XOR of the bits of h1 in MASK is V". From `gpt_sol_answer_M.md`, table "Exact affine conditions":
F = {h16 XOR h17 = 0, h2 XOR h10 = 1, h3 XOR h11 = 1, h0 = 0, h1 = 1}; P = 01001008 = h3 XOR h12 XOR h24;
Q = 02002040 = h6 XOR h13 XOR h25. For k = 15 and k = 17 the selected sets are F; P = 0 (six), F; P = 0; Q = 0
(seven), F; h16 = 0; P = 0; Q = 0 (eight).

| name | conditions | as given to the counter |
|---|---|---|
| p4 | h0 = 0, h1 = 1, h16 = 0, h17 = 0 (rule 4 of the programs) | `00000001:0,00000002:1,00010000:0,00020000:0` |
| p5 | p4 and h2 XOR h3 = 1 (rule 5, the filed one) | p4 `,0000000c:1` |
| F5 | F | `00030000:0,00000404:1,00000808:1,00000001:0,00000002:1` |
| old6 | p4 and h2 XOR h10 = 1, h3 XOR h11 = 1 (Sol's "old six", its K k = 6) | `00010000:0,00020000:0,00000001:0,00000002:1,00000404:1,00000808:1` |
| S6 | F and h3 XOR h12 XOR h24 = 0 | F5 `,01001008:0` |
| S7 | S6 and h6 XOR h13 XOR h25 = 0 | F5 `,01001008:0,02002040:0` |
| **S8** | **h0 = 0, h1 = 1, h16 = 0, h17 = 0, h2 XOR h10 = 1, h3 XOR h11 = 1, h3 XOR h12 XOR h24 = 0, h6 XOR h13 XOR h25 = 0** | old6 `,01001008:0,02002040:0` |
| S9 | S8 and h2 XOR h3 = 1 (Sol's nine) | S8 `,0000000c:1` |
| K7, K8 | old6 and h10 XOR h11 = 1; old6 and h2 XOR h3 = 1, h24 XOR h29 XOR h30 = 1 (answer K, full class) | old6 `,00000c00:1`; old6 `,0000000c:1,61000000:1` |

eta below bit 31 is 030303cf: h1 bits 0 to 3, 6 to 9, 16, 17, 24, 25 are fixed by the difference dh1. The bits
10, 11, 12, 13 of the rules lie outside it; the counter treats them as free bits of h1 (the second case of
`RULE_EXACT.md` section 2, tested here at 8 bits with three-bit parities and at 32 bits against Sol).

## 3. Brute force at 8-bit words (`sub_bf.c`, result `bf8_sub.txt`, command `c02_bf.sh all 4`, 260 s)

The enumeration of `rule_bf.c` (every quadruple (Y4, h1, Y9, w8) through the two executions of E3 written from the
definition of G; every side-1 triple) with these changes: every class of a case gets a random cube of 0 to 3 extra
fixed bits of e1 (the top bit included) and only its Y4 are enumerated; the counter is called with the same cube
(in part B through the variables that `-cube` sets); six rules per case, among them parities of three bits and
rules of 3 to 6 conditions of weight 1, 2 or 3.

| run | part A: cases, outcomes with solutions (in a proper cube), rule counts compared | part B: constant sets, (class, beta) with Z-tuples (in a proper cube), integers compared | different |
|---|---|---|---|
| 1, seed 7001, pruned search | 3; 18,428 (11,532); 331,704 | 40; 800 (597); 1,562,624 | 0 |
| 2, seed 7002, pruned search | 2; 30,470 (24,180); 548,460 | 32; 847 (602); 1,175,552 | 0 |
| 3, seed 7003, unpruned search of `pair_calc.c` | none | 32; 377 (247); 874,496 | 0 |
| 4, seed 7004, `n3r_orig` left out above 2^5 triples (4,102 outcomes by `n3r_proj` alone) | none | 32; 824 (601); 1,318,912 | 0 |
| 5, seed 7005, no cube (the counter of `rule_exact` with the new kinds of rules) | 1; 32,882 (0); 591,876 | 16; 154 (0); 401,408 | 0 |
| all | 6 cases; 81,780 (35,712); 1,472,040 | 152; 3,002 (2,047); 5,332,992; 1,593,174,656 seven-tuples in Z | **0** |

481 classes, 314 with a proper cube (3,410 of 6,400 members inside). In part A 155,513 (outcome, rule) pairs have
a three-bit parity in the rule (74,870 of them split by the rule) and 291,521 have a rule bit outside eta. Also
zero in every run: empty outcomes sampled 1 in 16, the total of the unchanged `n3x` with the cube, `n3r_orig`
against `n3r_proj` (both walks), E1 against the side-1 histogram, outcomes not counted.

## 4. The counts at 32 bits (`a15.out`, `a17.out`, `full.out`; `c04_chain.sh`; 344 s, 210 s, 510 s on 4 processes)

Constants of pin H8: D3 fdb77cfd, D11 0a08818b, delta fffffff8, Y3 8127c181, Y11 7af77f38, eta 830303cf. Options
`-mode both -capwork 24 -capx 24`: `n3r_orig` counts an outcome up to 2^24 triples and `n3r_proj` counts it too
(compared); above, `n3r_proj` alone. "Exact" = R of the solutions whose h1 satisfies the rule. "Conservative" = R
of the outcomes (beta, tau, eps) without any violating solution inside the class or cube that is counted.

### Cube k = 15, mask 07ef8303 value 030c0303, 131,072 members (denominator 2^81)

R = 194382080300609/1048576 = 185,377,197.552308083; 53 betas with a part; 317 outcomes with a nonzero product.

| rule | conditions | exact passing mass | decimal | conservative | decimal | outcomes: all pass / none / split |
|---|---|---|---|---|---|---|
| F5 | 5 | 3109942325834715/16777216 | 185,367,007.603330314 | 12147455784275/65536 | 185,355,465.458297729 | 109 / 24 / 184 |
| old6 | 6 | 3109793308378027/16777216 | 185,358,125.470759094 | 12147455783971/65536 | 185,355,465.453659058 | 104 / 69 / 144 |
| S6 | 6 | 3109942325834715/16777216 | 185,367,007.603330314 | 12147455784275/65536 | 185,355,465.458297729 | 109 / 24 / 184 |
| S7 | 7 | 6219882655062379/33554432 | 185,366,948.099803299 | 12147454997843/65536 | 185,355,453.458297729 | 104 / 31 / 182 |
| **S8** | 8 | 6219586146887739/33554432 | **185,358,111.467592090** | 12147454997539/65536 | **185,355,453.453659058** | 99 / 76 / 142 |
| S9 | 9 | 81752754751179/524288 | 155,931,005.003316879 | 4145247956617/32768 | 126,502,928.363555908 | 43 / 179 / 95 |
| p5 | 5 | 81752760518347/524288 | 155,931,016.003316879 | 4145248317065/32768 | 126,502,939.363555908 | 45 / 177 / 95 |
| p4 | 4 | 1554896901466299/8388608 | 185,358,154.948508620 | 48589823135925/262144 | 185,355,465.453815460 | 107 / 69 / 141 |

Per beta (R, then exact / conservative; all 53 in `a15_parts.tsv`, all 317 outcomes in `a15_outcomes.tsv`):

| beta | outcomes | R | S6 exact | S6 cons. | S7 exact | S7 cons. | S8 exact | S8 cons. |
|---|---|---|---|---|---|---|---|---|
| 18b0e098 | 7 | 67,698,688 | 67,698,688 | 67,698,688 | 67,698,688 | 67,698,688 | 67,698,688 | 67,698,688 |
| 18b1a098 | 16 | 51,384,320 | 51,384,320 | 51,384,320 | 51,384,320 | 51,384,320 | 51,384,320 | 51,384,320 |
| 18d0e098 | 12 | 50,790,400 | 50,790,400 | 50,790,400 | 50,790,400 | 50,790,400 | 50,790,400 | 50,790,400 |
| 18d1a098 | 12 | 13,246,464 | 13,246,464 | 13,246,464 | 13,246,464 | 13,246,464 | 13,246,464 | 13,246,464 |
| 18b3e098 | 4 | 1,474,560 | 1,474,560 | 1,474,560 | 1,474,560 | 1,474,560 | 1,474,560 | 1,474,560 |
| 18d3e098 | 6 | 755,712 | 755,712 | 755,712 | 755,712 | 755,712 | 755,712 | 755,712 |
| 18d16398 | 6 | 13,328 | 7,752 | 0 | 7,752 | 0 | 456 | 0 |
| 18f1e098 | 8 | 3,465 | 1,665 | 0 | 1,665 | 0 | 1,665 | 0 |
| the other 45 | 246 | 10,260.5523 | 7,446.6033 | 5,321.4583 | 7,387.0998 | 5,309.4583 | 5,846.4676 | 5,309.4537 |

The six heaviest betas (185,350,144 of R) pass all eight conditions with every solution. In the cube the four
single-bit conditions p4 already keep 185,358,154.95; the four further conditions of S8 cost 43.48 of mass.
S6 = F5 exactly, outcome by outcome: P = 0 is implied by F on every solution in the cube, as Sol says. Hence
old6 with P = 0 (seven conditions) keeps what old6 keeps, 185,358,125.47 (a deduction: old6 lies inside F5).

Inside the run: `n3r_orig` = `n3r_proj` on 687 outcomes, 0 different; 285 outcomes by `n3r_proj` alone (16 with a
product); the unchanged `n3x` called with the cube = the integer count on 680 outcomes where it does not sample,
0 different (it samples on 52; no figure uses it); integer E1 = `e1_exact` on 972, 0 different; not counted 0.

### Cube k = 17, mask 07ef831b value 030c031b, 32,768 members (denominator 2^79)

R = 390412035178855/2097152 = 186,162,965.382983685; 51 betas with a part; 311 outcomes with a nonzero product.

| rule | conditions | exact passing mass | decimal | conservative | decimal | outcomes: all pass / none / split |
|---|---|---|---|---|---|---|
| F5 | 5 | 3123103288437351/16777216 | 186,151,462.104162633 | 12198861193555/65536 | 186,139,849.755172729 | 107 / 35 / 169 |
| old6 | 6 | 3122956653343671/16777216 | 186,142,721.971492231 | 12198861193251/65536 | 186,139,849.750534058 | 102 / 77 / 132 |
| S6 | 6 | 3123103288437351/16777216 | 186,151,462.104162633 | 12198861193555/65536 | 186,139,849.755172729 | 107 / 35 / 169 |
| S7 | 7 | 6246205233159159/33554432 | 186,151,422.058318824 | 12198860403027/65536 | 186,139,837.692672729 | 103 / 39 / 169 |
| **S8** | 8 | 6245912868955207/33554432 | **186,142,708.926058024** | 12198860402723/65536 | **186,139,837.688034058** | 98 / 81 / 132 |
| S9 | 9 | 85325764079051/524288 | 162,745,979.459859848 | 4566154751625/32768 | 139,347,984.363555908 | 51 / 174 / 86 |
| p5 | 5 | 85325769846219/524288 | 162,745,990.459859848 | 4566155112073/32768 | 139,347,995.363555908 | 53 / 172 / 86 |
| p4 | 4 | 1561478367854791/8388608 | 186,142,726.880883098 | 24397722388837/131072 | 186,139,849.768348694 | 108 / 77 / 126 |

Heaviest betas, R = S6 = S7 = S8 exact = conservative: 18b0e098 67,698,688; 18b1a098 51,650,560; 18d0e098
50,790,400; 18d1a098 13,516,800; 18b3e098 1,638,400; 18d3e098 839,680 (together 186,134,528). The other 45:
R 28,437.38, S8 exact 8,180.93, S8 conservative 5,309.69 (`a17_parts.tsv`, `a17_outcomes.tsv`).
Inside the run: both functions on 666 outcomes, 0 different; 285 by `n3r_proj` alone (16 with a product); `n3x`
with the cube = the integer count on 659, 0 different (samples on 52); E1 on 951, 0 different; not counted 0.

### Full class, mask 03cf8303 value 030c0303, 524,288 members (denominator 2^83)

R = 85074516985129/524288 = 162,266,763.658769608; 60 betas; 453 outcomes with a nonzero product.

| rule | conditions | exact passing mass | decimal | conservative | decimal | outcomes: all pass / none / split |
|---|---|---|---|---|---|---|
| F5 | 5 | 2722188192869763/16777216 | 162,255,060.247764766 | 2658161987811/16384 | 162,241,332.263854980 | 165 / 45 / 243 |
| **old6** | 6 | 5443991608233427/33554432 | **162,243,592.984480470** | 332270216079/2048 | 162,241,316.444824219 | 132 / 104 / 217 |
| K7 | 7 | 302248762304709/2097152 | 144,123,440.887789249 | 64513843589/512 | 126,003,600.759765625 | 54 / 249 / 150 |
| K8 | 8 | 528287346417605/4194304 | 125,953,518.490220308 | 107782144 | 107,782,144.000000000 | 29 / 249 / 175 |
| S6 | 6 | 2722188192874883/33554432 | 81,127,530.124034971 | 0 | 0 | 0 / 45 / 408 |
| S7 | 7 | 5105306373346779/67108864 | 76,074,993.213218138 | 0 | 0 | 0 / 167 / 286 |
| S8 | 8 | 5105157355890091/67108864 | 76,072,772.680075333 | 0 | 0 | 0 / 212 / 241 |
| p5 | 5 | 302248762304709/2097152 | 144,123,440.887789249 | 64513843589/512 | 126,003,600.759765625 | 54 / 249 / 150 |

p5 is the regression against `research/h8/rule_exact` and the filed count: exact 144,123,440.89, conservative
126,003,600.76, both as there. The conservative count of old6 equals that of rule 4 (162,241,316.44). Per beta:
`full_parts.tsv`; heaviest, R = old6 exact = old6 conservative: 18b0e098 71,698,432; 18d0e098 54,005,760;
18b1a098 25,692,160; 18d1a098 8,429,568; 18b3e098 1,566,720; 18d3e098 838,656.

## 5. Against the outside figures (`a15_cmp.txt`, `a17_cmp.txt`, `full_cmp.txt`, `cmp_digits.txt`)

| what | Sol | ours | |
|---|---|---|---|
| R, cube k = 15 (L, M) | 194382080300609/1048576 | the same | equal |
| k = 15: five = six (F; P = 0), seven, eight, nine, old six | 3109942325834715/16777216, 6219882655062379/33554432, 6219586146887739/33554432, 81752754751179/524288, 3109793308378027/16777216 | the same | equal |
| R, cube k = 17 | 390412035178855/2097152 | the same | equal |
| k = 17: five = six, seven, eight, nine, old six | 3123103288437351/16777216, 6246205233159159/33554432, 6245912868955207/33554432, 85325764079051/524288, 3122956653343671/16777216 | the same | equal |
| full class: R; K k = 5, 6, 7, 8 | 85074516985129/524288; 2722188192869763/16777216, 5443991608233427/33554432, 302248762304709/2097152, 528287346417605/4194304 | the same | equal |
| full class, rule 5: exact and conservative (answer E) | 302248762304709/2097152, 64513843589/512 | the same | equal |
| per outcome: side-1 count, side-3 count, pairs | 317 (k = 15), 311 (k = 17), 453 (class) outcomes with a product | the same sets; 951 + 933 + 1,359 integers | 0 differ |
| per beta R | 53 (k = 15, also `gpt_sol_beta_M_A15.csv`: 60 rows, 7 zero), 51 (k = 17), 60 (class) | the same sets | 0 differ |
| M3: four heaviest betas of k = 15 | 67,698,688; 51,384,320; 50,790,400; 13,246,464; together 183,119,872 | the same | equal |
| printed decimals (K, M, task text), 17 strings | | | same to the last digit |

**Differences: none.** What Sol does not give and is therefore ours alone: every conservative count of the cubes,
the per-beta split of the rule masses, the rules p4 and p5 inside the cubes, and S6, S7, S8 on the full class.

Two of our own figures elsewhere do differ from the ones here: `research/others/tests/RESULTS.md` (section 1.1)
gives for the same cube "rule 4: 185,355,446.0" and "rule 5: 126,502,922.5"; here the conservative counts are
185,355,465.45 and 126,502,939.36 (19.5 and 16.9 more). The likely reason is the definition: there an outcome
seems to be dropped when it has a violating solution anywhere in the CLASS, here when it has one in the CUBE
(the trials only use members of the cube). NOT checked outcome by outcome. Its all-outcome curve has 2 bits
185,377,197.2 and 4 bits 186,162,965.1, each 0.3 below the exact figure, as its whole-class figure is
(162,266,763.4 against 162,266,763.66); the reason was not looked up.

## 6. The original calculator with its own option (`origall_a15.txt`, `origall_a15_cmp.txt`; `c05b_all.sh`)

`research/night/main/pair_calc.c` (sha256 d13ab39a507d07bd, untouched, built here as `pair_calc_orig`) with
`-sub 04200000 00000000`, all 60 betas, 90 s limit per beta, 269 s in all: 54 betas finished; each prints the
exact part to its one printed decimal (largest difference 0.044, rounding; one beta has a sampled outcome and
prints 0.0 for an exact 0.0056). Sum of the 54 printed parts 185,377,197.2; exact sum over the same 54 betas
185,377,197.2177. Six betas hit the limit (19b1bf98, 1fb36398, 19b1e398, 19b17f98, 1fb1bf98, 1fb17f98); their exact
parts together are 0.3346. So the original gives the R of the cube on all but 1.8e-9 of it.
The same for k = 17 (`-sub 04200018 00000018`, `origall_a17.txt`, `origall_a17_cmp.txt`, 211 s): 58 betas finished, each
equal to the exact part at the one printed decimal (largest difference 0.05; five have a sampled outcome, parts
0.1 and below); sum of the printed parts 186,162,965.3, exact sum over the same betas 186,162,965.2972; two betas
hit the limit (19b1bf98, 1fb1bf98; exact parts together 0.0858).

## 7. Cost and recommendation (`COST_COUNT.txt`, command `c06_tab.sh cost`)

Model of `research/pkg7_program/work/tools/cost.py`: a share 2^-(n-3) of the batches enters stage 2 for a rule
of n conditions; budgeted = (stage A + share * stage 2) / 7 + middle step / members (+ table build and outer
step, below 1e-8); charged = budgeted * 1.04 rounded up to 0.1; time_log2 = 123.339 - log2(f) + log2(charged/34)
+ 0.012 with f = kept / 3.75. Program counts read from the files: `COST.txt` stage A 47 / 49 / 53 for the
program's rules 4 / 5 / 6, stage 2 147, middle step 148; tightened batch (`research/pkg7_prep/opt/COST_OPT.txt`,
strict tier, confirmed by `opt_verify/VERDICT.md`) 37 / 37 / 41, stage 2 128, middle step 134. Grok's batch
(`research/grok/work/job15_batch`, 41 and 127 for rule 5) is the weaker of the two tightened ones for rule 5:
(41 + 127/4)/7 = 10.39 against (37 + 128/4)/7 = 9.86.

**Stage A of the new rules is not counted by any machine.** Two columns: "as given" takes the program's rule-6
count for every rule of six or more conditions (what "COST.txt scaled for the entry budget" says literally);
"estimate" is this helper's guess from what the program's rules 5 and 6 cost over rule 4: the two pairs
h2/h10 and h3/h11 share one shift (+3 operations +1 load), P and Q need three more shift groups (+9 operations
+3 loads): old6 = rule 4 + 4, S8 = rule 4 + 16.

| class or cube | rule | kept exact (conservative) | log2 f at margin 3.75 | program, as given: stage A, charged, time_log2 | program, estimate | tightened, as given | tightened, estimate |
|---|---|---|---|---|---|---|---|
| **k = 15** | **S8** | 185,358,111.47 (185,355,453.45) | 25.5588 | 53, 8.6, **95.809** | 63, 10.1, 96.041 | 41, 6.7, **95.449** | 53, 8.5, 95.792 |
| k = 17 | S8 | 186,142,708.93 (186,139,837.69) | 25.5649 | 53, 8.6, 95.803 | 63, 10.1, 96.035 | 41, 6.7, 95.443 | 53, 8.5, 95.786 |
| k = 15 | S7 | 185,366,948.10 (185,355,453.46) | 25.5589 | 53, 9.3, 95.922 | 65, 11.1, 96.177 | 41, 7.3, 95.573 | 55, 9.4, 95.937 |
| k = 15 | old6 | 185,358,125.47 (185,355,465.45) | 25.5588 | 53, 10.7, 96.124 | 51, 10.4, 96.083 | 41, 8.5, 95.792 | 41, 8.5, 95.792 |
| k = 15 | S6 | 185,367,007.60 (185,355,465.46) | 25.5589 | 53, 10.7, 96.124 | 61, 11.8, 96.265 | 41, 8.5, 95.792 | 51, 10.0, 96.027 |
| full class | old6 | 162,243,592.98 (162,241,316.44) | 25.3667 | 53, 10.7, 96.316 | 51, 10.4, 96.275 | 41, 8.5, 95.984 | 41, 8.5, 95.984 |
| k = 15 | p5 | 155,931,016.00 (126,502,939.36) | 25.3094 | 49, 12.8, 96.632 (cons. 96.934) | counted | 37, 10.3, 96.319 (cons. 96.620) | counted |
| full class | p5 | 144,123,440.89 (126,003,600.76) | 25.1958 | 49, 12.8, 96.746 (cons. 96.940) | counted | 37, 10.3, 96.432 (cons. 96.626) | counted |
| k = 15 | p4 | 185,358,154.95 (185,355,465.45) | 25.5588 | 47, 18.0, 96.875 | counted | 37, 15.1, 96.621 | counted |

With the conservative count in place of the exact one the times of S6, S7, S8, old6 and p4 inside the cubes move
by less than 0.0001. Reference: the filed pkg6 is kept 126,003,600 (conservative), f = 2^25, charged 19.1, 97.52.

**Recommendation.** Class: the cube k = 15, (e1 AND 07ef8303) == 030c0303, 131,072 members. Rule: S8, the eight
conditions of section 2. Kept count 185,358,111.47 (exact; 185,355,453.45 if the package keeps arguing per
outcome). At margin 3.75: f = 49,428,830 = 2^25.5588 (a round f = 49,400,000 gives margin 3.752). time_log2
95.809 with the counts of `COST.txt` as given, which rounds up to **95.9**; 95.449 (**95.5**) if the tightened
strict batch is used and its stage A does not grow. Read literally, the criterion of the task (best time_log2
at margin 3.75) picks k = 17 with S8: 95.803 against 95.809. I recommend k = 15 all the same: 0.006 bit is
below the rounding of the charged cost and of the claim (both round up to 95.9), and k = 17 has a quarter of
the members, so its outer range has to grow four times more (item 6 of section 8). The rule is the same for
both, so the choice can be changed later without a new count.

What the table shows beyond that: (a) the sub-class is the solid part of the gain. From the filed count to the
cube with a rule that keeps everything it is log2(185,358,111 / 126,003,600) = 0.557 bit; (b) once four more
conditions are nearly free in mass, the cost per trial is almost all stage A (53 / 7 = 7.57 of 8.23), so the
seventh and eighth conditions pay only if their test is cheap. On the estimate S8 and old6 are within 0.05 bit
of each other in the program tier and equal in the tightened tier. If the counted test of S8 comes out near the
estimate, old6 in the cube (six conditions, one shift) is the simpler rule at the same score: 96.08 / 95.79.

## 8. What is NOT established

1. **Stage A for S8 (and for old6, S6, S7).** No program tests these conditions yet and no machine counted them.
   The times "as given" assume the eight-condition test costs what the program's rule-6 test costs; the column
   "estimate" is a guess of this helper. The spread is 0.23 bit (program tier) to 0.34 bit (tightened tier).
2. **The program's test of the new conditions.** Bit i of h1 is bit (i + 24) mod 32 of z XOR bit (i + 16) mod 32
   of e1. The conditions on h1 bits 11, 12, 13 need e1 bits 27, 28, 29, which neither the class nor the cube
   fixes (the cube fixes 21 and 26). The two-level program carries e1 in its list word, so its test word holds
   every bit of h1 (by the description in `RULE_EXACT.md`, section 8; not run for these conditions); the
   function `rule_a_constants()` of the pkg6 program refuses such bits. `map_check.py` of `research/h8/rule_exact`
   (rule as counted against rule as tested, on real trials) has not been run for S8, and Lemma A does not cover it.
3. **Real trials.** The agreement is between two counters of the same model (the event Z with the two sides
   independent and uniform). That a real trial in the cube satisfies S8 with probability 2^-8, which the budget
   2^-5 needs (union bound 7 * 2^-8 = 0.0273), is not measured; the measured shares exist for rules 4, 5, 6 only.
   No real-message run and no scaled-down end-to-end run exists for the cube or for S8.
4. **Betas outside the list.** The 60 betas are those that carry mass in the full class by
   `research/h8/counts/H8_count.txt` and by Sol's job A; this job did not search the others again.
5. **Outcomes counted by one function.** 285 outcomes of each cube run were counted by `n3r_proj` alone (above
   2^24 triples), 16 of them with a product. Their side-3 totals equal Sol's; their split by the rule rests on
   the 8-bit enumeration and on the totals per rule being equal to Sol's.
6. **The trial space.** pkg6 searches 2^127 / f trials (its proof, H1 and the lines after it: 2^127 / 2^25 =
   2^102, which is all trials of a run: 2^83 contexts times 524,288 members). At f = 2^25.5588 the claim needs
   2^101.44 trials; the ranges of `research/pkg7_prep/text/02_loops_and_trial_space.md` with 131,072 members give
   2^100. An outer range has to grow by a factor of at least 2.72 (four times as many values of C0.d1 give 2^102),
   for k = 17 by at least 10.8, and the halting budgets of step 4 have to be set again. Not done here; this is
   this helper's reading of the fragment and of the filed proof, not a checked statement.
7. **Optimality.** Sol calls its sets "best found", not proved optimal; nothing here tests other rules. Its
   search log (`gpt_sol_affine_M_A15_search.csv`, read as data) says that with one- and two-bit parities alone
   the best seventh condition keeps 84 percent; that was not recounted.
8. **Exact against conservative.** Inside the cube the two differ by 2,658 of 185 million, so the choice hardly
   matters for the score; but the text has to say which one H1 is set against, and "exact" needs the argument
   per solution that pkg6 does not have (`RULE_EXACT.md`, section 13, items 5 and 7).
9. **The cost model** is used as given (formula, 1.04, rounding, budget rule); nothing was measured again. The
   16-register convention for words kept across batches is a matter of the package text.
10. Sol's other figures (k = 16 and k = 24 cubes, job D, upper bounds, joint laws) were not recounted.

## 9. Commands (from PowerShell; each prints a few lines)

    $H = "./research/pkg7/count"
    wsl -d Ubuntu -- bash "$H/c00_env.sh"                 # scratch ~/hashsmash/pkg7_count, load
    wsl -d Ubuntu -- bash "$H/c01_setup.sh"               # copies, hashes, pair_calc_sub.c, both builds
    wsl -d Ubuntu -- bash "$H/c02_bf.sh" all 4            # brute force at 8 bits, 5 runs, 260 s
    wsl -d Ubuntu -- bash "$H/c04_chain.sh"               # a15, a17, full: 4 processes, nice 5, about 18 minutes
    wsl -d Ubuntu -- bash "$H/c06_tab.sh" a15             # tables and comparison (also: a17, full, cost)
    wsl -d Ubuntu -- bash "$H/c05b_all.sh" a15 04200000 00000000 90    # the original calculator, -sub
    python -B cmp_orig.py a15 ; python -B cmp_digits.py ; python -B mk_tables.py
    wsl -d Ubuntu -- bash "$H/c08_hashes.sh"              # hashes.txt

One run by hand: `pair_calc_sub fdb77cfd 0a08818b fffffff8 8127c181 830303cf h8_betas_pos.txt 7af77f38 -rule
MASK:V,... -cube 07ef8303 030c0303 -mode both -capwork 24 -capx 24` (`c03_run.sh` has the rule lists).

## 10. The file behind each figure

| figure | file | made by |
|---|---|---|
| R, exact and conservative mass per rule, totals | `a15_totals.txt`, `a17_totals.txt`, `full_totals.txt` | `c06_tab.sh` from `a15.out`, `a17.out`, `full.out` |
| the same per beta; per outcome | `*_parts.tsv`; `*_outcomes.tsv` | `c06_tab.sh` |
| comparison with Sol | `a15_cmp.txt`, `a17_cmp.txt`, `full_cmp.txt`, `cmp_digits.txt` | `c06_tab.sh`, `cmp_digits.py` |
| brute force | `bf8_sub.txt` | `c02_bf.sh all 4` |
| the original calculator | `origall_a15.txt`, `origall_a15_cmp.txt` (and `_a17`) | `c05b_all.sh`, `cmp_orig.py` |
| cost table | `COST_COUNT.txt` | `c06_tab.sh cost` |
| tables of section 4 | `COUNT_tables.md` | `mk_tables.py` |
| sources, binaries, results | `sources.sha`, `hashes.txt`, `runs.log` | `c01_setup.sh`, `c08_hashes.sh`, `c03_run.sh` |

Credit for the package, as the handoff has it: GPT Sol 6.1 (the cube curve, the rule, the exact figures that
this job reproduces), winglock (the idea of a sub-class, first used on our first entry).
