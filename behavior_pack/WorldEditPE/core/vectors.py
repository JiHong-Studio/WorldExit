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
BlockVector3 向量工具
对应 WorldEdit 的 BlockVector3（不可变）
支持 tuple 式索引 (v[0], v[1], v[2]) 以便在算法中直接使用
"""


class BlockVector3(object):
    """不可变的方块坐标向量"""

    def __init__(self, x, y, z):
        self._x = int(x)
        self._y = int(y)
        self._z = int(z)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    # --- tuple-like indexing ---
    def __getitem__(self, index):
        if index == 0:
            return self._x
        elif index == 1:
            return self._y
        elif index == 2:
            return self._z
        raise IndexError("BlockVector3 index out of range")

    def __len__(self):
        return 3

    def __iter__(self):
        return iter((self._x, self._y, self._z))

    # --- conversion ---
    def to_tuple(self):
        return (self._x, self._y, self._z)

    def to_float_tuple(self):
        return (float(self._x), float(self._y), float(self._z))

    # --- arithmetic ---
    def add(self, dx, dy, dz):
        return BlockVector3(self._x + dx, self._y + dy, self._z + dz)

    def subtract(self, other):
        if isinstance(other, BlockVector3):
            return BlockVector3(self._x - other._x, self._y - other._y, self._z - other._z)
        return BlockVector3(self._x - other, self._y - other, self._z - other)

    def distance(self, other):
        dx = self._x - other._x
        dy = self._y - other._y
        dz = self._z - other._z
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def length(self):
        return (self._x * self._x + self._y * self._y + self._z * self._z) ** 0.5

    # --- comparison ---
    def __eq__(self, other):
        if isinstance(other, BlockVector3):
            return self._x == other._x and self._y == other._y and self._z == other._z
        if isinstance(other, (tuple, list)) and len(other) == 3:
            return self._x == other[0] and self._y == other[1] and self._z == other[2]
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._x, self._y, self._z))

    def __repr__(self):
        return "BlockVector3(%d, %d, %d)" % (self._x, self._y, self._z)

    def __str__(self):
        return "(%d, %d, %d)" % (self._x, self._y, self._z)

    def __add__(self, other):
        if isinstance(other, BlockVector3):
            return BlockVector3(self._x + other._x, self._y + other._y, self._z + other._z)
        if isinstance(other, (tuple, list)) and len(other) == 3:
            return BlockVector3(self._x + other[0], self._y + other[1], self._z + other[2])
        return BlockVector3(self._x + other, self._y + other, self._z + other)

    def __sub__(self, other):
        if isinstance(other, BlockVector3):
            return BlockVector3(self._x - other._x, self._y - other._y, self._z - other._z)
        if isinstance(other, (tuple, list)) and len(other) == 3:
            return BlockVector3(self._x - other[0], self._y - other[1], self._z - other[2])
        return BlockVector3(self._x - other, self._y - other, self._z - other)

    def __mul__(self, scalar):
        return BlockVector3(self._x * scalar, self._y * scalar, self._z * scalar)

    @staticmethod
    def from_tuple(t):
        if t is None:
            return None
        return BlockVector3(int(t[0]), int(t[1]), int(t[2]))

    @staticmethod
    def min(a, b):
        return BlockVector3(min(a._x, b._x), min(a._y, b._y), min(a._z, b._z))

    @staticmethod
    def max(a, b):
        return BlockVector3(max(a._x, b._x), max(a._y, b._y), max(a._z, b._z))
