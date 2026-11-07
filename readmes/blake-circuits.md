# BLAKE3 bit-sliced circuits & walk variants

Part of the HASH$CyberAxe Toolkit. Snapshot: November 5, 2026.

## What it does

Builds and inspects packed/bit-sliced BLAKE3 kernels, distinguished-point walks and recovery layouts across retained editions.

## What this adds to the workflow

Before: Comparing abstract gate totals without matching the primitive basis, stored program and recovery layout.

What we added: Makes lane representation, gate basis, code size, endpoint storage and recovery work inspectable together. The guides preserve upstream contributor credits.

## Where to get it

- Complete source and documentation archive: `downloads/HASH-CyberAxe-toolkit.zip`
- Full source inventory: `downloads/toolkit-index.csv`

## Components, versions and instructions

### BLAKE3 bit-sliced rho: 256 lanes, checked register assignments and duplicate-count semantics

- Original path: `research/checks_1015/pa_src/b3r3bs_pkg/experiments/bsrho.py`
- SHA-256: `b8341c83cfbdfd05cc52bd99d8a5e97ac46c0e008549082da4be5d764b917bfa`
- Usage guide: `guide.html?id=22c65db878283f2de450`
- Source/download: `record.html?id=22c65db878283f2de450`
- Detailed README in the archive: `guides/22c65db878283f2de450.md`
- Finite test report: `verification/bitslice-bounded-runtime.json`

### BLAKE3 select-gate walk: preserve collisions, change the implementation

- Original path: `research/blake3_r3/bsel/pkg/blake3/experiments/bsrho.py`
- SHA-256: `b72dd6a3705e844959fdff8ed4f4805484f3d24ae068fd6a9f06992d6cd8a8c1`
- Usage guide: `guide.html?id=1137947e216e9481729b`
- Source/download: `record.html?id=1137947e216e9481729b`
- Detailed README in the archive: `guides/1137947e216e9481729b.md`
- Finite test report: `verification/bsel-bounded-runtime.json`

### BLAKE3 compact pivot edition: three rounds despite the stale comments

