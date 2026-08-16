# -*- coding: utf-8 -*-
"""WorldEditPE 打包脚本：生成发布 zip（behavior_pack + resource_pack）"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = 'v0.1'
OUT = os.path.join(ROOT, 'WorldEditPE_%s.zip' % VERSION)

SKIP_DIRS = {'__pycache__'}
SKIP_EXTS = {'.pyc'}


def add_dir(zf, base, arc_root):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1] in SKIP_EXTS:
                continue
            path = os.path.join(root, f)
            arc = os.path.join(arc_root, os.path.relpath(path, base))
            zf.write(path, arc)


def main():
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_dir(zf, os.path.join(ROOT, 'behavior_pack'), 'behavior_pack')
        add_dir(zf, os.path.join(ROOT, 'resource_pack'), 'resource_pack')
    print('Packaged:', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
