s = open('certb_fast.cu', encoding='utf-8').read()
code = open('certify_snippet.cu', encoding='utf-8').read()
marker = '// ------------------------------------------------------------------ Taylor-shift midpoint polynomial'
assert marker in s
s = s.replace(marker, code + marker, 1)
main_old = '    const char *gpath = opt_str(argc, argv, "--g", nullptr);'
main_new = '''    if (mode == "certify") {   // certify --f f.bin --cofactor co.bin (--g g.bin | --F F.bin --center c) --outdir dir
        std::vector<fp> fh = read_poly(opt_str(argc, argv, "--f", "f.bin")), coh = read_poly(opt_str(argc, argv, "--cofactor", "co.bin")), gh2;
        const char *gp2 = opt_str(argc, argv, "--g", nullptr), *cen = opt_str(argc, argv, "--center", "none");
        if (gp2) gh2 = read_poly(gp2);
        else { uint64_t cl[4]; parse_dec(cen, cl); gh2 = build_center_poly(c, read_poly(opt_str(argc, argv, "--F", "tests/data/F_j0.bin")), cl); }
        ctx_setup_modulus(c, fh);
        return certify(c, gh2, fh, coh, cen, opt_int(argc, argv, "--line", 0), opt_int(argc, argv, "--trial", 0), opt_str(argc, argv, "--outdir", "."));
    }
''' + main_old
assert main_old in s
s = s.replace(main_old, main_new, 1)
open('certb_fast.cu', 'w', encoding='utf-8').write(s)
