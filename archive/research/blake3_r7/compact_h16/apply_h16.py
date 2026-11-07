#!/usr/bin/env python3
"""apply_h16.py : B3R7 H16 = u5b + 64-bit table slots (47-bit key, 17-bit trail number; the slot layout of TheTradoor 09fe5fcd, the 47-bit key of
b1e6de75) + age cap 16 L. Constants in bsrho.py and appA.py, every sentence that names the entry layout in proof_t.md, note_t.md, build_all.py.
Each replacement must match exactly once."""
import os
H = os.path.dirname(os.path.abspath(__file__))

def edit(rel, pairs):
    p = os.path.join(H, rel)
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, s.count(a), a[:80])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('ok', rel)

edit('pkg/blake3/experiments/bsrho.py', [
    ('KEYBITS, TBITS = 63, 17           # entry fields: 63-bit key, 17-bit trail number (80 bits = 10 bytes);',
     'KEYBITS, TBITS = 47, 17           # entry fields: 47-bit key, 17-bit trail number (64 bits = 8 bytes, one 64-bit slot);'),
    ('ENTRY = 10                         # table entry: key 8 bytes, trail number 2;',
     'ENTRY = 8                          # table entry: one 64-bit slot, key in the low 47 bits, trail number in the top 17;'),
    ('KAPPA_256 = 14\n', 'KAPPA_256 = 16\n'),
])
edit('appA.py', [
    ('TB, KEYB = 17, 63                                  # trail-number bits and key bits of a table entry (80 bits = 10 bytes)',
     'TB, KEYB = 17, 47                                  # trail-number bits and key bits of a table entry (64 bits = 8 bytes)'),
    ('N_BITS, S1, W, KAPPA = 256, 32, 90, 14 ', 'N_BITS, S1, W, KAPPA = 256, 32, 90, 16 '),
    ('= 5, 36, 1207, 800 * 32, 16384, 10, 0, 64 ', '= 5, 36, 1207, 800 * 32, 16384, 8, 0, 64 '),
])
edit('proof_t.md', [
    ('What changed against the in-review 76ab339a (B3R7e): the trail number of a table entry has 17 bits and the key 63 bits (the entry is still 10 bytes), because trail numbers reach 256 + {tmax} + 1 > 2^16; the starts bound 2^16 of Section 4 is 2^17 and the key false-match term uses 63 bits (Appendix A recomputed);',
     'What changed against the in-review 76ab339a (B3R7e): a table entry is one 64-bit slot, a 47-bit key and a 17-bit trail number (8 bytes; the slot layout of TheTradoor 09fe5fcd and the 47-bit key of b1e6de75, credited), so the table holds {tmax} entries; the trail number has 17 bits because trail numbers reach 256 + {tmax} + 1 > 2^16, so the starts bound of Section 4 is 2^17; the age cap is c = 16 L; the key false-match term uses the 47-bit key (Appendix A recomputed);'),
    ('(10-byte entry: key and t, no length, Section 7)', '(8-byte entry: key and t in one 64-bit slot, no length, Section 7)'),
    ('table capacity tmax = {tmax} entries of 10 bytes.', 'table capacity tmax = {tmax} entries of 8 bytes.'),
    ('two read-modify-write field stores of the 10-byte entry,', 'one store of the 8-byte entry (key and t in one 64-bit slot),'),
    ('the key array holds 4 keys per word, testing a word costs 8 operations, 9 with the AND that clears the top bit of each 64-bit lane (Section 7), charged 3 per key (12 per word).',
     'the table holds 4 slots per 256-bit word, testing a word costs 8 operations, 9 with the AND that clears the 17 trail-number bits of each 64-bit lane (Section 7), charged 3 per key (12 per word).'),
    ('Table: {tmax} entries * 10 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (63 bits) and the trail number t (17 bits), 80 bits in 10 bytes, kept in two arrays: the key array holds 4 64-bit lanes per word, each lane the 63-bit key with bit 16 of t in its top bit, and the number array holds the low 16 bits of t, 16 per word;',
     'Table: {tmax} entries * 8 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (47 bits) and the trail number t (17 bits), 64 bits in one 8-byte slot (the layout of 09fe5fcd): the table holds 4 slots per 256-bit word, each slot the 47-bit key in its low bits and t in its top 17 bits;'),
    ('- {sparereq} - {codebytes} - 25,600 - 16,384) / 10) = {tmax}', '- {sparereq} - {codebytes} - 25,600 - 16,384) / 8) = {tmax}'),
])
edit('note_t.md', [
    ('Change against our in-review 76ab339a (B3R7e): the table entry has a 17-bit trail number and a 63-bit key (still 10 bytes), so every trail number the run can reach fits;',
     'Change against our in-review 76ab339a (B3R7e): the table entry is one 64-bit slot, a 47-bit key and a 17-bit trail number (8 bytes; the slot layout of TheTradoor 09fe5fcd and the 47-bit key of b1e6de75, credited), and the age cap is 16 L, so the table holds more entries and every trail number the run can reach fits;'),
    ('| table | {tmax} entries of 10 bytes;', '| table | {tmax} entries of 8 bytes;'),
])
edit('build_all.py', [
    ('R.append("Memory: %d table entries of 10 bytes (%d bytes)', 'R.append("Memory: %d table entries of 8 bytes (%d bytes)'),
    ('keybits=64,', 'keybits=b.KEYBITS,'),
])
