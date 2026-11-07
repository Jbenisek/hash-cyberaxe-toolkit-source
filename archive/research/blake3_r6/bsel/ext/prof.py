import sys, resource, gc
sys.dont_write_bytecode=True
import bsrho as b
def rss(t): print(t, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, "MB", flush=True)
rss("import")
g,_=b.trace(18)[:2]
rss("trace18")
st=b.Step(18)
rss("Step18")
e=b.Engine(18); rss("Engine18")
