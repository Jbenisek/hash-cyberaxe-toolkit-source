"""Crude PDF text extraction (zlib streams + Tj/TJ operators). Windows python, stdlib only.
Usage: python pdftext.py in.pdf out.txt"""
import re, sys, zlib

def strings_from_stream(s):
    out = []
    # TJ arrays and Tj strings
    for m in re.finditer(rb'\[(.*?)\]\s*TJ|\((.*?)(?<!\\)\)\s*Tj|(T\*|Td|TD|ET)', s, re.S):
        if m.group(1) is not None:
            parts = re.findall(rb'\((.*?)(?<!\\)\)|(-?\d+\.?\d*)', m.group(1), re.S)
            buf = b''
            for txt, num in parts:
                if txt:
                    buf += txt
                elif num:
                    try:
                        if float(num) < -200:
                            buf += b' '
                    except ValueError:
                        pass
            out.append(buf)
        elif m.group(2) is not None:
            out.append(m.group(2))
        else:
            out.append(b'\n' if m.group(3) in (b'ET', b'T*') else b' ')
    return b''.join(out)

def main(inp, outp):
    data = open(inp, 'rb').read()
    res = []
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S):
        raw = m.group(1)
        try:
            dec = zlib.decompress(raw)
        except Exception:
            continue
        if b'Tj' in dec or b'TJ' in dec:
            res.append(strings_from_stream(dec))
    txt = b'\n'.join(res)
    txt = txt.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
    open(outp, 'wb').write(txt)
    print(outp, len(txt))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