- Original path: `research/blake3_r3/compact_u5b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `354198c3c1a78f4900262a54ad9b4b4ab2d154a24774d8c12f48249620976c23`
- Usage guide: `guide.html?id=e8b25ac96c68ac131224`
- Source/download: `record.html?id=e8b25ac96c68ac131224`
- Detailed README in the archive: `guides/e8b25ac96c68ac131224.md`
- Finite test report: `verification/compact-u5b-bounded-runtime.json`

### BLAKE3 B8: reuse a main round body, count every execution

- Original path: `research/blake3_r7/b8/pkg/blake3/experiments/bsrho.py`
- SHA-256: `0ac49958df4b5127a999239c9323c69fda51ca5ca10aa03fe6240b1f9b0b7648`
- Usage guide: `guide.html?id=06395aac029fb10f66d7`
- Source/download: `record.html?id=06395aac029fb10f66d7`
- Detailed README in the archive: `guides/06395aac029fb10f66d7.md`
- Finite test report: `verification/b8r7-bounded-runtime.json`

### BLAKE3 original five-round compact edition: check both capacity limits

- Original path: `research/blake3_r5/compact/pre/pkg/blake3/experiments/bsrho.py`
- SHA-256: `e75d5ad818fb012736b4b5761608f1147ba430f15095535cd8f58214fda251ed`
- Usage guide: `guide.html?id=0b41aa7c1718964a658b`
- Source/download: `record.html?id=0b41aa7c1718964a658b`
- Detailed README in the archive: `guides/0b41aa7c1718964a658b.md`
- Finite test report: `verification/compact-r5-bounded-runtime.json`

### BLAKE3 original compact edition: small gates, two capacity boundaries

- Original path: `research/blake3_r4/compact/pkg/blake3/experiments/bsrho.py`
- SHA-256: `18fab9b59af2c88e4c3966bc6ab785e14d6cdea735e34875432504ae76942a0a`
- Usage guide: `guide.html?id=164c76bee418b582ae75`
- Source/download: `record.html?id=164c76bee418b582ae75`
- Detailed README in the archive: `guides/164c76bee418b582ae75.md`
- Finite test report: `verification/compact-r4-bounded-runtime.json`

### BLAKE3 seven-round select edition: smaller records, different key bound

- Original path: `research/blake3_r7/bsel/pkg/blake3/experiments/bsrho.py`
- SHA-256: `0c2bdeabc4f021b6054dc7643660bb55e6849c8c6731586862b50d7f55471af6`
- Usage guide: `guide.html?id=20044f2a3beb5c0dd0ac`
- Source/download: `record.html?id=20044f2a3beb5c0dd0ac`
- Detailed README in the archive: `guides/20044f2a3beb5c0dd0ac.md`
- Finite test report: `verification/bsel-r7-bounded-runtime.json`

### BLAKE3 B4B/B4C: save endpoint space, recompute trail lengths

- Original path: `research/blake3_r4/b4c/pkg/blake3/experiments/bsrho.py`
- SHA-256: `9cc4c43839337a10ac5beae5d8ca907ee16496d028741f97ff652f7dae627013`
- Usage guide: `guide.html?id=228d7c3f58e4800aedf6`
- Source/download: `record.html?id=228d7c3f58e4800aedf6`
- Detailed README in the archive: `guides/228d7c3f58e4800aedf6.md`
- Finite test report: `verification/b4b-r4-bounded-runtime.json`

### BLAKE3 bit-sliced rho: 256 lanes, checked register assignments and duplicate-count semantics

- Original path: `research/blake3_r3/bitslice/pkg/blake3/experiments/bsrho.py`
- SHA-256: `b8341c83cfbdfd05cc52bd99d8a5e97ac46c0e008549082da4be5d764b917bfa`
- Usage guide: `guide.html?id=23a153752f061cfbb14c`
- Source/download: `record.html?id=23a153752f061cfbb14c`
- Detailed README in the archive: `guides/23a153752f061cfbb14c.md`
- Finite test report: `verification/bitslice-bounded-runtime.json`

### BLAKE3 B8r5: reuse a main round body, count every execution

- Original path: `research/blake3_r5/b8r5/pkg/blake3/experiments/bsrho.py`
- SHA-256: `7d42a65e80f80f6340af5c2f45d5261346da341133dcfd482d78a39d7a065738`
- Usage guide: `guide.html?id=34ce34cc1b5876e63fbb`
- Source/download: `record.html?id=34ce34cc1b5876e63fbb`
- Detailed README in the archive: `guides/34ce34cc1b5876e63fbb.md`
- Finite test report: `verification/b8r5-bounded-runtime.json`

### BLAKE3 five-round select edition: count the primitive before the speedup

- Original path: `research/blake3_r5/bsel/pkg/blake3/experiments/bsrho.py`
- SHA-256: `fd4098fd6069771a9da1b9353dbfec18c4774ac284f4a792385236f2c1f8ca4c`
- Usage guide: `guide.html?id=386ed7e9ca526013a4d7`
- Source/download: `record.html?id=386ed7e9ca526013a4d7`
- Detailed README in the archive: `guides/386ed7e9ca526013a4d7.md`
- Finite test report: `verification/bsel-r5-bounded-runtime.json`

### BLAKE3 six-round select edition: compare the same operation basis

- Original path: `research/blake3_r6/bsel/pkg/blake3/experiments/bsrho.py`
- SHA-256: `5d7d86dbfa3e2d87216dfcbbf3ca9d48532b5c4cce1b0f873a44dd16aa3eccac`
- Usage guide: `guide.html?id=3d207f1332a2b7623e8f`
- Source/download: `record.html?id=3d207f1332a2b7623e8f`
- Detailed README in the archive: `guides/3d207f1332a2b7623e8f.md`
- Finite test report: `verification/bsel-r6-bounded-runtime.json`

### BLAKE3 B9v4: the same rolled circuit, a different numerical model

- Original path: `research/blake3_r7/b9v4/pkg/blake3/experiments/bsrho.py`
- SHA-256: `5364c8dfa8032e4208178f546430bac16e4a361baee0d348afe5ef98c50ea9ae`
- Usage guide: `guide.html?id=42e8274ab2557778241d`
- Source/download: `record.html?id=42e8274ab2557778241d`
- Detailed README in the archive: `guides/42e8274ab2557778241d.md`
- Finite test report: `verification/b9r7-bounded-runtime.json`

### BLAKE3 B6: six-round arithmetic and the declared memory charge

- Original path: `research/blake3_r6/b6/pkg/blake3/experiments/bsrho.py`
- SHA-256: `5157efa058cb4154f66a20f374eb15c323ea07ad1dc1c5de7193849629b405d6`
- Usage guide: `guide.html?id=45389e750be50a312450`
- Source/download: `record.html?id=45389e750be50a312450`
- Detailed README in the archive: `guides/45389e750be50a312450.md`
- Finite test report: `verification/b6-r6-bounded-runtime.json`

### BLAKE3 original six-round compact edition: two capacity boundaries

- Original path: `research/blake3_r6/compact/pkg/blake3/experiments/bsrho.py`
- SHA-256: `87e8a6b771ffb929c01a17c0e4dd45d3df46e46761766e58c2200e94eab19745`
- Usage guide: `guide.html?id=4c11faabbbcb0cfc8f70`
- Source/download: `record.html?id=4c11faabbbcb0cfc8f70`
- Detailed README in the archive: `guides/4c11faabbbcb0cfc8f70.md`
- Finite test report: `verification/compact-r6-bounded-runtime.json`

### BLAKE3 pivot v2: changing the success model without changing the circuit

- Original path: `research/blake3_r3/pivotv2/pkg/blake3/experiments/bsrho.py`
- SHA-256: `856907a5107369b4e3467029fe1f82b625a2cd54860652b051b23259790fb148`
- Usage guide: `guide.html?id=4de0f2198cb830bb473f`
- Source/download: `record.html?id=4de0f2198cb830bb473f`
- Detailed README in the archive: `guides/4de0f2198cb830bb473f.md`
- Finite test report: `verification/pivotv2-bounded-runtime.json`

### BLAKE3 B6V2: six-round arithmetic and the declared memory charge

- Original path: `research/blake3_r6/b6v2/pkg/blake3/experiments/bsrho.py`
- SHA-256: `1b3626a3423f1dfca2e4d810918c5d3d73be94acd797c1ad6e72a877d904b17c`
- Usage guide: `guide.html?id=52995455b02d365d3663`
- Source/download: `record.html?id=52995455b02d365d3663`
- Detailed README in the archive: `guides/52995455b02d365d3663.md`
- Finite test report: `verification/b6v2-r6-bounded-runtime.json`

### BLAKE3 B9r6: same rolled circuit, revised probability accounting

- Original path: `research/blake3_r6/b9r6/pkg/blake3/experiments/bsrho.py`
- SHA-256: `e0c9ac2a5ca6b3f6274f1f0144a88d917599ad8b6a911b0a25d76fb4078db670`
- Usage guide: `guide.html?id=575f474c263aa6f1cf12`
- Source/download: `record.html?id=575f474c263aa6f1cf12`
- Detailed README in the archive: `guides/575f474c263aa6f1cf12.md`
- Finite test report: `verification/b9r6-bounded-runtime.json`

### BLAKE3 B8r6: reuse a main round body, count every execution

- Original path: `research/blake3_r6/b8r6/pkg/blake3/experiments/bsrho.py`
- SHA-256: `ceab2feac5d439c4463c6b0988e8674666c859cada837c53ac5a2f614ad64caf`
- Usage guide: `guide.html?id=5efe779329222098280f`
- Source/download: `record.html?id=5efe779329222098280f`
- Detailed README in the archive: `guides/5efe779329222098280f.md`
- Finite test report: `verification/b8r6-bounded-runtime.json`

### BLAKE3 B4E: replaying the selected probability calculation

- Original path: `research/blake3_r4/b4e/pkg/blake3/experiments/bsrho.py`
- SHA-256: `a09a22fed3cb0f516cea1eb359485895cfae12c5f55e8e2d7738cd75dc6feee7`
- Usage guide: `guide.html?id=60685f8374071d321a5c`
- Source/download: `record.html?id=60685f8374071d321a5c`
- Detailed README in the archive: `guides/60685f8374071d321a5c.md`
- Finite test report: `verification/b4e-r4-bounded-runtime.json`

### BLAKE3 bitslice3: polarity-search provenance and reuse of setup memory

- Original path: `research/blake3_r3/bitslice3/pkg/blake3/experiments/bsrho.py`
- SHA-256: `ef98cfcd1a51c617b230526f376ef194653cfe9a363ce04a1913c67d0c8d58c7`
- Usage guide: `guide.html?id=6446310cbb1eaf2a685f`
- Source/download: `record.html?id=6446310cbb1eaf2a685f`
- Detailed README in the archive: `guides/6446310cbb1eaf2a685f.md`
- Finite test report: `verification/bitslice3-bounded-runtime.json`

### BLAKE3 B4D: a new loss model is not a new hash kernel

- Original path: `research/blake3_r4/b4d/pkg/blake3/experiments/bsrho.py`
- SHA-256: `603dd4c2959b7d27828b127aa519e8097f15bd7a9c47be3d5325c59d31d5ef4e`
- Usage guide: `guide.html?id=6a173133e4dbf2b856fb`
- Source/download: `record.html?id=6a173133e4dbf2b856fb`
- Detailed README in the archive: `guides/6a173133e4dbf2b856fb.md`
- Finite test report: `verification/b4d-r4-bounded-runtime.json`

### BLAKE3 B5: five rounds and a larger declared memory budget

- Original path: `research/blake3_r5/b5/pkg/blake3/experiments/bsrho.py`
- SHA-256: `e83ab3afb633441517737e4b69c88b1e98f4ebb7d436d506974a272b356b7f4e`
- Usage guide: `guide.html?id=6bf8c2083f36d9cfe6bf`
- Source/download: `record.html?id=6bf8c2083f36d9cfe6bf`
- Detailed README in the archive: `guides/6bf8c2083f36d9cfe6bf.md`
- Finite test report: `verification/b5-r5-bounded-runtime.json`

### BLAKE3 seven-round compact binary edition: preserve the source-specific limits

- Original path: `research/blake3_r7/compact_u5b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `57067ce4d051bc6d2dfbc53a3dc41b353affe4507a01ade2b21aef76705978b7`
- Usage guide: `guide.html?id=7f4fd442dece600dc46b`
- Source/download: `record.html?id=7f4fd442dece600dc46b`
- Detailed README in the archive: `guides/7f4fd442dece600dc46b.md`
- Finite test report: `verification/compact-u5b-r7-bounded-runtime.json`

