# Edge-case probe: reduced BLAKE3 and the message-pair parser (2026-10-08)
Local only, on copies of the organizers' public code (org_blake3.py, org_runner.py). No Docker, no yukon, no server contact.
Anything below is a bug report or a note for the organizers. None of it is a scoring path, and none of it is to be exploited.
## 1. Differential test of blake3(msg, rounds)  -> 0 differences in 4,565 comparisons
- My own BLAKE3 (my_blake3.py: streaming chunk state plus CV stack, round count adjustable) gives the official 7-round vectors:
  empty = af1349b9...3262 and "abc" = 6437b3ac...9d85. The organizers' code gives the same two values.
- Full messages, rounds 1..7, 4 data patterns (i%251, zeros, 0xff, random), 96 lengths: 0, 1, 63, 64, 65, 1023, 1024, 1025,
  2047, 2048, 2049, 3071-3073, 4095-4097, plus 60 random lengths up to 9000. 2,688 comparisons, all equal.
- Chunk counts 2^k-1, 2^k, 2^k+1 for k=0..10 (up to 1025 chunks / 1 MiB), each at length -1/0/+1 byte, rounds=2. 330 comparisons, all equal.
- Counters near 2^32 and the high counter word: I compared only the chunk nodes I needed, without hashing huge data.
  Counters 0, 1, 2^31, 2^32-2..2^32+1, 2^33-1, 2^33, 2^40+12345, 2^51-2, 2^51-1 (the last chunk index reachable under the
  length limit); chunk sizes 0..1024; rounds 1..7. 588 comparisons, all equal.
- Tree merging was tested with a fast stand-in compression put into both implementations: every chunk count 1..299, plus
  2^k-1, 2^k, 2^k+1 for k=9..14 (16,385 chunks), each at length -1/0/+1 byte. 957 comparisons, all equal.
- Guards: rounds 0, 8, -1, True and 2.0 are rejected; str, bytearray and memoryview too; a bytes subclass is accepted. Notes, not bugs:
  the length limit is < 2^61 bytes (BLAKE3 allows < 2^64), and the high counter word is unmasked for counters >= 2^64; neither is reachable.
## 2. Parser: experiments/runner.py _python_result (lowercase-hex regex `(?:[0-9a-f]{2})+\Z`, then bytes.fromhex)
- Accepted: lowercase even-length hex; "" (empty message); exactly 2*max_message_bytes characters; both values null (trial counted as no pair).
- Rejected (the whole experiment fails, not just that trial): odd length; any uppercase letter; leading, trailing or inner spaces;
  "\n" and "\t"; 0x/0X prefixes; "-1"; "+ab"; "_"; fullwidth letters and digits (ａｂ, １２); Arabic-Indic, Devanagari,
  Chinese (一二), superscript and math-bold digits; NUL; zero-width space; BOM inside the string; lone surrogate; number,
  list, bool and object values; strings over the length limit.
- Normalised before the check, giving the same bytes and the same pair id: JSON \u escapes ("ab" == "ab");
  escaped key names ("message_a_hex"); stdout in UTF-8 with BOM, UTF-16 (LE/BE) or UTF-32, because json.loads(bytes)
  detects the encoding; whitespace around the document; trial -0.
- Envelope rejections: two documents, trailing data, a trailing comma, duplicate keys, an extra key, NaN, 1e400, a 5000-digit
  int, nesting 100,000 deep, trial given as "0", true, 0.0, 0e0 or 00, and schema_version 1.0 or true.
- Two spellings of one message: not possible. The regex makes hex <-> bytes one-to-one, and the pair id is
  sha256(sorted hex strings), so (a,b) and (b,a) share an id. One value, two messages: not possible either.
  Without the regex, bytes.fromhex alone would accept "AB", " ab " and "ab\n"; the regex is the only guard against that.
## 3. Observations for the organizers (by design, or not reachable today)
1. A replayed pair is marked repeated_pair=true but still adds to "successes". With a stub digest, 3 trials using 2 distinct
   pairs scored 3/3. The report's probability_inference text admits this. Counting only distinct pairs would remove the ambiguity.
2. If only one of the two messages is null, the whole experiment is rejected, not just that trial.
3. UTF-16 and UTF-32 stdout are accepted without notice. Harmless, but stdout_sha256 then differs for the same content.
4. int(x, 16) accepts "１２", "١٢", "f_f", " 0xff " and "-1". It is only applied to mask_hex/expected_hex, which validate_manifest
   checks against the same regex first (it also rejects a zero mask). So this is safe today but fragile if that regex is relaxed.
Not tested: Docker path, max_output_bytes cap, organizers' host Python (I ran 3.14.3), certificate files on a case-insensitive
filesystem, whole trees at counters >= 2^32 (node-level and tree tests instead). Blocked: nothing. Files: my_blake3.py, diff_blake3.py(+.out.txt), parse_edges.py(+.out.txt), org_*.py (copies, unedited).
