"""Odd-input probe of the organizer's participant-output parser (local copy org_runner.py).
Docker is never started: _run_docker is replaced by a stub that returns crafted stdout bytes.
Run: python -B parse_edges.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import org_runner as R
import org_blake3

ENTRY = {"id": "edge", "event": {"kind": "full-collision"}}
digest_fn = lambda m: org_blake3.blake3(m, 2)


def run(stdout: bytes, trials=1):
    R._run_docker = lambda source, request, limits, image: stdout
    limits = R.ExperimentLimits(trials=trials)
    try:
        res = R._python_result(ENTRY, b"", limits, b"seed-material", "blake3-r2-prefix-v1", digest_fn, "stub")
        return "ACCEPT", res["checked_trials"]
    except Exception as e:
        return "REJECT", f"{type(e).__name__}: {e}"


def doc(a: bytes, b: bytes = b'"00"', extra: bytes = b"", trial: bytes = b"0", sv: bytes = b"1"):
    return (b'{"schema_version":' + sv + b',"trials":[{"trial":' + trial +
            b',"message_a_hex":' + a + b',"message_b_hex":' + b + extra + b'}]}')


def show(label, stdout, trials=1):
    status, info = run(stdout, trials)
    if status == "ACCEPT":
        rows = info
        brief = "; ".join(
            f"a={r.get('message_a_hex', '-')[:20]!r} b={r.get('message_b_hex', '-')[:12]!r} "
            f"success={r['success']} repeated={r.get('repeated_pair')} pair={r.get('pair_sha256', '-')[:10]}"
            for r in rows)
        print(f"ACCEPT  {label:44s} {brief}")
    else:
        print(f"REJECT  {label:44s} {info[:110]}")
    return status, info


u = lambda s: s.encode("utf-8")
print("=== 1. message_a_hex spellings (message_b_hex = '00') ===")
cases = [
    ("baseline 'ab'", b'"ab"'), ("empty string", b'""'), ("odd 'a'", b'"a"'), ("odd 'abc'", b'"abc"'),
    ("uppercase 'AB'", b'"AB"'), ("mixed 'aB'", b'"aB"'),
    ("leading space", b'" ab"'), ("trailing space", b'"ab "'), ("inner space", b'"a b"'),
    ("trailing \\n (JSON escape)", b'"ab\\n"'), ("leading \\t", b'"\\tab"'),
    ("0x prefix", b'"0xab"'), ("0X prefix", b'"0Xab"'), ("'-1'", b'"-1"'), ("'+ab'", b'"+ab"'),
    ("underscore 'a_b0'", b'"ab_00"'),
    ("JSON \\u escapes for 'ab'", b'"\\u0061\\u0062"'),
    ("fullwidth 'ａｂ'", u('"ａｂ"')), ("fullwidth digits '１２'", u('"１２"')),
    ("Arabic-Indic '١٢'", u('"١٢"')), ("Devanagari '१२'", u('"१२"')),
    ("Chinese numerals '一二'", u('"一二"')), ("superscript '¹²'", u('"¹²"')),
    ("math bold '𝟏𝟐'", u('"𝟏𝟐"')),
    ("NUL inside", b'"ab\\u0000"'), ("zero-width space", b'"ab\\u200b"'), ("BOM inside string", b'"\\ufeffab"'),
    ("lone surrogate", b'"\\ud800"'),
    ("number 171", b"171"), ("list ['ab']", b'["ab"]'), ("true", b"true"), ("object", b'{"x":"ab"}'),
    ("a=null, b='00' (one-sided null)", b"null"),
    ("max length 8192 chars", b'"' + b"00" * 4096 + b'"'), ("8194 chars (over)", b'"' + b"00" * 4097 + b'"'),
    ("odd 8193 chars", b'"' + b"0" * 8193 + b'"'),
]
for label, a in cases:
    show(label, doc(a))
show("both null", doc(b"null", b"null"))
show("a == b == 'ab'", doc(b'"ab"', b'"ab"'))

print("\n=== 2. stdout envelope ===")
base = doc(b'"ab"')
for label, out in [
    ("UTF-8 BOM prefix", b"\xef\xbb\xbf" + base), ("UTF-16-LE with BOM", base.decode().encode("utf-16")),
    ("UTF-16-BE no BOM", base.decode().encode("utf-16-be")), ("UTF-32", base.decode().encode("utf-32")),
    ("leading/trailing whitespace", b" \n\t" + base + b"\r\n"), ("two documents", base + base),
    ("trailing garbage", base + b"x"), ("trailing comma", base[:-2] + b",]}"),
    ("duplicate key message_a_hex", doc(b'"ab"', extra=b',"message_a_hex":"cd"')),
    ("key spelled message\\u005fa_hex", base.replace(b'"message_a_hex"', b'"message\\u005fa_hex"')),
    ("extra unknown key", doc(b'"ab"', extra=b',"note":"x"')),
    ("trial '0' (string)", doc(b'"ab"', trial=b'"0"')), ("trial true", doc(b'"ab"', trial=b"true")),
    ("trial 0.0", doc(b'"ab"', trial=b"0.0")), ("trial -0", doc(b'"ab"', trial=b"-0")),
    ("trial 0e0", doc(b'"ab"', trial=b"0e0")), ("trial 00 (leading zero)", doc(b'"ab"', trial=b"00")),
    ("schema_version 1.0", doc(b'"ab"', sv=b"1.0")), ("schema_version true", doc(b'"ab"', sv=b"true")),
    ("obs 1e400 (inf)", doc(b'"ab"', extra=b',"observations":{"x":1e400}')),
    ("obs NaN", doc(b'"ab"', extra=b',"observations":{"x":NaN}')),
    ("obs true", doc(b'"ab"', extra=b',"observations":{"x":true}')),
    ("obs 10**100+1 int", doc(b'"ab"', extra=b',"observations":{"x":' + str(10**100 + 1).encode() + b'}')),
    ("obs huge int 5000 digits", doc(b'"ab"', extra=b',"observations":{"x":' + b"9" * 5000 + b'}')),
    ("obs key fullwidth 'ｘ'", doc(b'"ab"', extra=u(',"observations":{"ｘ":1}'))),
    ("obs nested 100000 deep", doc(b'"ab"', extra=b',"observations":' + b"[" * 100000 + b"]" * 100000)),
]:
    show(label, out)

print("\n=== 3. same bytes, different spelling / order -> distinct pair ids? ===")
two = (b'{"schema_version":1,"trials":['
       b'{"trial":0,"message_a_hex":"ab","message_b_hex":"cd"},'
       b'{"trial":1,"message_a_hex":"cd","message_b_hex":"\\u0061b"}]}')
show("(ab,cd) then (cd, \\u0061b)", two, trials=2)
three = (b'{"schema_version":1,"trials":['
         b'{"trial":0,"message_a_hex":"ab","message_b_hex":"cd"},'
         b'{"trial":1,"message_a_hex":"ab","message_b_hex":"cd"},'
         b'{"trial":2,"message_a_hex":"ab","message_b_hex":"cd00"}]}')
st, rows = show("replayed pair x2, then cd00", three, trials=3)

print("\n=== 4. what bytes.fromhex alone would accept (the regex is the only guard) ===")
for s in ["AB", " ab ", "a b", "ab\n", "0xab", "ａｂ", "１２", "a"]:
    try:
        print(f"bytes.fromhex({s!r}) -> {bytes.fromhex(s).hex()!r}   _HEX.fullmatch: {bool(R._HEX.fullmatch(s))}")
    except ValueError as e:
        print(f"bytes.fromhex({s!r}) -> ValueError   _HEX.fullmatch: {bool(R._HEX.fullmatch(s))}")
for s in ["１２", "ＦＦ", "f_f", " 0xff ", "-1", "١٢"]:
    try:
        print(f"int({s!r},16) -> {int(s, 16)}   _HEX.fullmatch: {bool(R._HEX.fullmatch(s))}")
    except ValueError:
        print(f"int({s!r},16) -> ValueError   _HEX.fullmatch: {bool(R._HEX.fullmatch(s))}")
print("(int(...,16) is only applied to mask_hex/expected_hex, which validate_manifest regex-gates first)")

print("\n=== 5. replayed pair under a stub digest where every distinct pair 'collides' ===")
digest_fn = lambda m: b"\x00" * 32
status, rows = run(three, trials=3)
print(status, [(r["success"], r["repeated_pair"]) for r in rows] if status == "ACCEPT" else rows)
print("python", sys.version.split()[0])
