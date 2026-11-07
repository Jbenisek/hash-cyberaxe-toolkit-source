import json,os
ev="research/dig/incoming2/blake3-r2-G07-U06/work/sens.py (+ledger_ext.py = proof ledger program, copied unmodified from blake3-r2-G07-U02/work); dossier 5a08fffa proof-numbered.md ledger"
base=" Package 5a08fffa NEW ledger, N=87,167,447,489,133,596,522, time_log2 57.49223042 (k=574922, reproduced by the program). Exact integer ledger arithmetic, one parameter changed at a time, bits = log2(N_changed/N). Ledger program only; the shipped program was not metered here (R4 only). Parameters not verified; sensitivity, not a gain claim. Note the cell text says MU 4459 declared, program NEW has 4425."
C={}
C["LIVE"]=("u_live = setup 21 + piece 10 x 16 + wrap 0 + 19 x 16 (= 485 units per live block)","R4 sensitivity of live-block setup/pieces/wrap/ranges (bits)",
 "EXACT: 3.450e-5 bit per unit of u_live per live block (live blocks L_B=2.0845e15 plus 16*S; 85.4% of N is the WB word-block row). Per parameter: setup 21->27 +0.000207, ->22 +0.000035, ->20 -0.000035; piece 10->9 -0.000552 (->11 +0.000552); wrap 0->1 +0.000035; ranges 16->15 -0.000656 (->17 +0.000655). All single changes below 0.001 bit.")
C["PASSL"]=("passing lane u_pass 39 + 1 + 12 (+21 scan) per passing word","R4 sensitivity of the passing lane (bits)",
 "EXACT: 3.95e-4 bit per unit of u_pass (also per unit of u_pass_x or of the 21 scan). u_pass 39->31 -0.003161; 39->27 -0.004745; 39->35 -0.001580; u_pass_x 1->0 -0.000395, 1->12 +0.004336. The older audit shortcut '31->27' read as partial words per live block (partial 31->27) is -0.000552; read as u_pass 31->27 it is -0.001584 from 31. Largest slack candidate in this unit: u_pass 39->27 = -0.0047 bit.")
C["WCTX"]=("per-context words (ceil((2^19+186*16)/7) x 46, partial 4*31*16) and descriptor table","R4 sensitivity of per-context words and descriptor table (bits)",
 "EXACT: the whole W_CTX row is 37,029,080 units = 4.2e-13 of N; the descriptor-table change 48,896->5,760 (-43,136 units) moves time by -6.4e-16 bit (nothing). The per-live-block word terms matter: words per live block 186->179 -0.001588 (->193 +0.001586; ->0 -0.042799 = ceiling of the whole 186 L term); u_word 46->45 -0.018118 (->47 +0.017893, 0.0181 bit per unit); partial 31->27 -0.000552.")
C["CREDIT"]=("solver credit: MU millionths, capx 23151, 14 L_C","R4 sensitivity of solver credit (bits)",
 "EXACT: credit = 4,749,926,824,615,254,638 = 5.449% of N in the program (MU term mc = 4.748e18 dominates; 14 L_C = 1.7e11 and the sqrt term 1.5e15 are negligible: capx 23151->23150 is under 1e-9 bit). MU 4425->4459 (the declared value in the cell text) +0.000604; MU 4425->4000 -0.007569; ->5000 +0.010178; the whole MU credit gone (MU->0) -0.080819 bit = ceiling. Per 100 millionths of MU about 0.0023 bit. The cell's 6.7%-25.8% range is other lines; not recomputed.")
C["ONCE3"]=("ONCE row 1.13e15 (ONCE_BASE 1,128,752,545,267,752) plus 12 add-ons = 2,537,846,523,297,832; BUILD of the 16 class lists 8.34e14","R4 sensitivity of the ONCE row and class-list BUILD (bits)",
 "EXACT: the program's ONCE is 2.5378e15 (ONCE_BASE 1.1288e15 + add-ons 1.4091e15, mostly 2^50 and 2^48 terms) = 0.0029% of N. Removing all add-ons -0.000023 bit; -1e14 units -0.000002; -1e15 -0.00002; 1% of ONCE below 1e-6 bit. The 8.34e14 BUILD is a part of ONCE_BASE and cannot move the score by more than 3e-5 bit even if free.")
C["FINAL3"]=("final: (430+64) x 2 + final_per_chunk 128 x 2^48 + 430 x 2^38","R4 sensitivity of the final row (bits)",
 "EXACT: final = 3.6147e16 = 0.0415% of N; 4.659e-6 bit per unit of final_per_chunk (2^48 each). 128->127 -0.000005; 128->96 -0.000149; 128->64 -0.000298; 128->512 (BASE) +0.001788. The (430+64)*2 and 430*2^38 terms are below 1e-9 bit. Whole final row at most 0.0006 bit.")
os.makedirs("..",exist_ok=True)
for k,(obj,q,num) in C.items():
    cid=f"blake3-r2|LEDGER.{k}|LEDGER|R4"
    d=dict(hash="blake3-r2",row_i=None,row_j=None,object=obj,question=q,labels=["N"],status="COMPUTED",number=num,
      source="our workflow: scan-once-wave2",own_test=True,evidence=ev,date="2026-10-12",lever=False,gain_bits=None,
      notes="universe cell "+cid+"."+base,topic=cid)
    json.dump(d,open(f"../blake3-r2_LEDGER.{k}_LEDGER_R4.json","w",encoding="utf-8"),indent=1)
