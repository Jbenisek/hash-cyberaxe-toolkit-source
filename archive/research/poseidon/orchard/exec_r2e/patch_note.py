s = open('note_template.md').read()


def sub(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)


sub("256-bit loads and stores with one address operation each, loop control at 3 operations per iteration plus 2 on exit for every loop that is not written out straight-line, other control operations,",
    "256-bit loads and stores, loop and address work at one half operation per butterfly and per element of an unrolled loop (half units rounded up to a whole operation at the end of each stage visit), other control operations,")
i = s.index("Loops. The loops that are genuinely unrolled")
j = s.index("Memory. The executable is linked statically")
s = s[:i] + ("Loops. The loop and address work follows the price list of the public r = 2 entries: one half unit per butterfly of the generated straight-line transform kernels and one half unit per element of every unrolled per-element loop; every other executed index or control operation is charged by a CONTROL statement next to it (proof.md section 4.2). The leading coefficient of g is tested for zero by a counted test before it is inverted; a centre where it vanished would be skipped.\n") + s[j:]
sub("under the full loop and address rule (an address operation for every load and store, 3 per loop iteration and 2 per loop exit);", "under the half-unit loop and address rule of the public r = 2 entries;")
sub("The one structural assumption of the cost model is a register file", "The one structural assumption of the cost model is a register file")
s = s.rstrip('\n') + "\n\nPoints raised by the earlier review of this entry, and where they are answered. (1) Ledger and trial table: the half units of loop and address work are now inside every stage row and every trial row (rounded up per stage visit), and the program prints one total with the line RECONCILE: stages, trials and counters are equal. (2) Conversions and output: fp_from_limbs and fp_to_limbs now increment the multiplication counter, so every conversion is in the counts, and the canonical hexadecimal encoding of the output is a counted stage H inside the total; there is no bound for uncounted work, and the self-check that was previously left uncounted is removed from the program. (3) Memory: the whole statically linked image is counted, the heap term is the allocator footprint read with mallinfo2() (headers included; the number of live allocations at the peak and the header bytes are stated in proof.md section 7), and the flat 4,096-byte allowance is gone. (4) Leading coefficient: its value is stated in proof.md section 2.3 and the program tests it for zero by a counted test before the inversion and skips the centre if it were zero. (5) The two dimension typos of the proof text are corrected.\n"
open('note_template.md', 'w', newline='\n').write(s)
print('ok')
