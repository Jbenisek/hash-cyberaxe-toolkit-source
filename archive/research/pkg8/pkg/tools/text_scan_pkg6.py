#!/usr/bin/env python3
"""Scan of everything that a submission of the sixth package would make public. Research helper, not submitted.

    python -B tools/text_scan_pkg6.py [--quiet] [--program]

Files: every file under blake3-r2/ and the submission note; with --program only the experiment program and its
manifest. Per line it looks for
  - bytes outside ASCII, control characters, HTML comments and links;
  - file-system paths (drive letters, home folders, mount points, the workspace's folder names);
  - the names of the accounts on this machine (taken from the environment at run time, never written here),
    e-mail addresses and handles that start with @;
  - strings that look like keys or tokens (known prefixes, private-key headers, long runs of base64);
  - offensive words, also in hex or digit spelling, and sentences that address or instruct a reviewer or a model:
    both with the word list and the patterns of research/public_text_scan.py, which are read from that file.
It prints one line per file and the place of anything found, never the matched text of a name, key or word.
The exit status is 0 only if nothing is found.

One exception, stated in the output whenever it is used: the six constants of the pin (tools/pkg6_data.py, PIN) are
numbers that the package has to print. Written with eight hexadecimal digits, one of them contains three digits
that the digit spelling of the word list reads as a listed word. For the word test alone, these six numbers are
taken out of a line before it is tested; the tool counts the lines that would have been reported without this and
names them. research/public_text_scan.py has no such exception and reports those lines.
"""
import getpass
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
RESEARCH = PKG.parent
sys.path.insert(0, str(TOOLS))
import pkg6_data  # noqa: E402  (only PIN)

PIN_HEX = re.compile(r"(?<![0-9a-f])(?:0x)?(?:" + "|".join(f"{v:08x}" for v in pkg6_data.PIN.values()) + r")(?![0-9a-f])")
QUIET = "--quiet" in sys.argv
FILES = [p for p in sorted((PKG / "blake3-r2").rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
FILES.append(PKG / "submission-note-r2.md")
if "--program" in sys.argv:
    FILES = [PKG / "blake3-r2" / "experiments" / "halfsearch.py", PKG / "blake3-r2" / "experiments" / "manifest.json"]

PATHS = re.compile(r"[A-Za-z]:[\\/]|\\\\|/mnt/|/home/|/root\b|~/|\bUsers[\\/]|AppData|research[\\/]|workspace[\\/]|hashsmash/|\.claude|"
                   r"\bpkg[0-9]|night[\\/]", re.I)
MAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
HANDLE = re.compile(r"(?<![A-Za-z0-9])@[A-Za-z0-9_]{3,}")
KEYS = re.compile(r"\b(sk|xai|ghp|gho|ghs|pk|rk)[-_][A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{12,}|-----BEGIN|\bBearer\s+[A-Za-z0-9._-]{16,}|"
                  r"(?<![A-Za-z0-9+/])(?=[A-Za-z0-9+/]*[A-Z])(?=[A-Za-z0-9+/]*[a-z])(?=[A-Za-z0-9+/]*[0-9])[A-Za-z0-9+/]{40,}={0,2}")
LINK = re.compile(r"https?://|www\.", re.I)


def machine_names():
    """Account names of this machine, lower case, from the environment; nothing is typed here."""
    names = set()
    for value in (os.environ.get("USERNAME"), os.environ.get("USER"), os.environ.get("LOGNAME"), Path.home().name):
        if value and len(value) >= 4 and value.lower() not in ("root", "user", "admin", "administrator"):
            names.add(value.lower())
    try:
        value = getpass.getuser()
        if value and len(value) >= 4 and value.lower() not in ("root", "user", "admin", "administrator"):
            names.add(value.lower())
    except Exception:
        pass
    for part in Path(__file__).resolve().parts:               # a home folder in the path of this file, if any
        pass
    for base in (Path('historical-sources/Users'), Path("C:/Users")):
        if base.is_dir():
            for child in base.iterdir():
                if child.is_dir() and len(child.name) >= 4 and child.name.lower() not in ("public", "default", "default user", "all users"):
                    names.add(child.name.lower())
    return names


def word_rules():
    """BAD, LEET and INJECT of research/public_text_scan.py, read from that file; (None, None, None) if they are not there."""
    path = RESEARCH / "public_text_scan.py"
    if not path.exists():
        return None, None, None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^BAD = .*?^LEET = [^\n]*\n", text, re.S | re.M)
    i = re.search(r"^INJECT = re\.compile\(.*?\n(?=LINK = )", text, re.S | re.M)
    env = {"re": re}
    try:
        exec(m.group(0) + i.group(0), {"str": str, "re": re}, env)
    except Exception:
        return None, None, None
    return env.get("BAD"), env.get("LEET"), env.get("INJECT")


def main():
    names = machine_names()
    bad, leet, inject = word_rules()
    if not bad:
        print("NOTE: the word list of research/public_text_scan.py could not be read; offensive words are NOT checked")
    total, excepted = 0, []
    for p in FILES:
        raw = p.read_bytes()
        issues = []
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", "replace")
            issues.append("bytes outside ASCII")
        if "<!--" in text:
            issues.append("HTML comment")
        if "\r" in text or any(ord(ch) < 32 and ch not in "\n" for ch in text):
            issues.append("carriage return, tab or control character")
        for n, line in enumerate(text.split("\n"), 1):
            low = line.lower()
            if PATHS.search(line):
                issues.append(f"line {n}: something that looks like a path or a folder of the workspace")
            if any(name in low for name in names):
                issues.append(f"line {n}: an account name of this machine")
            if MAIL.search(line):
                issues.append(f"line {n}: an e-mail address")
            if HANDLE.search(line):
                issues.append(f"line {n}: a handle that starts with @")
            if KEYS.search(line):
                issues.append(f"line {n}: a string that looks like a key or token")
            if LINK.search(line):
                issues.append(f"line {n}: link")
            if bad:
                def listed(text):
                    plain = re.sub(r"[^a-z ]", " ", text)
                    spelled = re.sub(r"[^a-z ]", " ", text.translate(leet))
                    squeezed = re.sub(r"[^a-z]", "", text.translate(leet))
                    return any(b in plain or b in spelled or b.replace(" ", "") in squeezed for b in bad)

                if listed(PIN_HEX.sub(" . ", low)):
                    issues.append(f"line {n}: offensive word (plain, hex or digit spelling)")
                elif listed(low):
                    excepted.append(f"{p.relative_to(PKG).as_posix()}:{n}")
                if inject is not None and inject.search(line):
                    issues.append(f"line {n}: text that addresses or instructs a reviewer or a model")
        total += len(issues)
        if issues or not QUIET:
            print(f"{'clean' if not issues else 'CHECK'}  {p.relative_to(PKG).as_posix()}  ({len(raw)} bytes)")
        for i in issues[:10]:
            print("      ", i)
    if excepted:
        print(f"NOTE: {len(excepted)} line(s) are reported by the word test only because of a constant of the pin written in "
              f"hexadecimal digits, and are not counted: {', '.join(excepted[:12])}{' ...' if len(excepted) > 12 else ''}")
    print(f"files {len(FILES)}, account names looked for {len(names)}, word list {'read' if bad else 'NOT read'}, findings {total}")
    return 1 if total or not bad else 0


if __name__ == "__main__":
    sys.exit(main())
