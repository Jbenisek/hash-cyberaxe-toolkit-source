"""Compact a Python program without changing its code: drop comments, cut every docstring to its first line,
drop blank lines and trailing spaces. Refuses unless the code (the AST with docstrings blanked) is identical.
    compact.py IN OUT"""
import ast, io, sys, tokenize

src = open(sys.argv[1], encoding="utf-8").read()
tree = ast.parse(src)
docs = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
        b = node.body[0]
        if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) and isinstance(b.value.value, str):
            docs[(b.lineno, b.col_offset)] = b.value.value
out = []
for t in tokenize.generate_tokens(io.StringIO(src).readline):
    if t.type == tokenize.COMMENT:
        continue
    if t.type == tokenize.STRING and (t.start[0], t.start[1]) in docs:
        first = docs[(t.start[0], t.start[1])].strip().split("\n")[0].strip()
        t = t._replace(string=repr(first))
    out.append(t)
res = tokenize.untokenize(out)
res = "\n".join(l.rstrip() for l in res.split("\n") if l.strip()) + "\n"

def code(s):
    tr = ast.parse(s)
    for node in ast.walk(tr):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            b = node.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) and isinstance(b.value.value, str):
                b.value.value = ""
    return ast.dump(tr)
if code(src) != code(res):
    sys.exit("STOP: the code changed")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(res)
print(f"{len(src.encode()):,} -> {len(res.encode()):,} bytes; code identical apart from docstrings: True; limit 65,536")
