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
"""
选区管理器
对应 WorldEdit 的 CuboidRegion / RegionSelector
"""

from WorldEditPE.utils.vectors import BlockVector3


class SelectionState(object):
    """
    玩家选区状态
    存储 pos1, pos2 以及选区类型
    """

    CUBOID = 'cuboid'

    def __init__(self):
        self._pos1 = None
        self._pos2 = None
        self._type = self.CUBOID
        self._dimension_id = 0

    def set_pos1(self, pos, dimension_id=0):
        if not isinstance(pos, BlockVector3):
            pos = BlockVector3.from_tuple(pos)
        self._pos1 = pos
        self._dimension_id = dimension_id

    def set_pos2(self, pos, dimension_id=0):
        if not isinstance(pos, BlockVector3):
            pos = BlockVector3.from_tuple(pos)
        self._pos2 = pos
        if dimension_id != 0:
            self._dimension_id = dimension_id

    @property
    def pos1(self):
        return self._pos1

    @property
    def pos2(self):
        return self._pos2

    @property
    def dimension_id(self):
        return self._dimension_id

    def is_complete(self):
        return self._pos1 is not None and self._pos2 is not None

    def get_volume(self):
        if not self.is_complete():
            return 0
        minp = BlockVector3.min(self._pos1, self._pos2)
        maxp = BlockVector3.max(self._pos1, self._pos2)
        dx = maxp.x - minp.x + 1
        dy = maxp.y - minp.y + 1
        dz = maxp.z - minp.z + 1
        return dx * dy * dz

    def iter_positions(self):
        if not self.is_complete():
            return
        minp = BlockVector3.min(self._pos1, self._pos2)
        maxp = BlockVector3.max(self._pos1, self._pos2)
        for x in xrange(minp.x, maxp.x + 1):
            for y in xrange(minp.y, maxp.y + 1):
                for z in xrange(minp.z, maxp.z + 1):
                    yield BlockVector3(x, y, z)

    def get_min_max(self):
        if not self.is_complete():
            return None, None
        return BlockVector3.min(self._pos1, self._pos2), BlockVector3.max(self._pos1, self._pos2)

    def get_info(self):
        lines = []
        if self._pos1:
            lines.append('§aPosition 1: §f(%d, %d, %d)' % (self._pos1.x, self._pos1.y, self._pos1.z))
        if self._pos2:
            lines.append('§aPosition 2: §f(%d, %d, %d)' % (self._pos2.x, self._pos2.y, self._pos2.z))
        if self.is_complete():
            lines.append('§aVolume: §f%d blocks' % self.get_volume())
            minp, maxp = self.get_min_max()
            lines.append('§aExtent: §f(%d,%d,%d) -> (%d,%d,%d)' % (
                minp.x, minp.y, minp.z, maxp.x, maxp.y, maxp.z))
        return lines

    def clear(self):
        self._pos1 = None
        self._pos2 = None