### BLAKE3 original seven-round compact edition: verify fields and code separately

- Original path: `research/blake3_r7/compact/pre/pkg/blake3/experiments/bsrho.py`
- SHA-256: `d6727ed0a0bd300633f8d51c6f1c3de6009be8c721261f0c71c9a41691730459`
- Usage guide: `guide.html?id=7fee6ced90743ed53280`
- Source/download: `record.html?id=7fee6ced90743ed53280`
- Detailed README in the archive: `guides/7fee6ced90743ed53280.md`
- Finite test report: `verification/compact-r7-bounded-runtime.json`

### BLAKE3 B4F: smaller stored code, more recovery operations

- Original path: `research/blake3_r4/b4f/pkg/blake3/experiments/bsrho.py`
- SHA-256: `0d25cea3ac5bf0cff088b7b89e0e0e71a07b14a5bb3521905691f4ddfe149182`
- Usage guide: `guide.html?id=80eca476224d0ba35ccc`
- Source/download: `record.html?id=80eca476224d0ba35ccc`
- Detailed README in the archive: `guides/80eca476224d0ba35ccc.md`
- Finite test report: `verification/b4f-r4-bounded-runtime.json`

### BLAKE3 b3r3t: numeric trial gates, mixed predicates and counters that reset on halt

- Original path: `research/blake3_r3/b3r3t/pkg/blake3/experiments/rho.py`
- SHA-256: `ce41f4e09ddacc2064f863693e54ad090010e034cb517b37225d2526632e341a`
- Usage guide: `guide.html?id=93a255371dbf33d11183`
- Source/download: `record.html?id=93a255371dbf33d11183`
- Detailed README in the archive: `guides/93a255371dbf33d11183.md`
- Finite test report: `verification/b3r3t-bounded-runtime.json`

