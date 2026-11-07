if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        from math import log2
        print_ledger(ledger())
        for R in (512, 256):
            pR = plan(256, None, None, R)
            if pR is None:
                print("smaller file R = %d: spill ops per batch %d, no table fits in 2^20 bytes" % (R, step256().spill_ops(R)))
                continue
            lgR = ledger(pR, None, R)
            print("smaller file R = %d: spill ops per batch %d, body %d, tmax %d, Tp %d, time_log2 %.5f, success lower bound %.4f" % (
                R, step256().spill_ops(R), lgR["body"], pR["tmax"], pR["Tp"], log2(lgR["total"] / UNIT), loss(pR)["P_lower"]))
        st = step256()
        ph, per, rest, body, code, tmax = machine_constants(st)
        print("PH", ph, "stage 1 per batch", per, "passing extra", rest, "body", body, "code bytes", code, "tmax", tmax, "key bits", keybits(tmax))
        ph1, ph2 = phase_bytes(code, tmax)
        print("setup phase bytes", ph1, "search phase bytes", ph2, "limit", MEM_LIMIT, "fits", max(ph1, ph2) <= MEM_LIMIT)
        print("generator scratch, use counts, nodes", gen_scratch(), "image", GEN_CODE * INSTR_BYTES, "calls (one pass)", st.gen_calls)
        print("recovery circuit operations", packed_circuit(st.qwords)[1], "registers", allocate(st)[1], "q (hex)", "%064x" % st.qint)
    elif arg == "--choose-key":
        choose_key()
    elif arg == "--gen-c":
        sys.stdout.write(GEN_C)
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
