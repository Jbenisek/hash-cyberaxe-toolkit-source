"""vm1mib.py - the '1 MiB VM': run a wasm32 module with linear memory capped at
16 pages (16 x 64 KiB = 1,048,576 B) and count executed instructions (wasmtime fuel).

    from vm1mib import run
    r = run("tests/loop.wasm", "addloop", [1000])
    -> {fuel_used, memory_pages_initial, memory_pages_max, highest_nonzero_byte,
        trapped, trap, result, declared_max_pages}

Refuses (ValueError, before running) a module that: declares no memory max, declares
max > 16 pages, imports a memory, or has more than one memory.
Host I/O (optional): pass host=HostIO(outdir) to give the guest the imports
env.host_write(fd, ptr, len), env.host_open(path_ptr, flags), env.host_close(fd),
env.host_exit(code). Bytes the guest writes go to files on the host, OUTSIDE the
1 MiB guest memory (like a native program streaming to a file).
"""
import os, sys
import wasmtime

PAGE = 65536
MAX_PAGES = 24
MAX_BYTES = MAX_PAGES * PAGE
DEFAULT_FUEL = 1 << 62


def _leb(b, i):
    r = s = 0
    while True:
        x = b[i]; i += 1
        r |= (x & 0x7F) << s; s += 7
        if not x & 0x80:
            return r, i


def memory_limits(wasm: bytes):
    """Parse the binary: return (defined [(min,max|None)], imported_memory_count)."""
    if wasm[:4] != b"\0asm":
        raise ValueError("not a wasm binary")
    i, mems, imported = 8, [], 0
    while i < len(wasm):
        sid = wasm[i]; i += 1
        size, i = _leb(wasm, i); end = i + size
        if sid == 2:  # imports
            n, j = _leb(wasm, i)
            for _ in range(n):
                for _f in range(2):
                    l, j = _leb(wasm, j); j += l
                kind = wasm[j]; j += 1
                if kind == 0: _, j = _leb(wasm, j)
                elif kind == 1:
                    j += 1; fl, j = _leb(wasm, j); _, j = _leb(wasm, j)
                    if fl & 1: _, j = _leb(wasm, j)
                elif kind == 2:
                    imported += 1
                    fl, j = _leb(wasm, j); _, j = _leb(wasm, j)
                    if fl & 1: _, j = _leb(wasm, j)
                elif kind == 3: j += 2
                else: raise ValueError("unknown import kind %d" % kind)
        elif sid == 5:  # memories
            n, j = _leb(wasm, i)
            for _ in range(n):
                fl, j = _leb(wasm, j); mn, j = _leb(wasm, j); mx = None
                if fl & 1: mx, j = _leb(wasm, j)
                if fl & 4: raise ValueError("memory64 not accepted")
                mems.append((mn, mx))
        i = end
    return mems, imported


def check_module(wasm: bytes):
    mems, imported = memory_limits(wasm)
    if imported: raise ValueError("module imports a memory: refused")
    if len(mems) > 1: raise ValueError("more than one memory: refused")
    if not mems: return None, None
    mn, mx = mems[0]
    if mx is None: raise ValueError("memory has no declared max: refused")
    if mx > MAX_PAGES: raise ValueError("declared max %d pages > %d: refused" % (mx, MAX_PAGES))
    return mn, mx


class GuestExit(Exception):
    def __init__(self, code): super().__init__("guest exit %d" % code); self.code = code