### BLAKE3 three-round rho candidate: a 22-bit experiment, packed digest and declared 256-bit budget

- Original path: `research/blake3_r3/candidate_blake3/experiments/rho.py`
- SHA-256: `4a5bc2ef7643dc0c1908ad6a7c248e72154302c91c0daffe340f1f4b8db6680f`
- Usage guide: `guide.html?id=9a8ea92a0d1c21fba40f`
- Source/download: `record.html?id=9a8ea92a0d1c21fba40f`
- Detailed README in the archive: `guides/9a8ea92a0d1c21fba40f.md`
- Finite test report: `verification/candidate-blake3-rho-bounded-runtime.json`

### BLAKE3 B5v2: revise the model without changing the circuit

- Original path: `research/blake3_r5/b5v2/pkg/blake3/experiments/bsrho.py`
- SHA-256: `1781a28188079818b5c74a4af1331f5696f1b9c21d2f3535d63169770a59884a`
- Usage guide: `guide.html?id=9b008d820e5a258e1845`
- Source/download: `record.html?id=9b008d820e5a258e1845`
- Detailed README in the archive: `guides/9b008d820e5a258e1845.md`
- Finite test report: `verification/b5v2-r5-bounded-runtime.json`

### BLAKE3 b3r3lc: charging prefix selection, storing advice and rounding the table

