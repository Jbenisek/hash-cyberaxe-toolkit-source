# HASH$CyberAxe research toolkit source collection

> **By Jeremy Benisek ([CyberAxe](https://cyberaxe.dev/))** · part of **[HASH$CyberAxe](https://hashcyberaxe.com/)** open research
>
> Research library: [hashcyberaxe.com](https://hashcyberaxe.com/) · Tools & data: [hashcyberaxe.com/tools.html](https://hashcyberaxe.com/tools.html) · Play the game: [hashcyberaxe.com/game](https://hashcyberaxe.com/game/)

**What this is for.** The full source of the HASH$CyberAxe research tools: the programs and scripts used to study reduced-round SHA-256, BLAKE3, SHA-3 and Poseidon. It covers characteristic builders, SAT encoders, independent verifiers, schedule diagnostics, BLAKE3 circuit kernels, cost calculators and the browser labs. Use it to see how a published result was produced, run a method on your own inputs, or build a new tool from the same parts. There are 19 tool families; each has a README in `readmes/` and setup guides in `guides/`.

**Credits.** Author: **Jeremy Benisek (CyberAxe)**: research direction, questions and project lead. Made with AI research and coding agents working under CyberAxe's direction; the agents are tools, not authors. Third-party code keeps its original authors and notices ([AUTHORS.md](AUTHORS.md)).

**License.** See [LICENSING.md](LICENSING.md). Credit: "Jeremy Benisek (CyberAxe), HASH$CyberAxe, https://hashcyberaxe.com/".

Part of the HASH$CyberAxe research tools and reproducibility collection.

## Start here

Read the included [original instructions](README_ORIGINAL.md) for the scientific method, inputs, examples and expected results.

## Requirements

Python 3.11 or newer runs the included integrity checker.

## Choose a tool

Start with `readmes/` (19 families), `guides/` (individual setup and examples), and `toolkit.json` (machine-readable inventory).

Historical source paths are preserved under `archive/`; use that directory as the old workspace root. `HASHCYBERAXE_WORKSPACE` adapters are retained. External solver/compiler/math dependencies vary by component; no search driver is automatically run.

The separately staged finite kits provide tested standalone entry points. This collection keeps shared source dependencies together rather than presenting every historical script as an independent application.

## Files, provenance and reuse

`PROJECT.json` records the original archive hash and the exact entry point. `ORIGINAL_FILES.json` maps every preserved payload file to its source identity. A root original README, when present, is named `README_ORIGINAL.md`; scientific code and data bytes are unchanged.

`FILES.sha256.json` pins this prepared edition. [RIGHTS.md](RIGHTS.md) explains retained source credits and licensing. Scientific result scope is documented in the original instructions.

## Source

Prepared from the HASH$CyberAxe research library (https://hashcyberaxe.com/) by its publication process; `PROJECT.json` and `ORIGINAL_FILES.json` record the original archive and file identities.

## Editorial guide edition

Editorial version: `showcase-20261105-v3`. The Markdown under `guides/` mirrors the current library guide text by guide ID. `EDITORIAL_GUIDES.json` records this amendment. `ORIGINAL_FILES.json` retains original archive hashes and records project hashes for explicitly derived guide documents.

The raw source archive identity, every `archive/` member, scientific code, data, proof, results and source credits remain unchanged. `FILES.sha256.json` pins this prepared editorial edition.

## Not in this public edition

Left out of the public source collection (3920 files; the library's full archive keeps them):

- `archive/research/rivals/`: other teams' competition board submissions: not HASH$CyberAxe work, and they contain private contact details.
- `archive/research/poseidon/rivals/`: other teams' Poseidon notes: not HASH$CyberAxe work.
- `archive/critical/research/kepler_snapshot_`: AI agent session snapshots and agent reviews.
- `archive/critical/research/grok/`: AI agent work folders.
- `archive/research/fifties/combos/grok`: AI agent task briefs and their work folders.
- `archive/research/luna/audit_packets/`: audits of AI agent sessions.
- `archive/critical/research/sol_answer_`: AI agent answer notes.
- `judge_textscan\.py`: a content-filter script whose word list spells out slurs.

Their 45 rows in `toolkit-index.csv` and 45 tool guides were removed with them. Some remaining notes still mention those paths.

**Public edition.** 54 files were edited for this edition: agent names replaced with HASH$CyberAxe credit and owner quotes with CyberAxe. [PUBLIC_EDITION_EDITS.json](PUBLIC_EDITION_EDITS.json) lists each file, why, and its original SHA-256.
