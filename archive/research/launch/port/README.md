# Row templates (owner 10-18: template each path, only change the required lines)

Each family template keeps every line that is the same across the filed rows as fixed text; only the numbers,
entry ids and credits that differ per row are slots. A new row = one values file + one command.

## Tools
- `mktmpl.py <out> <file-rel> <rowdir>...` builds `<file>.tmpl` + `<file>.vals.json` from filed rows (rows aligned, so
  variant sections become optional blocks).
- `filltmpl.py <tmpl> <vals.json> <row> <out>` fills one file. `extract.py <tmpl> <real-file> <row> <out.json>` reads a
  row's values back out of a real file.
- `newrow.py <template-dir> <values.json> <row> <base-pkg> <out-pkg> name=rel ...` builds a whole package from a base
  row's package plus the new row's values (all templated files).
- `test_all.sh` runs the standing tests; `mock_e2e.sh` runs a timed build + organizer intake (stage only; the mock
  submit script is archived to slotstage/out/archive_mock, never left in the queue).

## Families (templates/)
| family | rows | files |
|---|---|---|
| poseidon_onecentre | r11S r12K-r22K (12) | proof, claim, note, dependencies |
| poseidon_generic | r7-r56 (50) | proof, claim, note, dependencies |
| sha3_r9_r22 | r9-r22 (14) | proof, claim, note, dependencies |
| sha256_r40_r63 | r40-r63 (24) | proof, claim, note, dependencies |

## Test results 10-18 20:50 MDT
- Reconstruction: every row of every family rebuilds byte for byte (16 template files, 100 rows), 136 s.
- Leave-one-out: generic, SHA3, SHA-256 all fit; Poseidon one-centre fits except variant rows r11S, r14K, r21K
  (their unique lines are kept as slots).
- Held-out generation: r13 (one-centre), r40 (generic), r15 (SHA3), r50 (SHA-256) generated from templates built
  WITHOUT them are byte-identical to the filed rows.
- End-to-end (mock_times.txt): built from the previous row's base package, all 4 files identical, intake passed:
  one-centre r13 0.45 s build + 98.2 s intake; generic r40 0.44 s + 19.8 s; SHA3 r15 0.38 s + 2.3 s; SHA-256 r50 0.50 s + 26.4 s.

## Not covered
Variant rows outside these families (SHA3 r7/r8/r23/r24, SHA-256 r39/r64, BLAKE3) have their own text; build a
template for a variant from its own rows when it gets more than one.
