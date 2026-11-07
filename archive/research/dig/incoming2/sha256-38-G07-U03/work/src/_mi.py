class MI(Machine):
    def run(s, code, maxops=None):
        c, lab, r = code.c, code.lab, s.r; pc = 0; n = len(c); mem = s.mem
        def v(x): return x if isinstance(x, int) else r.get(x, 0)
        ops = 0
        isi = lambda x: isinstance(x, int)
        while pc < n:
            ins = c[pc]; op = ins[0]; pc += 1
            if op in ('add', 'sub', 'and', 'or', 'xor'): ops += isi(ins[2]) + isi(ins[3])
            elif op == 'rsub': ops += 1 + isi(ins[3])
            elif op == 'bne': ops += isi(ins[2])
            elif op == 'sti': ops += isi(ins[2])
            if op == 'add': r[ins[1]] = (v(ins[2]) + v(ins[3])) & WORD; ops += 1
            elif op == 'sub': r[ins[1]] = (v(ins[2]) - v(ins[3])) & WORD; ops += 1
            elif op == 'rsub': r[ins[1]] = (ins[2] - v(ins[3])) & WORD; ops += 1
            elif op == 'and': r[ins[1]] = v(ins[2]) & v(ins[3]); ops += 1
            elif op == 'or': r[ins[1]] = v(ins[2]) | v(ins[3]); ops += 1
            elif op == 'xor': r[ins[1]] = v(ins[2]) ^ v(ins[3]); ops += 1
            elif op == 'shl': r[ins[1]] = (v(ins[2]) << ins[3]) & WORD; ops += 1
            elif op == 'shr': r[ins[1]] = v(ins[2]) >> ins[3]; ops += 1
            elif op == 'ld': r[ins[1]] = s.load(v(ins[2])); ops += 1
            elif op == 'ldi': r[ins[1]] = mem.get(ins[2], 0); ops += 1
            elif op == 'sti': mem[ins[1]] = v(ins[2]); ops += 1
            elif op == 'li': r[ins[1]] = ins[2]; ops += 1
            elif op == 'st': s.store(v(ins[1]), v(ins[2])); ops += 1
            elif op == 'bz': ops += 2; pc = lab[ins[2]] if v(ins[1]) == 0 else pc
            elif op == 'bnz': ops += 2; pc = lab[ins[2]] if v(ins[1]) != 0 else pc
            elif op == 'bne': ops += 2; pc = lab[ins[3]] if v(ins[1]) != v(ins[2]) else pc
            elif op == 'jmp': ops += 1; pc = lab[ins[1]]
            elif op == 'rand': r[ins[1]] = s.rw.pop(0); ops += 1
            elif op == 'f38':
                s.units += 1; m0 = [r[x] for x in ins[1]]; s.m0 = m0
                cv = s.cvforce if s.cvforce is not None else compress(IV, m0); s.cv = cv
                for x, y in zip(ins[2], cv): r[x] = y
            elif op == 'succ': s.succ = (ins[1], v(ins[2])); s.succ_ops = s.ops + ops; break
            elif op == 'halt_ok': break
            elif op == 'obs': s.obs.append(v(ins[1]))
            elif op == 'mark': s.marks.append(ins[1]); s.mark_ops.append((ins[1], s.ops + ops))
        s.ops += ops
