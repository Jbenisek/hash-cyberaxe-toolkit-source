"""Read an exact public artifact from a local or HTTPS compact library.

python extract_compact_file.py LIBRARY_ROOT archive/research/path/file.py --output file.py
Without --output the original bytes go to stdout. No artifact is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen


def bucket(path):
    value=2166136261
    raw=path.encode('utf-16-le')
    for i in range(0,len(raw),2):value=((value^int.from_bytes(raw[i:i+2],'little'))*16777619)&0xffffffff
    return format(value>>28,'x')


def read_public(root, path):
    path=path.replace('\\','/')
    if path.startswith('/') or '..' in path.split('/'):
        raise ValueError('Use an indexed path relative to the library root.')
    remote=str(root).startswith(('http://','https://'))
    def load(name):
        if remote:
            with urlopen(str(root).rstrip('/')+'/'+name,timeout=60) as response:return response.read()
        return (Path(root)/name).read_bytes()
    if not remote and (Path(root)/path).is_file():return load(path)
    parts=path.split('/')
    if (path.startswith('data/guides/') and path.endswith('.json')) or (path.startswith(('agent/tools/','agent/datasets/')) and path.endswith('.md')):
        gid=Path(path).stem
        if len(gid)!=20 or any(c not in '0123456789abcdef' for c in gid):raise ValueError('Invalid guide ID')
        group=json.loads(load('data/guide-groups/'+gid[:2]+'.json'))
        return group['json_text' if path.endswith('.json') else 'markdown'][gid].encode('utf-8')
    if path.startswith('archive/'):
        manifest=json.loads(load('data/compact/manifest.json'))
        if path in manifest['kept_archive_paths']:return load(path)
        entry=json.loads(load('data/compact/files-'+bucket(path)+'.json'))[path]
        bundle,offset,size,pin,mime=entry
        if remote:
            if not size:raw=b''
            else:
                request=Request(str(root).rstrip('/')+'/'+bundle,headers={'Range':f'bytes={offset}-{offset+size-1}'})
                with urlopen(request,timeout=60) as response:
                    content=response.read();raw=content if response.status==206 else content[offset:offset+size]
        else:
            with (Path(root)/bundle).open('rb') as source:source.seek(offset);raw=source.read(size)
        if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('SHA-256 mismatch; refusing altered artifact')
        return raw
    return load(path)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('library_root');parser.add_argument('artifact_path');parser.add_argument('--output',type=Path);args=parser.parse_args()
    raw=read_public(args.library_root,args.artifact_path)
    if args.output:args.output.write_bytes(raw)
    else:sys.stdout.buffer.write(raw)
