# -*- coding: utf-8 -*-
# WorldEditPE - WorldEdit for NetEase Minecraft (Bedrock)
# Copyright (C) 2026 JiHong-Studio (ChengXing507 & Ecaps)
# This file is part of WorldEditPE.
# WorldEditPE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# WorldEditPE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with WorldEditPE.  If not, see <https://www.gnu.org/licenses/>.
# Line / wall / outline drawing algorithms
# These functions return a dict of {pos_tuple: block_dict} with the changes.


def draw_line(pos1, pos2, block):
    """Return a dict of {pos_tuple: block_dict} for the 3D line from pos1 to pos2.

    *pos1*, *pos2* are (x, y, z) tuples. Uses a 3D Bresenham algorithm.
    """
    x0, y0, z0 = int(pos1[0]), int(pos1[1]), int(pos1[2])
    x1, y1, z1 = int(pos2[0]), int(pos2[1]), int(pos2[2])
    changes = {}

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    dz = abs(z1 - z0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    sz = 1 if z0 < z1 else -1

    # Dominant axis handling
    if dx >= dy and dx >= dz:
        err1 = 2 * dy - dx
        err2 = 2 * dz - dx
        while x0 != x1:
            changes[(x0, y0, z0)] = block
            if err1 > 0:
                y0 += sy
                err1 -= 2 * dx
            if err2 > 0:
                z0 += sz
                err2 -= 2 * dx
            err1 += 2 * dy
            err2 += 2 * dz
            x0 += sx
    elif dy >= dx and dy >= dz:
        err1 = 2 * dx - dy
        err2 = 2 * dz - dy
        while y0 != y1:
            changes[(x0, y0, z0)] = block
            if err1 > 0:
                x0 += sx
                err1 -= 2 * dy
            if err2 > 0:
                z0 += sz
                err2 -= 2 * dy
            err1 += 2 * dx
            err2 += 2 * dz
            y0 += sy
    else:
        err1 = 2 * dx - dz
        err2 = 2 * dy - dz
        while z0 != z1:
            changes[(x0, y0, z0)] = block
            if err1 > 0:
                x0 += sx
                err1 -= 2 * dz
            if err2 > 0:
                y0 += sy
                err2 -= 2 * dz
            err1 += 2 * dx
            err2 += 2 * dy
            z0 += sz

    changes[(x0, y0, z0)] = block
    return changes


def draw_walls(minp, maxp, block):
    """Return a dict of {pos_tuple: block_dict} for the 4 vertical walls of a box.

    *minp*, *maxp* are (x, y, z) tuples.
    """
    mnx, mny, mnz = int(minp[0]), int(minp[1]), int(minp[2])
    mxx, mxy, mxz = int(maxp[0]), int(maxp[1]), int(maxp[2])
    changes = {}

    for x in xrange(mnx, mxx + 1):
        for y in xrange(mny, mxy + 1):
            changes[(x, y, mnz)] = block
            if mxz != mnz:
                changes[(x, y, mxz)] = block
    for z in xrange(mnz + 1, mxz):
        for y in xrange(mny, mxy + 1):
            changes[(mnx, y, z)] = block
            if mxx != mnx:
                changes[(mxx, y, z)] = block
    return changes


def draw_outline(minp, maxp, block):
    """Return a dict of {pos_tuple: block_dict} for the full edge outline of a box.

    *minp*, *maxp* are (x, y, z) tuples.
    """
    mnx, mny, mnz = int(minp[0]), int(minp[1]), int(minp[2])
    mxx, mxy, mxz = int(maxp[0]), int(maxp[1]), int(maxp[2])
    changes = {}

    # Vertical edges (4)
    for x, z in ((mnx, mnz), (mnx, mxz), (mxx, mnz), (mxx, mxz)):
        for y in xrange(mny, mxy + 1):
            changes[(x, y, z)] = block

    # Bottom ring
    for x in xrange(mnx, mxx + 1):
        changes[(x, mny, mnz)] = block
        if mxz != mnz:
            changes[(x, mny, mxz)] = block
    for z in xrange(mnz + 1, mxz):
        changes[(mnx, mny, z)] = block
        if mxx != mnx:
            changes[(mxx, mny, z)] = block

    # Top ring
    if mxy != mny:
        for x in xrange(mnx, mxx + 1):
            changes[(x, mxy, mnz)] = block
            if mxz != mnz:
                changes[(x, mxy, mxz)] = block
        for z in xrange(mnz + 1, mxz):
            changes[(mnx, mxy, z)] = block
            if mxx != mnx:
                changes[(mxx, mxy, z)] = block

    return changes