- Original path: `research/blake3_r3/b3r3lc/pkg/blake3/experiments/rho.py`
- SHA-256: `90e3ddb5882413e7022cf54b4dccc29d50cb12337c8c51678fb4651584dd4e8e`
- Usage guide: `guide.html?id=9c85dddedc5b90091a98`
- Source/download: `record.html?id=9c85dddedc5b90091a98`
- Detailed README in the archive: `guides/9c85dddedc5b90091a98.md`
- Finite test report: `verification/b3r3lc-bounded-runtime.json`

### BLAKE3 b3r3lb: a selected first block, a smaller second-block kernel and separate preprocessing

- Original path: `research/blake3_r3/b3r3lb/pkg/blake3/experiments/rho.py`
- SHA-256: `636e841494c0be8567c16eea7a0329b4ae56309acaf76fa656ef96ab7b6901be`
- Usage guide: `guide.html?id=a5910b2c3380999a61ea`
- Source/download: `record.html?id=a5910b2c3380999a61ea`
- Detailed README in the archive: `guides/a5910b2c3380999a61ea.md`
- Finite test report: `verification/b3r3lb-bounded-runtime.json`

### BLAKE3 pivot walk: the same circuit can have a different storage price

- Original path: `research/blake3_r3/pivot1/pkg/blake3/experiments/bsrho.py`
- SHA-256: `4109c3f80a0a25369f7c06fb7d37d86a0c07d917ff66602a0c6e6fe9ab4d5078`
- Usage guide: `guide.html?id=a7ba998ad7abb23c2944`
- Source/download: `record.html?id=a7ba998ad7abb23c2944`
- Detailed README in the archive: `guides/a7ba998ad7abb23c2944.md`
- Finite test report: `verification/pivot1-bounded-runtime.json`

### BLAKE3 original five-round compact edition: check both capacity limits

- Original path: `research/blake3_r5/compact/pkg/blake3/experiments/bsrho.py`
- SHA-256: `e75d5ad818fb012736b4b5761608f1147ba430f15095535cd8f58214fda251ed`
- Usage guide: `guide.html?id=a91cbde7cc5b30dab037`
- Source/download: `record.html?id=a91cbde7cc5b30dab037`
- Detailed README in the archive: `guides/a91cbde7cc5b30dab037.md`
- Finite test report: `verification/compact-r5-bounded-runtime.json`

### BLAKE3 four-round stack: deferred limits need a delay argument

- Original path: `research/blake3_r3/stack1020_r4/pkg/blake3/experiments/bsrho.py`
- SHA-256: `fe6813248f135c5e2166df174a67c4704a62a39fcd9f5ad53ee27917119fa25b`
- Usage guide: `guide.html?id=aeacd0b2b4ee18a40797`
- Source/download: `record.html?id=aeacd0b2b4ee18a40797`
- Detailed README in the archive: `guides/aeacd0b2b4ee18a40797.md`
- Finite test report: `verification/stack1020-r4-bounded-runtime.json`

### BLAKE3 original seven-round compact edition: verify fields and code separately

- Original path: `research/blake3_r7/compact/pkg/blake3/experiments/bsrho.py`
- SHA-256: `d6727ed0a0bd300633f8d51c6f1c3de6009be8c721261f0c71c9a41691730459`
- Usage guide: `guide.html?id=b078520db574cdf35900`
- Source/download: `record.html?id=b078520db574cdf35900`
- Detailed README in the archive: `guides/b078520db574cdf35900.md`
- Finite test report: `verification/compact-r7-bounded-runtime.json`

