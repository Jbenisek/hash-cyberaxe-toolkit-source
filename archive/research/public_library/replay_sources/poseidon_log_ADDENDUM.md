

## Added log-checker controls (v2)

The same replay command also runs twelve copied-source controls for
verify_collision.py. An inert temporary fixture explicitly blocks its optional
organizer import: passing these tests is NOT organizer-verifier evidence.
The r1 and r2 positive examples use the project reference and existing public
numerical witnesses. They are not new collision discoveries.

No input files, a log without a digest and an uppercase-only digest can exit
zero without verifying a witness. Duplicate fields keep their last value.
A parsed bad digest, identical message pair, missing required field,
noncanonical field input and invalid schedule fail. The parser accepts
lowercase 64-hex-digit prefixes and does not validate trailing text. Require
an explicit positive verified-record count: exit zero alone is insufficient.

R defaults to 1 and counts partial rounds in addition to eight full rounds.
R=0 is not an identity operation. These controls do not execute a solver,
import organizer code, reproduce attack counters or establish a success law.

Keep all eight files together, including MANIFEST.json. The v2 wrapper launches
api_replay.py and check_log_contract.py using isolated Python mode with bytecode
writes disabled, each with a 30-second timeout. The latter creates and removes
temporary log fixtures and bounded checker subprocesses. Original source and
numerical inputs are never modified. The API's 74 named checks, 33 existing
witnesses and 20 invalid-input controls remain present, with twelve additional
cases under results.log_checker_contract.
