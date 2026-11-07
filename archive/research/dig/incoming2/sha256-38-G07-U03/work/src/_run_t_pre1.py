import sys, os
sys.path.insert(0, '../baseA'); sys.path.insert(0, '.'); sys.dont_write_bytecode = True
from vtpre import *
class MachineP(Machine):
    def load(s, addr):
        if addr in s.mem: return s.mem[addr]
        t = addr >> 150
        return s.tab[addr] if t in (3, 4) and addr in s.tab else 0
src = open('t_pre1.py').read().replace("'../runs/pre1.json'", "'../runs/pre1_check.json'")
exec(compile(src, 't_pre1.py', 'exec'))