### BLAKE3 original compact edition: small gates, two capacity boundaries

- Original path: `research/blake3_r4/compact/pre/pkg/blake3/experiments/bsrho.py`
- SHA-256: `18fab9b59af2c88e4c3966bc6ab785e14d6cdea735e34875432504ae76942a0a`
- Usage guide: `guide.html?id=b1ba200612ba458ce0a3`
- Source/download: `record.html?id=b1ba200612ba458ce0a3`
- Detailed README in the archive: `guides/b1ba200612ba458ce0a3.md`
- Finite test report: `verification/compact-r4-bounded-runtime.json`

### BLAKE3 B7: seven-round arithmetic and the declared memory charge

- Original path: `research/blake3_r7/b7/pkg/blake3/experiments/bsrho.py`
- SHA-256: `6debf93642cd67e0fc31bb5aebcda46a1524c4e80a2dd192eea9ce481c775315`
- Usage guide: `guide.html?id=b2448fd19fa618a3e0bb`
- Source/download: `record.html?id=b2448fd19fa618a3e0bb`
- Detailed README in the archive: `guides/b2448fd19fa618a3e0bb.md`
- Finite test report: `verification/b7-r7-bounded-runtime.json`

### BLAKE3 B9v3: the same rolled circuit, a different numerical model

- Original path: `research/blake3_r7/b9v3/pkg/blake3/experiments/bsrho.py`
- SHA-256: `5364c8dfa8032e4208178f546430bac16e4a361baee0d348afe5ef98c50ea9ae`
- Usage guide: `guide.html?id=c082fa8b9ac99349625e`
- Source/download: `record.html?id=c082fa8b9ac99349625e`
- Detailed README in the archive: `guides/c082fa8b9ac99349625e.md`
- Finite test report: `verification/b9r7-bounded-runtime.json`

### BLAKE3 original six-round compact edition: two capacity boundaries

- Original path: `research/blake3_r6/compact/pre/pkg/blake3/experiments/bsrho.py`
- SHA-256: `87e8a6b771ffb929c01a17c0e4dd45d3df46e46761766e58c2200e94eab19745`
- Usage guide: `guide.html?id=c4884c1835009e51d0b5`
- Source/download: `record.html?id=c4884c1835009e51d0b5`
- Detailed README in the archive: `guides/c4884c1835009e51d0b5.md`
- Finite test report: `verification/compact-r6-bounded-runtime.json`

### BLAKE3 fixed-prefix stack: smaller columns, compact tables and checkpoint recovery

- Original path: `research/blake3_r3/stack1020/pkg/blake3/experiments/bsrho.py`
- SHA-256: `65d9b1537f1ac8b5a2a8807a93c7d3179c87a0973e69b5d48a3341b012440411`
- Usage guide: `guide.html?id=ca040f5d3527f0a8844c`
- Source/download: `record.html?id=ca040f5d3527f0a8844c`
- Detailed README in the archive: `guides/ca040f5d3527f0a8844c.md`
- Finite test report: `verification/stack1020-bounded-runtime.json`

### BLAKE3 B4B/B4C: save endpoint space, recompute trail lengths

- Original path: `research/blake3_r4/b4b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `9cc4c43839337a10ac5beae5d8ca907ee16496d028741f97ff652f7dae627013`
- Usage guide: `guide.html?id=cb1bdb1323a17b0511b6`
- Source/download: `record.html?id=cb1bdb1323a17b0511b6`
- Detailed README in the archive: `guides/cb1bdb1323a17b0511b6.md`
- Finite test report: `verification/b4b-r4-bounded-runtime.json`

### BLAKE3 bitslice2: a fixed first block changes the circuit and the accounting

- Original path: `research/blake3_r3/bitslice2/pkg/blake3/experiments/bsrho.py`
- SHA-256: `4f46578df1c1bec00b363b269bd139833fd61c3f734f4c5513685f60cd2ee943`
- Usage guide: `guide.html?id=d8c0c3bd99ea7cd35121`
- Source/download: `record.html?id=d8c0c3bd99ea7cd35121`
- Detailed README in the archive: `guides/d8c0c3bd99ea7cd35121.md`
- Finite test report: `verification/bitslice2-bounded-runtime.json`

### BLAKE3 five-round compact binary edition: wider trail IDs, missing code bytes

- Original path: `research/blake3_r5/compact_u5b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `d628553d0d8e7c806b62145c7bdaef647b60905c1b9c72f2e4e347b8af846530`
- Usage guide: `guide.html?id=dd6b81cc79fe124e033c`
- Source/download: `record.html?id=dd6b81cc79fe124e033c`
- Detailed README in the archive: `guides/dd6b81cc79fe124e033c.md`
- Finite test report: `verification/compact-u5b-r5-bounded-runtime.json`

