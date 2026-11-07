# Poseidon (Orchard) research atlas

Start with reports/RESEARCH_REPORT.md and REFERENCE_CARD.md. The workbook is a searchable companion; data/*.csv and *.json are the agent-facing feed. Each of 64 rounds also has its own Markdown dossier.

## Reproduce
```
python check_all.py
```
Requires Python 3.10+ and a C11 compiler `cc` for the exhaustive toy. No wallet,network,APIkey or external dataset is required. The math scripts use only Python standard libraries. Workbook generation uses artifact_tool separately and is not required for reproduction.

`analyze.py`: official vector transcriptions, inverses, MDS minors, partial chart, local root counts, native sensitivity/signatures, pairgrid, benchmarks.
`low_round_chart.py`: native bivariate-quintic coefficients and 2048 exact evaluations.
`build_toy.py`: compiles and runs all-input p257 model, explicitly not nativeOrchard.
`extra_checks.py`: derivative trap, toyminors, exact bookkeeping, legal-triple cardinality.
`build_documents.py`: reproducible reports,64 dossiers,sourcecatalog,questioncrosswalk,findings,unknowns.

## Scope
The public proposal snapshot is PR923/head 01f736268b7086d97f38837d343d63a81bf31649; it was open/unmerged and did not register a Yukon lane when queried. Do not submit a score based solely on its provisional arithmetic weights. No native collision campaign, complete cryptanalysis or productionZcash break is claimed.

Native-exact, sampled, toy-exact and source-only fields are separate. Structural coverage is not a proof of all interactions. See the report for exact population definitions and the sign conventions: additive field differences, not XOR masks.

`MANIFEST.json` and `SHA 256 SUMS.txt` pin local file bytes. Re-running changes timing data and documentation hashes; this is expected. Preserve the original directory when comparing replay results.
