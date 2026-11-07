#!/usr/bin/env python3
"""Scan of the experiment program (and of the work copy of its manifest) for what must not become public.

    python -B work/tools/text_scan.py        writes work/evidence/text_scan.txt

A copy of tools/text_scan_pkg6.py of the package before this one, with the files changed to halfsearch.py of this
folder and work/base/blake3-r2/experiments/manifest.json. Per line it looks for bytes outside ASCII, control
characters, HTML comments and links; file-system paths and the workspace's folder names; the names of the accounts
on this machine (taken from the environment at run time, never written here), e-mail addresses and handles;
strings that look like keys or tokens; and the word list and the patterns of research/public_text_scan.py, which
are read from that file. It prints the place of anything found, never the matched text of a name, key or word.

The one exception of the original is kept and stated whenever it is used: the six constants of the pin, written
with eight hexadecimal digits, are taken out of a line before the word test. Research helper, not submitted.
"""
import getpass
import os
import re
import sys
from pathlib import Path

from common import PROGRAM, RESEARCH, ROOT, WORK, program, sha, write

hs = program()
PIN = (hs.X3, hs.X7, hs.X11, hs.X15, hs.W4, hs.W13)
PIN_HEX = re.compile(r"(?<![0-9a-f])(?:0x)?(?:" + "|".join(f"{v:08x}" for v in PIN) + r")(?![0-9a-f])")
FILES = [PROGRAM, ROOT / "blake3-r2" / "experiments" / "manifest.json"]
PATHS = re.compile(r"[A-Za-z]:[\\/]|\\\\|/mnt/|/home/|/root\b|~/|\bUsers[\\/]|AppData|research[\\/]|workspace[\\/]|hashsmash/|\.claude|"
                   r"\bpkg[0-9]|night[\\/]", re.I)
MAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
HANDLE = re.compile(r"(?<![A-Za-z0-9])@[A-Za-z0-9_]{3,}")
KEYS = re.compile(r"\b(sk|xai|ghp|gho|ghs|pk|rk)[-_][A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{12,}|-----BEGIN|\bBearer\s+[A-Za-z0-9._-]{16,}|"
                  r"(?<![A-Za-z0-9+/])(?=[A-Za-z0-9+/]*[A-Z])(?=[A-Za-z0-9+/]*[a-z])(?=[A-Za-z0-9+/]*[0-9])[A-Za-z0-9+/]{40,}={0,2}")
LINK = re.compile(r"https?://|www\.", re.I)


def machine_names():
    names = set()
    values = [os.environ.get("USERNAME"), os.environ.get("USER"), os.environ.get("LOGNAME"), Path.home().name]
    try:
        values.append(getpass.getuser())
    except Exception:
        pass
    for value in values:
        if value and len(value) >= 4 and value.lower() not in ("root", "user", "admin", "administrator"):
            names.add(value.lower())
    for base in (Path('historical-sources/Users'), Path("C:/Users")):
        if base.is_dir():
            for child in base.iterdir():
                if child.is_dir() and len(child.name) >= 4 and child.name.lower() not in ("public", "default", "default user", "all users"):
                    names.add(child.name.lower())
    return names


def word_rules():
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
    out = [f"PROGRAM sha256 {sha()}; python -B work/tools/text_scan.py"]
    if not bad:
        out.append("NOTE: the word list of research/public_text_scan.py could not be read; offensive words are NOT checked")
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
                    excepted.append(f"{p.name}:{n}")
                if inject is not None and inject.search(line):
                    issues.append(f"line {n}: text that addresses or instructs a reviewer or a model")
        total += len(issues)
        out.append(f"{'clean' if not issues else 'CHECK'}  {p.relative_to(ROOT).as_posix()}  ({len(raw)} bytes)")
        out.extend("       " + i for i in issues[:10])
    if excepted:
        out.append(f"NOTE: {len(excepted)} line(s) are reported by the word test only because of a constant of the pin written in "
                   f"hexadecimal digits, and are not counted: {', '.join(excepted[:12])}{' ...' if len(excepted) > 12 else ''}")
    out.append(f"files {len(FILES)}, account names looked for {len(names)}, word list {'read' if bad else 'NOT read'}, findings {total}")
    print(write("text_scan.txt", out), end="")
    return 1 if total or not bad else 0


if __name__ == "__main__":
    sys.exit(main())