### BLAKE3 pivot walk: the same circuit can have a different storage price — retained exact copy

- Original path: `research/checks_1015/pa_src/pos_b3r3pv/experiments/bsrho.py`
- SHA-256: `4109c3f80a0a25369f7c06fb7d37d86a0c07d917ff66602a0c6e6fe9ab4d5078`
- Usage guide: `guide.html?id=ddcbe2f9b88d719a60b4`
- Source/download: `record.html?id=ddcbe2f9b88d719a60b4`
- Detailed README in the archive: `guides/ddcbe2f9b88d719a60b4.md`
- Finite test report: `verification/pivot1-bounded-runtime.json`

### BLAKE3 B8v2: reuse a main round body, count every execution

- Original path: `research/blake3_r7/b8v2/pkg/blake3/experiments/bsrho.py`
- SHA-256: `a2ad71a0ea6d0df50e4ba3b137e55ec0d5ba314ab60be29bd8ac0a1f6f7d4d8b`
- Usage guide: `guide.html?id=de83a64db4c0e64e2a3b`
- Source/download: `record.html?id=de83a64db4c0e64e2a3b`
- Detailed README in the archive: `guides/de83a64db4c0e64e2a3b.md`
- Finite test report: `verification/b8v2r7-bounded-runtime.json`

### BLAKE3 B4: store the trail length, count the full instruction record

- Original path: `research/blake3_r4/b4/pkg/blake3/experiments/bsrho.py`
- SHA-256: `07cb1f6a62b7f375d4ba6da2653846a2df8509ec7cd3790b2624c4494dc4f747`
- Usage guide: `guide.html?id=e65b323e082eb4377ff7`
- Source/download: `record.html?id=e65b323e082eb4377ff7`
- Detailed README in the archive: `guides/e65b323e082eb4377ff7.md`
- Finite test report: `verification/b4-r4-bounded-runtime.json`

### BLAKE3 H16-named copies: read the executable gate and endpoint fields

- Original path: `research/blake3_r7/pkg_u5b_snapshot_for_h16/blake3/experiments/bsrho.py`
- SHA-256: `d9cbc92ca0f7f8f3aceefb9ad5f70c764517a40215c5ce4dc2eda9e8721e6bb5`
- Usage guide: `guide.html?id=ea46afa7e8e9d843311f`
- Source/download: `record.html?id=ea46afa7e8e9d843311f`
- Detailed README in the archive: `guides/ea46afa7e8e9d843311f.md`
- Finite test report: `verification/compact-h16-r7-bounded-runtime.json`

### BLAKE3 H16-named copies: read the executable gate and endpoint fields

- Original path: `research/blake3_r7/compact_h16/pkg/blake3/experiments/bsrho.py`
- SHA-256: `d9cbc92ca0f7f8f3aceefb9ad5f70c764517a40215c5ce4dc2eda9e8721e6bb5`
- Usage guide: `guide.html?id=ed1c96d93cc8cbca8fe0`
- Source/download: `record.html?id=ed1c96d93cc8cbca8fe0`
- Detailed README in the archive: `guides/ed1c96d93cc8cbca8fe0.md`
- Finite test report: `verification/compact-h16-r7-bounded-runtime.json`

### BLAKE3 six-round compact binary edition: separate the two capacity checks

