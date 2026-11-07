def run_rolled(flat, words):
    """Interpreter of the flat listing (loop control I, D, C, Z, J as in the proof); returns the 8 output registers."""
    R, pc, cnt, flag, top = [0] * 35, 0, 0, False, 0
    R[24:32] = words
    jend = max(i for i, c in enumerate(flat) if c[0] == "J")
    while pc < len(flat):
        o, d, a, b = flat[pc]
        pc += 1
        if o == "I":
            cnt, top = ROUNDS, pc
        elif o == "D":
            cnt -= 1
        elif o == "C":
            flag = cnt == 0
        elif o == "Z":
            pc = jend + 1 if flag else pc
        elif o == "J":
            pc = top
        elif o == "l":
            R[d] = a
        else:
            R[d] = {"+": lambda: R[a] + R[b], "^": lambda: R[a] ^ R[b], "|": lambda: R[a] | R[b], "a": lambda: R[a] & b, "x": lambda: R[a] ^ b,
                    "&>": lambda: R[a] >> b, "&<": lambda: R[a] << b, "=": lambda: R[a]}[o]()
    return tuple(R[:8])


