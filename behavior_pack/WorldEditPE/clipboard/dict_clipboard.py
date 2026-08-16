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
# DictClipboard - clipboard stored as {relative_pos: block_dict}

from ..utils.blocks import is_air, AIR


class DictClipboard(object):
    """Stores copied blocks keyed by their position relative to the copy origin."""

    def __init__(self):
        super(DictClipboard, self).__init__()
        self._blocks = {}      # relative_pos (tuple) -> block dict
        self._origin = None    # world position that was the copy origin

    @property
    def origin(self):
        return self._origin

    @property
    def blocks(self):
        return self._blocks

    def store(self, blocks, origin):
        """Store blocks with positions relative to *origin*."""
        self._origin = tuple(origin) if origin is not None else None
        if self._origin is None:
            self._blocks = {}
            return
        self._blocks = {}
        for world_pos, block in blocks.items():
            rel_pos = (
                world_pos[0] - self._origin[0],
                world_pos[1] - self._origin[1],
                world_pos[2] - self._origin[2]
            )
            self._blocks[rel_pos] = block

    def paste(self, target_origin, skip_air=True):
        """Return a dict of {world_pos: block_dict} for pasting at *target_origin*."""
        result = {}
        if self._origin is None or not self._blocks:
            return result
        for rel_pos, block in self._blocks.items():
            if skip_air and is_air(block):
                continue
            world_pos = (
                target_origin[0] + rel_pos[0],
                target_origin[1] + rel_pos[1],
                target_origin[2] + rel_pos[2]
            )
            result[world_pos] = block
        return result

    def rotate(self, yaw_degrees):
        """Rotate clipboard blocks around Y axis (relative origin).
        Rotation: 90° -> (x,z) -> (-z,x)
                 180° -> (x,z) -> (-x,-z)
                 270° -> (x,z) -> (z,-x)
        """
        if yaw_degrees % 360 == 0:
            return
        new_blocks = {}
        for (x, y, z), block in self._blocks.items():
            d = yaw_degrees % 360
            if d == 90:
                nx, nz = -z, x
            elif d == 180:
                nx, nz = -x, -z
            elif d == 270:
                nx, nz = z, -x
            else:
                nx, nz = x, z
            new_blocks[(nx, y, nz)] = block
        self._blocks = new_blocks

    def flip(self, direction_axis):
        """Flip clipboard blocks relative to the origin (player's copy position).
        Mirrors around the origin point, matching WorldEdit behavior.
        direction: 'north'/'south' -> flip z (z -> -z)
                   'east'/'west'   -> flip x (x -> -x)
                   'up'/'down'     -> flip y (y -> -y)
        """
        if not self._blocks:
            return
        new_blocks = {}
        for (x, y, z), block in self._blocks.items():
            nx, ny, nz = x, y, z
            axis = direction_axis.lower()
            if axis in ('north', 'south', 'z'):
                nz = -z
            elif axis in ('east', 'west', 'x'):
                nx = -x
            elif axis in ('up', 'down', 'y'):
                ny = -y
            new_blocks[(nx, ny, nz)] = block
        self._blocks = new_blocks

    def is_empty(self):
        return len(self._blocks) == 0

    def clear(self):
        self._blocks = {}
        self._origin = None

    def __len__(self):
        return len(self._blocks)

    def __repr__(self):
        return "DictClipboard(%d blocks)" % len(self._blocks)