- Original path: `research/blake3_r6/compact_u5b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `e669b71c3aa7856c9be7fd13fd078dc474090cc4550b7867703f896566d6412a`
- Usage guide: `guide.html?id=edf75ad8e46e614808b9`
- Source/download: `record.html?id=edf75ad8e46e614808b9`
- Detailed README in the archive: `guides/edf75ad8e46e614808b9.md`
- Finite test report: `verification/compact-u5b-r6-bounded-runtime.json`

### BLAKE3 b3r3s: grouped filters, paid replays and the kernel-versus-loop register boundary

- Original path: `research/blake3_r3/b3r3s/pkg/blake3/experiments/rho.py`
- SHA-256: `8cb1b4256e971a796ee108f6c36a7f9afce4ea038b4f7f0f2968da71c08c3882`
- Usage guide: `guide.html?id=f0b94ce27461d76414a7`
- Source/download: `record.html?id=f0b94ce27461d76414a7`
- Detailed README in the archive: `guides/f0b94ce27461d76414a7.md`
- Finite test report: `verification/b3r3s-bounded-runtime.json`

### BLAKE3 bitslice3: polarity-search provenance and reuse of setup memory

- Original path: `research/checks_1015/pa_src/b3r3bs3_pkg/experiments/bsrho.py`
- SHA-256: `ef98cfcd1a51c617b230526f376ef194653cfe9a363ce04a1913c67d0c8d58c7`
- Usage guide: `guide.html?id=f17efcf3b6151f66e012`
- Source/download: `record.html?id=f17efcf3b6151f66e012`
- Detailed README in the archive: `guides/f17efcf3b6151f66e012.md`
- Finite test report: `verification/bitslice3-bounded-runtime.json`

### BLAKE3 four-round select edition: correct arithmetic, rejected price

- Original path: `research/blake3_r4/bsel/pkg/blake3/experiments/bsrho.py`
- SHA-256: `6da66e1b5955fd9f15da8bcdb5a6a5aea186a76269d1beb47ed11e152550f092`
- Usage guide: `guide.html?id=fa350f39fd8c09898cc3`
- Source/download: `record.html?id=fa350f39fd8c09898cc3`
- Detailed README in the archive: `guides/fa350f39fd8c09898cc3.md`
- Finite test report: `verification/bsel-r4-bounded-runtime.json`

### BLAKE3 four-round binary edition: inspect the missing recovery bytes

- Original path: `research/blake3_r4/compact_u5b/pkg/blake3/experiments/bsrho.py`
- SHA-256: `ceea9ed7d1d88598753536a8ed3115a713599bd1f05077f1ae77ff9aa8c26cad`
- Usage guide: `guide.html?id=fcc4edaf31f936c81aea`
- Source/download: `record.html?id=fcc4edaf31f936c81aea`
- Detailed README in the archive: `guides/fcc4edaf31f936c81aea.md`
- Finite test report: `verification/compact-u5b-r4-bounded-runtime.json`

### BLAKE3 H16-named copies: read the executable gate and endpoint fields

- Original path: `research/blake3_r7/h16_stage/pkg/blake3/experiments/bsrho.py`
- SHA-256: `d9cbc92ca0f7f8f3aceefb9ad5f70c764517a40215c5ce4dc2eda9e8721e6bb5`
- Usage guide: `guide.html?id=fcd4702837a6409bfbeb`
- Source/download: `record.html?id=fcd4702837a6409bfbeb`
- Detailed README in the archive: `guides/fcd4702837a6409bfbeb.md`
- Finite test report: `verification/compact-h16-r7-bounded-runtime.json`

## Getting started

Choose a starter/replay ZIP above when one is available; it supplies its own entry point and fixtures. Otherwise consult the selected component guide before installing dependencies.

- Python 3 standard library. Both reviewed copies are standalone and byte-identical; bitslice2 and later editions are separate sources.
- Independent checks use hash-smash/verifier/blake3.py at SHA-256 bf67aca295b45b06621891d9219c71166e5855b1afd0464a87d1dbb1314f0237; it is not newly redistributed by this guide.

### Generate the full-width circuit and allocate its registers without a search

Working directory: A disposable directory containing the downloaded, hash-checked bsrho.py

```text
python -I -B -c "import runpy; m=runpy.run_path('bsrho.py',run_name='bounded_copy'); s=m['step256'](); c,r=m['allocate'](s); print(s.ops,r)"
```

Expected: 19022 771

## Reuse and attribution

Preserve source-specific licenses, contributor credits and version context. Some families adapt or compare upstream tools; this toolkit does not assert that every underlying method originated here. Historical experiments may need external solvers, compilers, data or parameters; the linked guide identifies the actual interface and tested scope.
