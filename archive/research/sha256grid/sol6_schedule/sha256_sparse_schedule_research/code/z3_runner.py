import ctypes as C,sys,json,time
z=C.CDLL('libz3.so.4')
def f(name,ret,args):
 q=getattr(z,name);q.restype=ret;q.argtypes=args;return q
V=C.c_void_p;S=C.c_char_p;I=C.c_int
mkcfg=f('Z3_mk_config',V,[]);setpar=f('Z3_set_param_value',None,[V,S,S]);mkctx=f('Z3_mk_context',V,[V]);mksolver=f('Z3_mk_solver',V,[V]);inc=f('Z3_solver_inc_ref',None,[V,V]);fr=f('Z3_solver_from_string',None,[V,V,S]);check=f('Z3_solver_check',I,[V,V]);getmodel=f('Z3_solver_get_model',V,[V,V]);modstr=f('Z3_model_to_string',S,[V,V]);reason=f('Z3_solver_get_reason_unknown',S,[V,V]);stats=f('Z3_solver_get_statistics',V,[V,V]);statstr=f('Z3_stats_to_string',S,[V,V])
cfg=mkcfg();setpar(cfg,b'timeout',str(int(sys.argv[3]) if len(sys.argv)>3 else 30000).encode());ctx=mkctx(cfg);s=mksolver(ctx)
if len(sys.argv)>4:
 tactic=f('Z3_mk_tactic',V,[V,S])(ctx,sys.argv[4].encode())
 s=f('Z3_mk_solver_from_tactic',V,[V,V])(ctx,tactic)
inc(ctx,s)
params=f('Z3_mk_params',V,[V])(ctx)
f('Z3_params_inc_ref',None,[V,V])(ctx,params)
sym=f('Z3_mk_string_symbol',V,[V,S])(ctx,b'timeout')
f('Z3_params_set_uint',None,[V,V,V,C.c_uint])(ctx,params,sym,int(sys.argv[3]) if len(sys.argv)>3 else 30000)
f('Z3_solver_set_params',None,[V,V,V])(ctx,s,params)
t=time.process_time();w=time.perf_counter();fr(ctx,s,open(sys.argv[1],'rb').read());print('parsed',flush=True);r=check(ctx,s)
out={'status':{1:'SAT',-1:'UNSAT',0:'UNKNOWN'}[r],'cpu_seconds':time.process_time()-t,'wall_seconds':time.perf_counter()-w,'stats':statstr(ctx,stats(ctx,s)).decode()}
if r==1:out['model']=modstr(ctx,getmodel(ctx,s)).decode()
if r==0:out['reason']=reason(ctx,s).decode()
open(sys.argv[2],'w').write(json.dumps(out,indent=2));print(out['status'],out['cpu_seconds'],flush=True)
