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
# Fill and drain algorithms for WorldEditPE
# These functions return a dict of {pos_tuple: block_dict} changes.

from ..utils.blocks import is_air, is_liquid, AIR


def fill_xz(operator, center, pattern, radius, depth, recursive=False):
    """Fill an area downward from *center*.

    Args:
        operator: a WorldOperator instance.
        center: (x, y, z) starting position.
        pattern: block dict to place.
        radius: horizontal radius to fill.
        depth: how far down to fill.
        recursive: if True, continue filling into adjacent air below.

    Returns a dict of {pos_tuple: block_dict} with the changes.
    """
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    d = int(depth)
    changes = {}

    for x in xrange(cx - r, cx + r + 1):
        for z in xrange(cz - r, cz + r + 1):
            if (x - cx) * (x - cx) + (z - cz) * (z - cz) > r * r:
                continue
            # Find the first air block downward from the surface
            y = cy
            while y > cy - d:
                block = operator.get_block((x, y, z))
                if block is None:
                    break
                if is_air(block):
                    changes[(x, y, z)] = pattern
                    if recursive:
                        # Continue down in same column while air below
                        yy = y - 1
                        while yy > cy - d:
                            b = operator.get_block((x, yy, z))
                            if b is None:
                                break
                            if is_air(b):
                                changes[(x, yy, z)] = pattern
                                yy -= 1
                            else:
                                break
                    break
                y -= 1
    return changes


def drain_area(operator, center, radius):
    """Drain liquids in a cylindrical area around *center*.

    Args:
        operator: a WorldOperator instance.
        center: (x, y, z) centre of the area.
        radius: horizontal radius to drain.

    Returns a dict of {pos_tuple: block_dict} with the changes (blocks set to air).
    """
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    r2 = r * r
    changes = {}

    for x in xrange(cx - r, cx + r + 1):
        dx = x - cx
        dx2 = dx * dx
        for z in xrange(cz - r, cz + r + 1):
            dz = z - cz
            if dx2 + dz * dz > r2:
                continue
            # Scan a reasonable vertical range (e.g. +/- 30 blocks)
            for y in xrange(cy - 30, cy + 30):
                block = operator.get_block((x, y, z))
                if block is None:
                    continue
                if is_liquid(block):
                    changes[(x, y, z)] = AIR
    return changes
