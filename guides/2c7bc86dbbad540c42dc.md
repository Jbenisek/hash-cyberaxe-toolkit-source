# Poseidon prefix experiment: JSON input, bounded trials and a 14-bit event (v2/out)

Source: `research/poseidon/pkg_r7_paper/v2/out/experiments/exp_lowbits.py`

Public SHA-256: `c17123acb72061354d6c8eadf34c5f62245c93ac10b4174a3433b06ed47268a3`

## Reviewed usage contract

Run the historical JSON interface for poseidon-orchard-r7-prefix-v1 and inspect its fourteen-bit digest-prefix event. Full digest equality is a separate predicate. Byte-identical copies share source behavior, while each package retains its own parameters, evidence and success/price assumptions.

## Source inspection and available execution evidence

static-source-review; copied empty/invalid CLI and bounded numerical/stub controls; no real birthday search.

For each valid trial: a 76,800-byte stream (75 KiB), at most 1,200 permutation evaluations and at most 1,200 dictionary entries. At r7 each permutation makes 31 fifth-power calls, giving at most 37,200 such calls per trial, plus matrix arithmetic, SHAKE, serialization and Python overhead. The entire trials list is read and its outputs accumulated; batch work and memory are not globally capped. These source-level bounds are not a contest charge or an attack success theorem.

## Declared inputs

**One JSON request on standard input**: target_profile supplies the round count through its -r suffix; trials is a list of objects containing trial (echoed identifier) and seed (hexadecimal bytes). The historical packages declare poseidon-orchard-r7-prefix-v1. There is no internal validation of the complete profile name or a batch-length cap.

**Trial generation**: SHAKE-256(seed bytes) produces the entire 64*1200-byte stream up front. Each 64-byte block becomes two little-endian integers reduced modulo P, used as the first two state coordinates; capacity is 2^65. This deterministic, modulo-reduced stream is not a proved uniform independent input law.

## Outputs and interpretation

**JSON response**: schema_version=1 and a trials list. Each row echoes trial and contains message_a_hex/message_b_hex, either two nulls after exhaustion or two distinct 128-character hex strings. Each message concatenates two canonical 32-byte little-endian field elements.

**Exact matching predicate**: The first output field word is serialized little-endian as d. The key is (d[0]<<6)|(d[1]>>2): the first fourteen bits of the big-endian reading of those digest bytes. In field-integer bit numbering this selects bits0..7 and10..15, not the lowest fourteen field bits. Equality of this key is not full-output equality.

**Bounded publication evidence**: The empty JSON batch succeeds with zero target evaluations; missing profile and invalid seed fail without a JSON response. Three individual real permutations use 24,31,80 fifth-power calls for 0,7,56 partial rounds. Three separately mocked trial controls exercise a prefix-only match, identical-message rejection and exhaustion. Mock outputs are not scientific witnesses.

## Imports

- Python 3 standard library: sys, json and hashlib. Constants and the permutation are embedded; there are no imported local target modules.
- Download a copy and inspect the matching package manifest before real use. The source has an unguarded standard-input entry point, so importing it normally also consumes stdin.

## Entry points

```json
[
  {
    "name": "perm",
    "line": 73,
    "arguments": [
      "state",
      "rounds"
    ],
    "doc": ""
  },
  {
    "name": "enc",
    "line": 81,
    "arguments": [
      "v"
    ],
    "doc": ""
  },
  {
    "name": "trial",
    "line": 83,
    "arguments": [
      "seed",
      "rounds"
    ],
    "doc": ""
  }
]
```

## Worked examples

### PowerShell input-only smoke test; no birthday search

Working directory: A disposable directory containing the downloaded exp_lowbits.py, not an active research checkout

```text
'{"target_profile":"poseidon-orchard-r7-prefix-v1","trials":[]}' | python -I -B exp_lowbits.py
```

Expected: One JSON response with schema_version=1 and trials=[]. This tests input/output plumbing only and performs zero target evaluations.

## Example runs and tests

Nine identical distributed source copies. Empty/invalid-input copied CLI checks, three individual real permutation call traces and three mocked trial-flow controls. No real birthday search, organizer-verifier comparison, full-output collision or success-rate claim. Stubbed outputs are synthetic, not research witnesses. The runtime report identifies tested bytes, not every function or mode in the tool.

[Read the check report](../../verification/lowbits-family-bounded-runtime.json).

## Read alongside

- research/poseidon/pkg_r7_paper/v2/out/experiments/manifest.json
- research/poseidon/pkg_r7_paper/v2/out/proof.md

## Failure modes

- A returned pair satisfies only the reduced-event key; independently verify the intended full target before calling it a collision.
- The filename lowbits does not mean the lowest fourteen bits of the field integer.
- Seed reuse repeats the deterministic search; modulo reduction and selected inputs do not establish independent trials.
- Malformed input raises an exception rather than producing a structured per-trial error; a later bad trial can prevent the whole response.
- The program does not enforce the supported partial-round range or the complete target-profile name. Its loop is meaningful for the declared profile; do not infer arbitrary-profile compatibility.
- Nine identical source copies are nine package locations, not nine independent experiments or discoveries.
- The bounded report does not compare this permutation with the organizer verifier, price a full attack, or measure a real birthday success rate.
