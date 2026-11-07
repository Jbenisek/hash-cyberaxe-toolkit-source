"""Build human and machine-readable research documentation from recorded results."""
from pathlib import Path
import csv,json,math,hashlib
from poseidon_core import P,CAP,ROOT5
B=Path(__file__).resolve().parent;D=B/'data';R=B/'reports';R.mkdir(exist_ok=True)
(B/'round_cards').mkdir(exist_ok=True)
stats=json.loads((D/'results.json').read_text());low=json.loads((D/'low_round_chart_results.json').read_text())
extra=json.loads((D/'extra_results.json').read_text())
def readcsv(name):
 with (D/name).open() as f:return list(csv.DictReader(f))
def writecsv(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
srcbase='https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/'
sources=[
('S01','HashSmash Orchard target proposal #923','https://github.com/Layr-Labs/hash-smash/pull/923','LIVE CONNECTOR SNAPSHOT','Open/unmerged when queried; no Yukon registration or baselines in this PR; field-cost question explicitly open. Head 01f736268b7086d97f38837d343d63a81bf31649.'),
('S02','Proposed contest verifier','https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/verifier/poseidon.py','PINNED PROPOSAL SOURCE','Exact target encoding, schedule, constants and output. Reviewed source; not copied as an authenticated full checkout.'),
('S03','Official P128Pow5T3 parameters',srcbase+'p128pow5t3.rs','PRIMARY SOURCE','RF=8, RP=56, exponent 5; official parameter and vector tests.'),
('S04','Official Poseidon round and hash mode',srcbase+'lib.rs','PRIMARY SOURCE','Round constants -> S-box -> MDS; ConstantLength<2> capacity=2^65; one output field element.'),
('S05','Official Grain constant generation',srcbase+'grain.rs','PRIMARY SOURCE','80-bit self-shrinking LFSR; reproduced in poseidon_core.py.'),
('S06','Official Cauchy MDS generation',srcbase+'mds.rs','PRIMARY SOURCE','Cauchy 1/(x_i+y_j), secure_mds selection 0 for this parameter set; reproduced locally.'),
('S07','Official permutation vectors','https://github.com/zcash/zcash-test-vectors/blob/master/test-vectors/json/orchard_poseidon.json','PRIMARY SOURCE / TRANSCRIBED SUBSET','First 3 of 11 vectors transcribed into local JSON and replayed. Do not report all 11 as tested.'),
('S08','Official constant-length hash vectors','https://github.com/zcash/zcash-test-vectors/blob/master/test-vectors/json/orchard_poseidon_hash.json','PRIMARY SOURCE / TRANSCRIBED COPY','All 11 vectors transcribed and replayed. Source master is not a pinned commit; local manifest pins the copy used.'),
('S09','Proposed contest regression tests','https://github.com/Annkkitaaa/hash-smash/blob/01f736268b7086d97f38837d343d63a81bf31649/tests/test_poseidon.py','PINNED PROPOSAL SOURCE','22-vector suite and 27/54 reference arithmetic described there; our run separately replayed 14 official vectors.'),
('S10','POSEIDON design paper','https://eprint.iacr.org/2019/458','PRIMARY RESEARCH / LANDING ABSTRACT ONLY','Design context, not a new native attack or a transferred numeric bound. Full paper not reviewed in this pass.'),
('S11','Algebraic Cryptanalysis of HADES Design Strategy: Application to POSEIDON and Poseidon2','https://eprint.iacr.org/2023/537','PRIMARY RESEARCH / LANDING ABSTRACT ONLY','Algebraic complexity revisions for specified settings; no Orchard collision result established here.'),
('S12','Breaking Poseidon Challenges with Graeffe Transforms and Complexity Analysis by FFT Lower Bounds','https://eprint.iacr.org/2025/950','PRIMARY RESEARCH / LANDING ABSTRACT ONLY','Challenge/CICO targets and memory-access costs are not automatically this two-input collision target.'),
('S13','A Zero-Dimensional Groebner Basis for Poseidon','https://eprint.iacr.org/2024/310','WITHDRAWN','Landing record reports withdrawal on 2024-12-23. Not used to justify a bound.'),
('S14','Orchard native PRF use','https://github.com/zcash/orchard/blob/main/src/spec.rs','PRIMARY SOURCE / LIVE BRANCH','prf_nf(nk,rho) uses P128Pow5T3 ConstantLength<2>. Protocol usage is not the same as freely chosen two-field contest inputs.'),
]
sources=[dict(source_id=a,title=b,url=c,scope=d,note=e) for a,b,c,d,e in sources]
writecsv('sources.csv',sources);(D/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
url={x['source_id']:x['url'] for x in sources}
findings=[
('F01','Target boundary','Two canonical field inputs; third state coordinate fixed at 2^65. No SHA-style block counter or later free message injection.','SOURCE','All proposed prefixes','S01;S02;S04','parameters.json'),
('F02','Full-state inverse','Each round, and therefore each prefix, is a permutation of Fp^3. Distinct legal input messages cannot merge in the entire state.','PROVED','Full state, all 64 prefixes','S03;S04','linear_certificates.json'),
('F03','Actual collision event','Only output lane 0 must agree. Full-state equality is a strictly stronger and impossible goal for distinct legal messages.','PROVED','Proposed hash target','S02;S04','reports/RESEARCH_REPORT.md'),
('F04','MDS mixing','All 19 nonempty square minors are nonzero; rank 3 and branch number 4. This is a linear-layer statement, not a nonlinear attack lower bound.','COMPUTED_EXACT','Native field','S06','mds_minors.csv'),
('F05','First-round legal family','In X=(m0+c00)^5,Y=(m1+c01)^5 coordinates, first-round states form an affine plane with p^2 points. Every one-round digest has exactly p messages.','PROVED','One full round, canonical two-field domain','S03;S04','low_round_chart_results.json'),
('F06','Two-round coordinate change','Two-round digest is degree 5 in X,Y, not degree 25 in these coordinates; 21 nonzero coefficients. Fixed X and digest gives at most 5 Y roots.','PROVED+COMPUTED','Proposed two-full-round prefix only','S03;S04','two_round_quintic_coefficients.csv'),
('F07','Partial-round observability','O=[e0; e0 M; e0 M^2] has rank 3. An internal difference can avoid the active S-box for two consecutive partial rounds, but not three.','PROVED+COMPUTED','Only the stated exact S-box-avoidance condition','S04','linear_certificates.json'),
('F08','Three-active-value chart','Three successive active input values uniquely parameterize any internal state in each of the 54 all-partial three-round windows.','PROVED+COMPUTED','Unrestricted internal states','S04','partial_window_charts.csv'),
('F09','Legal-state cost remains','Exactly p^2 of p^3 triples in each internal chart correspond to the legal input plane; uniformly guessing all three has legal probability 1/p.','PROVED','Cardinality, not an efficient sampler or attack bound','S02;S04','extra_results.json'),
('F10','Exact local differential','Nonzero delta: (x+delta)^5-x^5=eta is a quartic with at most 4 roots; completed-square reduction gives an exact root counter.','PROVED+COMPUTED','Single native S-box; not a multi-round probability law','S03','sbox_counts.json'),
('F11','False neutral direction','A zero local derivative at the active input does not give an exact neutral finite change. Verified on all 64 native round indices.','PROVED+COMPUTED','Chosen internal states; not legal-prefix reachability','S04','derivative_trap.csv'),
('F12','Parity signatures','No significant result after 512-test Bonferroni correction on 2048 legal message samples. This tests 8 input features vs output LSB, not full collision success.','SAMPLED','Diagnostic only; other signatures remain open','S02;S04','signature_screen.csv'),
('F13','Exact trash bookkeeping','All 66049 toy inputs enumerated through all 64 rounds. In each row collisions + noncollisions = 2181202176 unordered pairs.','EXACT_TOY','p=257, toy MDS and cap=2, not native Orchard','S04','toy_full_input_counts.csv'),
('F14','Encoding baseline','Uniform Fp encodings are not uniform 256-bit strings: bit 255 is zero and bit 254 is extremely rare. Expected XOR weight about 127 per field word.','PROVED','Uniform-field baseline only','S02','encoding_bit_baseline.csv'),
('F15','Reference pricing','Full-state reference arithmetic is 27 ops/full round, 21/partial, 1392/full deployment under add=mul=1. Field-to-word pricing is unresolved in the proposal.','COMPUTED+SOURCE','Arithmetic ledger; no accepted score','S01;S09','round_cards.csv'),
('F16','Digest-only specialization','With constant precomputation, endpoints r1/r2 need 12/34 field arithmetic operations rather than 27/54 full-state operations; excludes loads/control/encoding.','PROVED_ARITHMETIC','Not an attack or a contest claim','S02;S04','low_round_chart_results.json'),
]
findings=[dict(finding_id=a,topic=b,result=c,status=d,scope=e,source_ids=f,evidence_file=g,source_url=url[f.split(';')[0]]) for a,b,c,d,e,f,g in findings]
writecsv('findings.csv',findings)
crosswalk=[
('Q01','What does each row do?','64 round cards record ARC/S-box/MDS and the three phases.','SOURCE+COMPUTED','round_cards.csv'),
('Q02','How does every row reach every other?','4096 directed cells; 2080 forward cells sampled; 2016 future-to-stored-past cells are noncausal, not inverse impossibility.','SAMPLED+STRUCTURAL','round_pair_grid.csv'),
('Q03','What is independently writable?','m0,m1 only. Capacity and all constants are fixed; zero fresh per-round message knobs.','PROVED','F01'),
('Q04','What corresponds to the dense prefix?','Legal input plane, first four full rounds, then their p^2-point image. No A0/c7/SHA advice family is imported.','PROVED','F05;F09'),
('Q05','Which local operations are invertible?','S-box exponent inverse and MDS inverse give unique whole-state round inverse. Projection to digest is not invertible.','PROVED+COMPUTED','F02'),
('Q06','Can differences cancel or toggle?','Field difference propagates by M times fifth-power differences; zeros at one projection need not mean whole-state cancellation.','PROVED','F03;F10'),
('Q07','What is a neutral direction?','Partial S-box-avoiding subspace has dimensions 2,1,0 for 1,2,3 consecutive active-input equalities. Legal reachability separately required.','PROVED+COMPUTED','F07;F09'),
('Q08','Is a local Jacobian kernel enough?','No. Zero derivative has a nonzero fifth-order finite displacement; 64 native checks included.','PROVED+COMPUTED','F11'),
('Q09','Can one solve instead of sample?','New coordinates expose a two-round quintic; exact single-S-box quartic roots known. Full legal-generator costs remain open.','PARTIAL','F06;F10'),
('Q10','Can constraints become fewer equations?','Last digest is one field equation, not three state equations. A generic field equation costs about 254 bits under uniformity, not one bit.','PROVED_SCOPE','F03'),
('Q11','What replaces XOR parity collapse?','Fp linear relations and nonlinear solution-set unions. SHA GF(2) ranks do not transfer.','STRUCTURAL','F04;F06'),
('Q12','Do per-row probabilities multiply?','Only conditional probabilities on the actual propagated population. Local DDT maxima and sampled marginals are not independent coins.','PROVED_RULE','F10'),
('Q13','Can internal states be chosen freely?','No: p^2 legal points in p^3 internal states. Internal triple coordinates retain the 1/p legal membership constraint.','PROVED','F09'),
('Q14','What changes if we add more blocks?','The proposed ConstantLength<2> contest domain has exactly one two-element block; adding blocks changes the target.','SOURCE','F01'),
('Q15','Can round constants be changed?','No. Prefixes retain deployed RF8/RP56 constants; constants disappear from additive differences but constrain actual states.','SOURCE+PROVED','F01'),
('Q16','Can periodic / spiral ideas transfer?','Not literally as bit rotations. The exact partial-round Krylov/observability chart is the tested coordinate-system analogue.','PARTIAL','F07;F08'),
('Q17','Can we mine the failed pairs?','Exact collision/trash conservation tested in toy field. No native reduced-round collision population or correction family sampled.','EXACT_TOY+OPEN_NATIVE','F13'),
('Q18','Can a cheap signature choose the better route?','Eight preregistered-in-code input signatures vs LSB show no significant effect; meaningful conditional route ranking is still open.','SAMPLED','F12'),
('Q19','Does additional family size cut work?','Not automatically. Selection/setup/yield/distinctness and conditional success must be counted together.','ACCOUNTING_RULE','F09;F15'),
('Q20','What is the current score and leader?','No verified live Poseidon leaderboard in the retrieved snapshot; PR is open and excludes registration/baselines.','UNVERIFIED_LIVE','S01'),
('Q21','What is the generic reference?','Output alphabet p, about 2^254; birthday scale sqrt(p), about 2^127. Not the strength of one or two rounds.','SOURCE+DERIVED','F05;F14'),
('Q22','Are field and CPU word operations the same?','No. Proposed field arithmetic and measured CPU times are separate columns; no inherited SHA/BLAKE unit conversion.','SOURCE+MEASURED','F15'),
('Q23','What is memory use?','A canonical state is 96 bytes and 192 constants + MDS is 6432 bytes; actual Python objects/workbook overhead differs. No proposed search-memory score.','EXACT_STORAGE_SCOPE','parameters.json'),
('Q24','How do we avoid local-only false gains?','Always replay from canonical m0,m1 and fixed capacity through the requested endpoint; do not repair intermediate lanes independently.','VALIDATION_RULE','reference_checks.csv'),
('Q25','What lower bounds are established?','Only scoped linear facts and quartic root upper bounds; no optimal collision-search lower bound.','SCOPED_PROOFS','F04;F07;F10'),
('Q26','How should we calibrate solvers?','Replay published vectors; local root tests match exhaustive p257; native reference uses two independent expressions; no solver campaign claimed.','COMPUTED','reference_checks.csv;sbox_counts.json'),
('Q27','What is the native end-to-end success rate?','Not measured for a collision generator. Diagnostic parity/avalanche checks cannot substitute for it.','OPEN','F12'),
('Q28','Does a reduced result break deployed Zcash?','No such inference: deployed 64 rounds, protocol key/input roles and nullifier composition differ from freely chosen contest fields.','SCOPE','S01;S14'),
('Q29','Do all-round degrees prove hardness?','No. 5^(r+1) is only a formal degree upper bound; coordinate changes already lower the r2 description to degree5.','PROVED_SCOPE','F06'),
('Q30','What was actually newly learned here?','Exact affine first image, quintic coefficients, partial chart across54 windows, silent horizon, derivative trap, native local roots and toy conservation.','PROVED+COMPUTED','findings.csv'),
('Q31','What remains at bedrock?','Verified local algebra and replay. Global multi-round legal fibre laws, every conditional relationship and useful generator costs remain open.','OPEN_GLOBAL','unknowns.csv'),
('Q32','How much of the grid is finished?','64/64 structural cards;4096/4096 indexed cells;2080/2080 forward cells sampled at24 internal interventions each; no global necessity-completion percentage asserted.','COUNTED_COVERAGE','results.json'),
]
crosswalk=[dict(question_id=a,prior_question=b,poseidon_answer=c,status=d,evidence=e,source_url=url['S04']) for a,b,c,d,e in crosswalk];writecsv('question_crosswalk.csv',crosswalk)
unknowns=[
('U01','Critical','Live registration and cost rule','Obtain the activated organizer profile and settled field-operation model.','An unmerged proposal is not a live scoring contract.','SOURCE_PENDING'),
('U02','High','Native two-round fibres','Count root multiplicities of the quintic over the legal input law; retain zero-root cases and timing.','Degree5 and a5-root bound are not exact whole-field counts.','OPEN'),
('U03','High','Partial chart legal intersection','Characterize the p^2 valid triples inside the p^3 internal chart using the actual preceding full rounds.','The inverse chart alone does not buy controllable state bits.','OPEN'),
('U04','High','Nontrivial invariant families','Seek coordinated legal changes preserving useful output relations; separate exact finite relations from Jacobian kernels.','Two-step silent direction is neither a global neutral family nor a three-round impossibility for other forms.','OPEN'),
('U05','High','Conditional per-round counts','Measure or count propagated populations, not independent local S-box histograms.','No local differential multiplication as an attack exponent.','OPEN'),
('U06','High','Output-only event alternatives','Describe legal equal-lane0 output families without imposing equal hidden lanes.','Whole-state merger is impossible, but projected collisions may exist.','OPEN'),
('U07','Medium','Genuine route signature','Predefine features and a target with operational meaning; split by independent input batches and compare equal total work.','This pass tests output LSB only; 2048 samples cannot detect a 2^-127 event.','OPEN'),
('U08','Medium','Discarded-pair native distribution','Define an actually attainable proposal stream and null model before recording residuals.','Toy collision histograms are not native near-hit evidence.','OPEN'),
('U09','High','Field arithmetic pricing','Meter modular multiplication, square roots, inversion, loads, canonical encoding and batch costs under the chosen model.','377 field multiplications for elementary root5 exponentiation are not free and not CPU word ops.','OPEN'),
('U10','Medium','Broader parameter variants','Keep RF8/RP-n exploration separate from prefixes of RF8/RP56.','A different schedule changes the mathematical target.','OPEN_SEPARATE_TARGET'),
('U11','Medium','Literature full-text audit','Read paper definitions, parameters, proofs, code, and errata for matched targets; landing abstracts are not enough.','No latest world-best Orchard collision complexity established here.','OPEN'),
('U12','Medium','Proof certificate formalization','Export field identities and ranks to a small trusted checker or formal system.','This pass supplies replayable integers and proofs in prose, not a Lean certificate.','OPEN'),
]
unknowns=[dict(id=a,priority=b,topic=c,next_obligation=d,limitation=e,status=f,source_url=url['S04']) for a,b,c,d,e,f in unknowns];writecsv('unknowns.csv',unknowns)
assumptions=[
('A01','32-byte output means 128-bit birthday','Wrong alphabet: p is about 2^254; nominal birthday127.','RESOLVED','encoding_bit_baseline.csv'),
('A02','One or two rounds exercise partial-round weakness','False: both are leading full rounds.','RESOLVED','round_cards.csv'),
('A03','Re-seed constants for reduced RF/RP','Different hash: use fixed deployed constants and truncate.','RESOLVED','parameters.json'),
('A04','A pair can merge in the whole state as in SHA','False for this same-capacity permutation input: output projection matters.','RESOLVED','linear_certificates.json'),
('A05','Partial-round untouched lanes are free forever','False for exact active-input avoidance; rank horizon3. Other relations not excluded.','SCOPED_RESOLVED','partial_window_charts.csv'),
('A06','Zero Jacobian direction is a neutral family','False for finite changes at S-box zero; fifth-order change survives.','RESOLVED','derivative_trap.csv'),
('A07','A chart with3 parameters grants3 controllable words','False: onlyp^2 chart triples are legal, out ofp^3.','RESOLVED','extra_results.json'),
('A08','Product of local roots/p gives total success','Unsupported without joint conditional law.','NOT_ALLOWED_AS_INFERENCE','sbox_counts.json'),
('A09','No output-parity signal means no useful signature','False inference: limited diagnostic, not a collision-utility screen.','OPEN','signature_screen.csv'),
('A10','Two-round raw degree25 is the simplest equation','False: bijective input power coordinates give quintic degree5.','RESOLVED','two_round_quintic_coefficients.csv'),
('A11','Cheap circuit arithmetic means cheap CPU arithmetic','No universal conversion; record both measurements and pricing.','OPEN_PRICING','benchmark.csv'),
('A12','Full-state count or toy result is a mainnet break','False transfer of goal/field/rounds/domain.','RESOLVED_SCOPE','toy_config.json'),
('A13','An indexed cell is a completely proved cell','False: explicitly separate structural,sampled,localexact,globalopen.','RESOLVED_SCOPE','round_pair_grid.csv'),
('A14','The same partial chart ignores absolute constants','Constants enter the affine shifts and must be retained.','RESOLVED','partial_window_charts.csv'),
]
writecsv('assumption_audit.csv',[dict(id=a,assumption=b,finding=c,status=d,evidence=e,source_url=url['S04']) for a,b,c,d,e in assumptions])
# Meaningful row dossiers, each with native observation, equations and separate scope.
cards=readcsv('round_cards.csv');sens=readcsv('legal_message_sensitivity.csv');toy=readcsv('toy_full_input_counts.csv')
for card,obs,small in zip(cards,sens,toy):
 i=int(card['round_index']);isfull=card['zone']!='partial';act='all three lanes' if isfull else 'lane 0 only'
 text=f'''# Round {i:02d} — deployment round {i+1}

**Zone:** {card['zone']}. **S-box:** {act}. **Fresh legal message choices here:** zero.

## Definition and local algebra
Let s be the input state. Add the three constants c[{i}]. Apply z -> z^5 to {act}; then multiply by the pinned MDS. All arithmetic is in Fp, not XOR arithmetic.

Constants (canonical big-endian display, NOT serialized message order):
```
{chr(10).join(card['round_constants'].split(';'))}
```
The exact local paired rule is delta_out = M * d, where d[j] = (s[j]+c[j]+delta[j])^5 - (s[j]+c[j])^5 for active lanes, and d[j]=delta[j] for inactive lanes.

Whole-state inverse: apply M^-1, the inverse power d=5^-1 mod(p-1) on active lanes, then subtract the constants. The local state inverse is unique. A digest-lane inverse is a different problem.

## Interactions
All three previous state coordinates enter each post-MDS coordinate. This is immediate structural dependence, not a proof that every finite perturbation changes every coordinate. Earlier-round state is not an independently editable legal message input. Future-row interventions cannot alter the stored past, but future constraints can constrain earlier values.

{('This full round has no nonzero S-box-avoiding difference on all three active lanes. That does not exclude output-only cancellations.' if isfull else 'For consecutive partial rounds, exact active-input equality leaves dimension 2 for one round, 1 for two, and 0 for three. This is the O=[e0;e0 M;e0 M^2] rank result, not a ban on other differential families.')}

## Recorded native diagnostic
{obs['samples']} legal-message pairs with m0 -> m0+1 modp, m1 and capacity fixed. Output-lane change counts: {obs['changed_lane0']}, {obs['changed_lane1']}, {obs['changed_lane2']}. Total XOR popcount across all samples and3 words: {obs['xor_popcount_sum']}. No collision probability inferred. See all512 limited feature tests in signature_screen.csv.

The row's full-state inverse was checked on16 independent internal states. A singular-derivative finite-change counterexample was checked at this row. These internal samples do not assert legal-input reachability.

## Recorded exhaustive toy diagnostic
Different field p=257 and toy MDS/capacity: {small['inputs']} complete inputs, {small['distinct_full_states']} distinct full states, {small['distinct_digest_values']} digest values. Exact unordered projected collisions {small['unordered_collisions']}; noncollisions {small['unordered_noncollisions']}; total {small['unordered_pairs']}. This does not estimate native-field rates.

## Arithmetic ledger
{card['field_additions']} additions + {card['field_multiplications']} multiplications = {card['field_ops_total']} field arithmetic operations for full-state evaluation. Cumulative through this row: {card['cumulative_ops']}. Counts omit encoding,control,loads and representation costs and do not constitute a contest score.

Formal polynomial degree upper bound: 5^{i+1}. This is neither exact minimal degree nor a work bound.

## Open obligations
Global legal-input fibre counts, operationally useful conditional signature, interactions under an actual nonuniform proposal law, and costed exact end-to-end generator. This row is indexed and locally tested, not declared completely solved.

Sources: {url['S02']} ; {url['S04']}. Evidence: data/round_cards.csv, data/round_pair_grid.csv, data/legal_message_sensitivity.csv, data/toy_full_input_counts.csv.
'''
 (B/'round_cards'/f'round_{i:02d}.md').write_text(text)

reference=f'''# Reference card — Orchard Poseidon, pinned research atlas

Date: 2026-10-12. Target proposal: HashSmash PR923, head01f736268b7086d97f38837d343d63a81bf31649. The retrieved PR is open/unmerged and does not register Yukon tracks. A live UI change must be checked against its actual deployed profile before filing.

## Exact identity
- Pallas **base** prime: `{P:#x}`.
- State3, rate2, capacity1; S-box exponent5.
- Deployment RF8/RP56: full round indices0..3 and60..63; partial4..59.
- Proposed tracks prefix1/prefix2; both are full-round prefixes.
- Add constants -> S-box -> MDS. No fresh message injection between rounds.
- Input exactly64 bytes: m0,m1 each32-byte **little-endian canonical** integer less thanp.
- Initial state `[m0,m1,{CAP}]` = `[m0,m1,2^65]`.
- Output state lane0,32-byte little-endian canonical field encoding.
- Reject x+p encodings and wrong lengths. No extra padding block at ConstantLength<2>.
- Constants are always generated for RF8/RP56, never for the truncated round count.
- Difference convention throughout: delta = second value minus first modulo p, not XOR.
- Matrix multiplies a column vector from the left.

## Validated here
11 hash vectors +3 permutation vectors;1024 round inversions;1024 independent formula replays;19 nonzero MDS minors;432 partial chart identities;2048 low-round chart identities. Scope and counts are in data/results.json and reports/RESEARCH_REPORT.md.

## Never transfer these assumptions
SHA parity ranks, SHA/BLAKE operation-unit prices, free intermediate inputs, independent per-round probabilities, an alleged complete-state merger, or native rates inferred from p257 experiments.

## Evidence labels
PROVED = shown algebraically with stated domain. COMPUTED_EXACT = exact finite calculation in the named field or finite set. SAMPLED = finite diagnostic only. EXACT_TOY = exhaustive different small field. SOURCE = source claim not newly reproduced. OPEN = no result. Neither local proof nor an indexed grid cell means global attack optimality.

Sources: {url['S01']} ; {url['S02']} ; {url['S04']}.
'''
(B/'REFERENCE_CARD.md').write_text(reference)
bench_data=readcsv('benchmark.csv')
report=f'''# Orchard Poseidon: round-interaction research atlas

## Result and scope
This package transfers the **questions, audit discipline, grid format and experiment layers**, not the SHA/BLAKE numerical conclusions. It contains64 round dossiers,4096 directed round-pair records, exact native field identities, native finite tests, a deliberately separate exhaustive small-field experiment, cost ledgers, literature/source provenance, and an explicit list of unfinished mathematical questions.

It is not merely a list of tasks: the native tests and exact algebra below were run in this session. It is also **not a complete cryptanalysis of64 rounds**, an accepted score, a native collision campaign, or a claim about funds/transactions. No omitted question is silently labeled resolved.

## 1. Which contest target was actually retrieved?
The public addition is HashSmash PR923, head `01f736268b7086d97f38837d343d63a81bf31649`. The connector reports **open, unmerged**. Its text says the targets are locally defined but not registered in Yukon and require organizer baselines; the field-specific cost rule is an organizer decision still open. The user's UI may have moved ahead of this source snapshot. All contest-facing conclusions here are conditional on the pinned proposal, not a claim to have verified current live ranking. [S01]

The proposal uses Orchard's P128Pow5T3 over the Pallas base field, three state elements, exponent5, rate2 and one capacity element. Exactly two canonical field elements form the message, with capacity2^65. There are64 deployed rounds:4full,56partial,4full. A full round applies the fifth power to all three coordinates; a partial round only to coordinate0. The proposed one- and two-round targets are **the first one and two full rounds**, keeping deployed constants. [S02-S04]

The canonical input count is exactly p^2 and output alphabet size isp. Since p is just above2^254, the generic birthday reference is approximately2^127. The32-byte encoding does not give2^256 output values. This baseline is not an estimate of resistance at one or two rounds. [S01-S04]

Orchard's production `prf_nf(nk,rho)` calls the full parameter set in a ConstantLength<2> mode. A contest with both field inputs freely chosen is not the same goal as compromising that keyed protocol use. [S14]

## 2. The row model
Number every deployed round0..63. For roundr and state s_r in Fp^3, let z_r=s_r+c_r. Let f_r fifth-power the active coordinate(s), leaving other coordinates unchanged. Then

    s_(r+1) = M f_r(s_r+c_r).

For a paired state with additive difference Delta, the exact differential update is

    Delta_out = M D_r(s_r+c_r,Delta),

where active D_j=(z_j+Delta_j)^5-z_j^5 and inactive D_j=Delta_j.

This replaces the SHA carry/XOR/selector grid with a **prime-field addition, power and linear-mixing grid**. Machine multiplication carries matter for implementation cost, but they are not the intrinsic differential-coordinate system of this primitive. A single independent field equation under a uniform law costs log2(p), about254bits, not one Boolean bit. Dependence and distributions still must be proved before applying that cost.

Every round uses all three incoming coordinates through M. The pair grid records direct and transitive structural reach separately from sampled finite changes. Its upper triangle has2080 forward cells,24 internal interventions per cell; its lower triangle has2016 no-forward-causal-path cells. Those lower cells can still participate in **backward constraint implications**. Neither triangular entry is an optimality or necessity certificate.

## 3. PROVED: full-state merging is the wrong endpoint
The calculation gcd(5,p-1)=1 gives a unique fifth root for every field value. The inverse exponent is

    d = {ROOT5:#x}.

All19 square minors of M are nonzero, so M is invertible and has branch number4. Undo M, apply d to active coordinates, then subtract c_r to invert a round. This was checked on1024 independently chosen native states. [S03-S06, local certificate]

Consequently every prefix permutes Fp^3, and the p^2 legal initial states remain distinct **as full states** at every round. Two distinct legal inputs can collide only because the hash exposes coordinate0 and discards coordinates1,2. Requiring all three outputs equal would remove every nontrivial candidate. Conversely a coordinate0 equality at an intermediate row is not preserved for free by later nonlinear rounds.

The full-state inverse is not automatically cheap: ordinary left-to-right exponentiation for d uses253 squarings and124 further multiplications,377 field multiplications per active lane, excluding control/load costs. It is exact, not a performance record. A primitive inverse is not a hash-preimage algorithm because two output coordinates remain unknown.

## 4. PROVED and COMPUTED: the first-round image is an affine plane
Put

    X=(m0+c[0,0])^5,
    Y=(m1+c[0,1])^5,
    Z=(2^65+c[0,2])^5.

X,Y independently range over Fp because the fifth power is bijective; Z is fixed. Thus s_1=M(X,Y,Z), and

    row2(M^-1) * s_1 = Z.

There are exactlyp^2 legal states on this affine plane. Its coordinate0 is the nonconstant linear form

    H1=M00 X + M01 Y + M02 Z.

Because M01 is nonzero, each digest has exactlyp canonical input messages. For two distinct uniformly selected messages the one-round collision probability is exactly1/(p+1). This is an exact counting statement about the whole native input domain, derived without enumeratingp^2 inputs. It is not a claim that generic sampling is an optimal way to use the formula.

## 5. PROVED and COMPUTED: two rounds have a quintic coordinate description
Using the same X,Y and k_j=M_j2 Z+c[1,j], the second-round digest is exactly

    H2(X,Y) = sum_(j=0..2) M_0j (M_j0 X + M_j1 Y + k_j)^5.

In original message coordinates the straightforward composition has degree up to25. In these **bijective power coordinates** it is degree5. This is a change of coordinates, not omission of the first round. All21 bivariate monomial coefficients were produced in the native field and saved. Both X^5 andY^5 coefficients are nonzero.

For fixed X and target output, this is a genuine quintic inY with at most5roots. The complete native two-round fibre histogram is **OPEN**. Averaged over allp possible digests the number of inputs is exactlyp by counting, but that average does not prove that every digest is attained or equally frequent. No solver runtime or improved attack exponent is inferred from the small degree.

The algebraic identity was checked on2048 independent legal messages against the full first-two-round reference. This directly addresses the previous project's request to test a different perspective rather than keep multiplying the apparent degree.

## 6. PROVED and COMPUTED: partial rounds have a precise silent horizon
For a partial round write e0=(1,0,0)^T, v=M e0, b_r=M c_r, and n(x)=x^5-x. Then

    s_(r+1)=M s_r+b_r+v n(s_r[0]+c_r[0]).

If paired inputs agree on coordinate0 before the S-box, the nonlinear differences vanish in that layer and their state difference advances by M. To avoid the active S-box for k consecutive partial rounds, Delta must satisfy

    e0^T M^j Delta=0 for j=0..k-1.

The native observability matrix O=[e0^T; e0^T M; e0^T M^2] has rank3. Exact remaining dimensions are2for one constraint,1for two,0for three. The supplied vector(0,M02,-M01) spans the two-constraint kernel and fails the third constraint.

That proves **this exact S-box-avoidance mechanism cannot remain nontrivial through three successive partial rounds**. It does not prove no other differential family, invariant, or nonlinear relation works. There are432 native two-step checks across all54 three-partial-round windows.

## 7. PROVED: three active values are coordinates, not three free message words
Let q0=s_r[0], q1=s_(r+1)[0], q2=s_(r+2)[0] in an all-partial three-round window. Set n0=n(q0+c_r0), n1=n(q1+c_(r+1),0). Then

    k1=(b_r)_0+v_0 n0
    k2=(M b_r)_0+(M v)_0 n0+(b_(r+1))_0+v_0 n1
    O s_r=(q0, q1-k1, q2-k2)^T.

Since O is invertible, every(q0,q1,q2) has exactly one unrestricted internal state. The reconstruction was checked432times,8times at each of54windows.

**The legality obstruction is exact:** onlyp^2 of these p^3 triples lie on the image of legal canonical messages. Uniformly selecting unrestricted triples gives legal membership probability1/p. This is cardinality, not a conjectured random-map heuristic. A useful new generator would have to traverse that legal subset cheaply; the chart alone does not do so.

This is the direct Poseidon analogue of the SHA fixed-CV correction: a convenient internal coordinate must not be counted as a freely editable input.

## 8. PROVED and COMPUTED: exact local differential counts via a quartic
For nonzero additive difference delta, set beta=eta/delta^5, z=x/delta+1/2, y=z^2. Then

    (x+delta)^5-x^5=eta
    <=> 80y^2+40y+1-16beta=0.

The discriminant is1280+5120beta. Solve the quadratic fory, then requirey to be a square and recoverz andx. The implementation removes duplicates, including discriminant-zero and square-root-zero cases. There are at most4preimages. Roots pair under x -> -x-delta; a repeated symmetric point can give an odd number of distinct roots. Eta0 has no root for nonzerodelta because fifth power is bijective.

All65,792(delta,eta) pairs for p257, delta nonzero, were compared against brute force. There were zero mismatches. The exhaustive toy root-count histogram is0roots:40,960;2roots:16,640;3roots:256;4roots:7,936. Separately256 native delta/eta cases were exactly solved and each root replayed, half random targets and half known-image targets. The native table is a selected finite set, not an exhaustive native DDT.

These local root counts do not multiply into an end-to-end success rate unless the conditional input law at each nonlinear layer supports that multiplication. The same absolute state is mixed and reused; layers are not independent lotteries by default.

## 9. PROVED and COMPUTED: zero derivative can be a false freedom
At an active input z=0, derivative5z^4=0. A differential/Jacobian calculation can therefore show an apparent direction of zero first-order response. Yet for a finite nonzero displacementt, (0+t)^5-0=t^5 is nonzero. Since M's column entries are nonzero, this displacement changes all three mixed coordinates.

One such native counterexample is recorded at every round index:64checks. The whole round remains a permutation despite a singular derivative at the chosen point. Thus a Jacobian kernel is not a certificate of an exact finite neutral subspace. The test uses internal states and does not assert that the chosen singular state is cheaply reached by legal messages.

## 10. SAMPLED: native sensitivity and a deliberately limited signature screen
2048 uniformly sampled canonical message pairs were evaluated with m0 incremented by1modp, keeping m1 and capacity fixed. Every prefix0..63 is recorded:262,144 native round transitions. This measures finite sensitivity from legal inputs, not collision-search success.

Eight features chosen in code before the sample were input bits0/8, input popcount parities, sum parity, and m0<m1. They were tested against output-coordinate0's canonical least-significant bit for every prefix. Across512tests, **zero** had a Bonferroni-adjusted normal-approximation p-value below.05. This is not a proof of no useful signature; it neither tests an actual conditioned attack population nor has power to observe a2^-127 event. All raw group sizes, counts, p-values and seeds are in signature_screen.csv.

Uniform-field binary encodings need the right null model: p is a255-bit integer just above2^254. Bit255 is alwayszero; bit254 is extremely rare. Independent uniform field words have expected XOR Hamming weight approximately127, not128. Per-bit exact numerator and denominator are saved. Observed low activity in those high encoding bits is not a cryptanalytic bias.

## 11. EXACT TOY: collision-versus-trash conservation on all inputs
A separatep257 model uses width3,exponent5,the same full/partial schedule,nativeconstants reduced modulo257,a different small Cauchy MDS,and capacity2. All66,049message inputs were advanced through all64rounds:4,227,136state updates. All19toy MDS minors are nonzero and every round retains66,049distinct full states.

Each row partitions the2,181,202,176unordered distinct message pairs into projected collisions and noncollisions. The counts add exactly on all64rows. At the first round all257digest buckets have257members; at the second their sizes range204..493. Those observations show why generator-dependent distributions must be measured rather than presumed; **they are not native Orchard probability estimates**.

The toy data are histogram counts, not a deployed collision submission, and use a plainly separate configuration file. No native failed-pair collection or second-stage correction has been claimed.

## 12. Cost ledger: keep arithmetic, implementation time and scores separate
A straightforward full-state round needs3round-constant additions,6MDS accumulation additions,9MDS multiplications,and3multiplications per active fifth-power S-box. Thus fullround=9adds+18muls=27;partial=9adds+12muls=21. All64rounds total576adds+816muls=1392. These reproduce the proposal's reference arithmetic convention; the proposal itself says the final field-operation scoring policy needs organizer resolution. [S01,S09]

If only the endpoint digest is requested and constants are precomputed, the first-round formula uses12online field operations(4adds+8muls),with5precomputeops. The two-round expression uses34(10adds+24muls),with10precomputeops. These counts are **not emitted contest scores**: they exclude loads,branches,encoding,initialization and operation-type weights. They are endpoint-specialized arithmetic opportunities, not a collision-search speedup.

Benchmarks were run with Python3.13.5 arbitrary-precision modular integers, one process, AMD EPYC9V74. Each entry uses512repetitions after parameter initialization. Example:~{float(bench_data[0]['evals_per_cpu_second']):,.0f} one-round permutations/s, ~{float(bench_data[1]['evals_per_cpu_second']):,.0f} two-round/s, ~{float(bench_data[-1]['evals_per_cpu_second']):,.0f} full64-round/s in this environment. Millisecond timings are noisy; seven actual CPU/wall records are supplied. Do not use them as optimized C/GPU performance or convert them to a cryptanalytic success exponent.

Canonical storage alone is96bytes per state and6,432bytes for192constants plus9MDSentries. A backward table adds288bytes for M^-1. Language objects and any search lists have separate memory costs. Nothing here establishes a low-memory collision method or charges protocol operations.

## 13. Literature: what was read and what was not
The official implementation, generator and vectors supply the concrete instance. The Poseidon design paper, HADES algebraic analysis(2023/537), and Graeffe/CICO challenge analysis(2025/950) were identified and their landing abstracts reviewed. **Their full proofs and implementations were not audited in this pass.** Different width,field,round schedule,security level,CICO/preimage/collision goals and memory model prevent direct transfer of their claimed exponents. The2024/310 record is withdrawn and is not used as support. [S10-S13]

No worldwide best full-round Orchard collision result is asserted. Likewise a reference's nominal127 is not a tested reduced-round strength.

## 14. What has and has not reached bedrock
Completed: exact target identity for the proposal;64structural cards;4096indexed paircells;19nativeMDSminors;whole-state invertibility;first-roundfibre law;two-roundquinticidentity;partialobservabilityhorizon;54internalcoordinatecharts;localquarticrootlaw;finite-change derivativecounterexample;recordednativechecks;all-inputsmall-fieldbookkeeping.

Not completed: exact native multi-round digest fibres; full joint differential population; legality-preserving multi-round inverse generator; useful route selection on an attack population; proof that no other useful interactions exist; or fully priced accepted collision algorithms. The workbook does not invent an overall percentage of mathematical understanding. Every open obligation is a row in unknowns.csv.

The highest-information next cells are the **legal subset inside the partial chart**, **two-round projected fibre multiplicities**, and **conditional rather than marginal nonlinear constraints**. This is a test priority, not a claim that other rows lack value. All64rows remain in the atlas, including the leading and trailing full rounds and the input/output boundary.

## Reproduction
From the package root, run `python check_all.py`. Python's standard library is sufficient for native arithmetic; the full toy enumeration also needs a C11compiler called `cc`. Each computation is deterministic apart from timing. The code regenerates parameters instead of fetching a network dependency. The14test-vector copies are local transcriptions with their own manifest hashes, not an authenticated upstream checkout. No workbook library is needed to replay the mathematics.

## Sources
'''
for s in sources:report+=f"\n[{s['source_id']}] {s['title']}\n{s['url']}\nScope: {s['scope']}. {s['note']}\n"
(R/'RESEARCH_REPORT.md').write_text(report)
readme='''# Poseidon (Orchard) research atlas

Start with reports/RESEARCH_REPORT.md and REFERENCE_CARD.md. The workbook is a searchable companion; data/*.csv and *.json are the agent-facing feed. Each of64rounds also has its own Markdown dossier.

## Reproduce
```
python check_all.py
```
Requires Python3.10+ and a C11compiler `cc` for the exhaustive toy. No wallet,network,APIkey or external dataset is required. The math scripts use only Python standard libraries. Workbook generation uses artifact_tool separately and is not required for reproduction.

`analyze.py`: official vector transcriptions, inverses, MDS minors, partial chart, local root counts, native sensitivity/signatures, pairgrid, benchmarks.
`low_round_chart.py`: native bivariate-quintic coefficients and2048exact evaluations.
`build_toy.py`: compiles and runs all-input p257model, explicitly not nativeOrchard.
`extra_checks.py`: derivative trap, toyminors, exact bookkeeping, legal-triple cardinality.
`build_documents.py`: reproducible reports,64dossiers,sourcecatalog,questioncrosswalk,findings,unknowns.

## Scope
The public proposal snapshot is PR923/head01f736268b7086d97f38837d343d63a81bf31649; it was open/unmerged and did not register a Yukon lane when queried. Do not submit a score based solely on its provisional arithmetic weights. No native collision campaign, complete cryptanalysis or productionZcashbreak is claimed.

Native-exact, sampled, toy-exact and source-only fields are separate. Structural coverage is not a proof of all interactions. See the report for exact population definitions and the sign conventions: additive field differences, not XOR masks.

`MANIFEST.json` and `SHA256SUMS.txt` pin local file bytes. Re-running changes timing data and documentation hashes; this is expected. Preserve the original directory when comparing replay results.
'''
(B/'README.md').write_text(readme)

# Improve narrative typography without touching formulas, code fences or URLs.
import re
for path in [B/'README.md',B/'REFERENCE_CARD.md',R/'RESEARCH_REPORT.md',*sorted((B/'round_cards').glob('*.md'))]:
    output=[];code=False
    for line in path.read_text().splitlines():
        if line.startswith('```'):code=not code
        if not code and not line.startswith('    ') and 'http' not in line:
            line=line.replace('Poseidon2','POSEIDONTWO')
            line=re.sub(r'\b([a-zA-Z]{3,})(\d+)',r'\1 \2',line)
            line=re.sub(r'\b(of|on|to|at|by|in|is)(\d+)',r'\1 \2',line)
            line=re.sub(r'(\d+)([a-zA-Z]{2,})\b',r'\1 \2',line)
            line=line.replace('POSEIDONTWO','Poseidon2').replace('log 2(', 'log2(')
            for a,b in {'roundr':'round r','andY':'and Y','inY':'in Y','allp':'all p','enumeratingp':'enumerating p','nonzerodelta':'nonzero delta','Eachof':'Each of','4roots':'4 roots','atp257':'at p=257','forp257':'for p=257','p257model':'p=257 model','p257two':'p=257 two','SHA256':'SHA-256','Zcashbreak':'Zcash break','inputdomain':'input domain','allunorderedpairs':'all unordered pairs','fullstate':'full state','fixedcap':'fixed cap','stateupdates':'state updates'}.items():line=line.replace(a,b)
            for a,b in {'all64':'all 64','all19':'all 19','all54':'all 54','all21':'all 21','all66':'all 66','All19':'All 19','All21':'All 21','All65':'All 65','All64':'All 64','All66':'All 66','onlyp^2':'only p^2','exactlyp^2':'exactly p^2','exactlyp':'exactly p','isp.':'is p.','dimension2':'dimension 2','dimension3':'dimension 3','dimension1':'dimension 1','beforethe':'before the','eachrow':'each row','whole64':'whole 64'}.items():line=line.replace(a,b)
        output.append(line)
    path.write_text('\n'.join(output)+'\n')