class HostIO:
    """Files the guest may open for writing live in outdir (basename only).
    Opening for read is refused (-1). fd 1/2 are captured into self.stdout/self.stderr."""
    def __init__(self, outdir):
        self.outdir = outdir; os.makedirs(outdir, exist_ok=True)
        self.files = {}; self.next = 3; self.stdout = bytearray(); self.stderr = bytearray()
        self.bytes_out = 0

    def define(self, linker, store, mem_getter):
        I32 = wasmtime.ValType.i32()
        def cstr(p):
            m = mem_getter(); d = m.data_ptr(store); s = bytearray()
            while d[p]: s.append(d[p]); p += 1
            return s.decode()
        def w(fd, p, n):
            data = bytes(mem_getter().read(store, p, p + n)); self.bytes_out += n
            if fd == 1: self.stdout += data
            elif fd == 2: self.stderr += data
            elif fd in self.files: self.files[fd].write(data)
            else: return -1
            return n
        def o(p, flags):
            name = os.path.basename(cstr(p))
            if not (flags & 1) or name != cstr(p): return -1   # write-only, plain names
            mode = "ab" if flags & 0o2000 else "wb"
            f = open(os.path.join(self.outdir, name), mode)
            fd = self.next; self.next += 1; self.files[fd] = f; return fd
        def c(fd):
            f = self.files.pop(fd, None)
            if f: f.close(); return 0
            return -1
        def x(code): raise GuestExit(code)
        F = wasmtime.FuncType
        linker.define_func("env", "host_write", F([I32, I32, I32], [I32]), w)
        linker.define_func("env", "host_open", F([I32, I32], [I32]), o)
        linker.define_func("env", "host_close", F([I32], [I32]), c)
        linker.define_func("env", "host_exit", F([I32], []), x)

    def close(self):
        for f in self.files.values(): f.close()
        self.files.clear()


def run(module, export, args=(), host=None, fuel=DEFAULT_FUEL, setup=None):
    """module: path or bytes. setup(store, instance, memory) runs before the call
    (e.g. to copy inputs into guest memory); its fuel is not counted (it runs host code)."""
    wasm = open(module, "rb").read() if isinstance(module, str) else bytes(module)
    mn, mx = check_module(wasm)
    cfg = wasmtime.Config(); cfg.consume_fuel = True
    eng = wasmtime.Engine(cfg); store = wasmtime.Store(eng)
    store.set_limits(memory_size=MAX_BYTES)          # second, runtime guard
    mod = wasmtime.Module(eng, wasm)
    linker = wasmtime.Linker(eng)
    holder = {}
    if host is not None: host.define(linker, store, lambda: holder["mem"])
    store.set_fuel(fuel)
    inst = linker.instantiate(store, mod)          # data segments: host copy, start fn would burn fuel
    ex = inst.exports(store)
    mem = ex["memory"] if "memory" in ex else None
    holder["mem"] = mem
    if setup: setup(store, inst, mem)
    f0 = store.get_fuel()
    out = {"declared_min_pages": mn, "declared_max_pages": mx, "trapped": False, "trap": None,
           "result": None, "exit_code": None}
    try:
        out["result"] = ex[export](store, *args)
    except GuestExit as e:
        out["exit_code"] = e.code
        if e.code: out["trapped"] = True; out["trap"] = "guest exit %d" % e.code
    except (wasmtime.Trap, wasmtime.WasmtimeError) as e:
        if isinstance(e.__cause__ if e.__cause__ else None, GuestExit) or "guest exit" in str(e):
            code = int(str(e).split("guest exit")[1].split()[0]) if "guest exit" in str(e) else -1
            out["exit_code"] = code
            if code: out["trapped"] = True; out["trap"] = "guest exit %d" % code
        else:
            out["trapped"] = True
            ls = [l.strip() for l in str(e).splitlines() if l.strip()]
            out["trap"] = next((l for l in ls if "wasm trap" in l or "out of bounds" in l or "fuel" in l), ls[-1])
    out["fuel_used"] = f0 - store.get_fuel()
    # wasmtime does not flush spent fuel on a memory/other trap (reads 0): report null. Fuel-exhaustion traps
    # ("all fuel consumed") and guest exits are exact.
    if out["trapped"] and not (str(out["trap"]).startswith("guest exit") or "fuel" in str(out["trap"])):
        out["fuel_used"] = None; out["fuel_note"] = "unknown after trap: " + str(out["trap"])[:60]
    if mem is not None:
        pages = mem.size(store); out["memory_pages_max"] = pages   # memory only grows: final = high-water
        d = bytes(mem.read(store, 0, pages * PAGE))
        nz = len(d.rstrip(b"\0")); out["highest_nonzero_byte"] = nz
    out["_store"], out["_inst"], out["_mem"] = store, inst, mem
    if host: host.close()
    return out


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


if __name__ == "__main__":
    # vm1mib.py module.wasm export [int args...]
    r = run(sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3:]])
    print(public(r))
