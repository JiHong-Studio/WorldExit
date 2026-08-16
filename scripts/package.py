# -*- coding: utf-8 -*-
# WorldEditPE - WorldEdit for NetEase Minecraft (Bedrock)
# Copyright (C) 2026 JiHong-Studio (ChengXing507 & Ecaps)
# This file is part of WorldEditPE.
# WorldEditPE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""WorldEditPE 打包脚本：生成发布 zip（仅 behavior_pack）"""
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
    print('Packaged:', OUT, os.path.getsize(OUT), 'bytes')


if __name__ == '__main__':
    main()
