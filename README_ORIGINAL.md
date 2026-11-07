# HASH$CyberAxe Toolkit

Research tools, educational browser instruments and reproducible methods.
HashSmash is the current contest collection; the toolkit can grow across future contests.

## Choose a job

Use tools.html for the named toolkit catalogue, family READMEs, starter kits and
searchable source inventory. data/toolkit.json is the equivalent machine registry.
The inventory lists all 6,697 archived tool paths, grouped by exact source SHA-256
in the website so copies are not mistaken for separate products.

## Get a tool and run the right example

1. Choose a named tool family on the Tools page.
2. Read its README under downloads/toolkit-readmes/ and pick a component/version.
3. Prefer its documented starter/replay ZIP when one is available. These have their
   own entry points, fixtures and bounded-check instructions.
4. For source studies, extract HASH-CyberAxe-toolkit.zip. Original source paths are
   under archive/. Use archive/ as the historical workspace root when a command
   starts with research/. Source-specific setup still applies.
5. Read guides/<record-id>.md for inputs, outputs, dependencies, examples, expected
   results, review scope and the exact source hash. Do not execute a long historical
   search merely to check that a tool opens; use the guide's finite example.
6. Independently verify generated numerical results. Encoding, solving, numerical
   equality and pricing are separate stages of the research workflow.

## What is in the source archive

- Published research source files and adjacent public data/docs, with original paths.
- All 6,697 individual tool Markdown guides, plus the named family READMEs.
- The catalogue and source-specific verification reports.
- Public library example checkers and the compact exact-source extraction helper.
- Source hashes in SOURCE_SHA256.tsv. These identify bytes, not a universal test pass.

The source archive supplies the published tree, not every external dependency.
Python, C/C++, native XOR/CNF solvers and mathematical packages vary by tool.
Browser labs are linked from the catalogue; the full scientific cellbook remains
in the library's separate data downloads rather than being duplicated in this ZIP.
External books and private chats are not part of this toolkit.

## What improves previous workflows

Each named family's README includes a Before / What we added comparison, grounded
in its source guides. Examples include independent numerical replay instead of
trusting solver labels, explicit model pins instead of hand-edited defaults,
byte-identical source grouping instead of duplicate tool listings, inspectable
kernel/storage accounting, and an interactive reader over formerly separate dumps.
These are capability comparisons. A universal speedup over all earlier tools is
not asserted; numerical comparisons need their own matched experiment and evidence.

## New tools and releases

The catalogue uses stable family IDs, source record IDs and SHA-256 versions.
New tool families and editions can be added without replacing existing source
history. The downloadable registry is intended for both human and agent readers.

## Licenses and credits

Keep the original source licenses and contributor attributions. Some tools build
on upstream work, including the nldtool ecosystem and credited circuit designs.
No blanket license over all imported source is asserted by this README.
