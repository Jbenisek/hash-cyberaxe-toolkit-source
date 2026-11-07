#!/usr/bin/env python3
"""lastdiff_rank.py - rank SAT cells of census files."""
import sys
import argparse
import re

NUMLIST = re.compile(r'^\s*(\d+(\s*,\s*\d+)*)?\s*$')


def parse_nums(s):
    s = s.strip()
    if not s:
        return []
    return [int(x) for x in s.split(',') if x.strip() != '']


def parse_line(line):
    """Return (R, words_str, kicks_str, verdict, extra_list) or None."""
    fields = line.rstrip('\n').split('\t')
    if len(fields) < 2:
        return None
    try:
        R = int(fields[0].strip())
    except ValueError:
        return None
    words_str = fields[1].strip()
    # robust kicks: present only if 3rd field looks like a numeric list
    if len(fields) >= 3 and NUMLIST.match(fields[2]):
        kicks_str = fields[2].strip()
        verdict = fields[3].strip() if len(fields) > 3 else ''
        extra = fields[4:]
    else:
        kicks_str = ''
        verdict = fields[2].strip() if len(fields) > 2 else ''
        extra = fields[3:]
    return R, words_str, kicks_str, verdict, extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--min-free', type=int, default=None)
    ap.add_argument('--max-words', type=int, default=None)
    ap.add_argument('--summary', action='store_true')
    args = ap.parse_args()

    rows = []            # ranking rows
    summary = {}         # file -> {(R,lastdiff): count}

    for fn in args.files:
        try:
            fh = open(fn, 'r')
        except OSError as e:
            print(f"# cannot open {fn}: {e}", file=sys.stderr)
            continue
        with fh:
            for line in fh:
                if line.startswith('#'):
                    continue
                if not line.strip():
                    continue
                p = parse_line(line)
                if p is None:
                    continue
                R, words_str, kicks_str, verdict, extra = p
                if verdict != 'SAT':
                    continue
                words = parse_nums(words_str)
                kicks = parse_nums(kicks_str)
                lastdiff = max(kicks) if kicks else (max(words) if words else -1)
                free = R - 1 - lastdiff
                core = lastdiff + 1
                nwords = len(words)
                summary.setdefault(fn, {})
                key = (R, lastdiff)
                summary[fn][key] = summary[fn].get(key, 0) + 1
                if args.min_free is not None and free < args.min_free:
                    continue
                if args.max_words is not None and nwords > args.max_words:
                    continue
                rows.append((fn, R, lastdiff, core, free, nwords,
                             words_str, kicks_str, '|'.join(extra)))

    if args.summary:
        print('\t'.join(['file', 'R', 'lastdiff', 'count']))
        for fn in args.files:
            if fn not in summary:
                continue
            for (R, ld) in sorted(summary[fn].keys()):
                print('\t'.join(map(str, [fn, R, ld, summary[fn][(R, ld)]])))
        return

    rows.sort(key=lambda r: (-r[4], r[5], -r[1]))
    print('\t'.join(['file', 'R', 'lastdiff', 'core', 'free',
                      'nwords', 'words', 'kicks', 'extra']))
    for r in rows:
        print('\t'.join(map(str, r)))


if __name__ == '__main__':
    main()
