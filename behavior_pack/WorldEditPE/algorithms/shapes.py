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
# Shape generation algorithms for WorldEditPE
# All functions yield (x, y, z) tuples for block positions.


def generate_cylinder(center, radius, height, block):
    """Yield world positions for a solid cylinder."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    h = int(height)
    r2 = r * r
    for y_off in xrange(h):
        y = cy + y_off
        for x in xrange(cx - r, cx + r + 1):
            dx = x - cx
            dx2 = dx * dx
            for z in xrange(cz - r, cz + r + 1):
                dz = z - cz
                if dx2 + dz * dz <= r2:
                    yield (x, y, z)


def generate_hollow_cylinder(center, radius, height, block):
    """Yield world positions for a hollow cylinder (shell only)."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    h = int(height)
    r2 = r * r
    inner_r = max(0, r - 1)
    inner_r2 = inner_r * inner_r
    for y_off in xrange(h):
        y = cy + y_off
        for x in xrange(cx - r, cx + r + 1):
            dx = x - cx
            dx2 = dx * dx
            for z in xrange(cz - r, cz + r + 1):
                dz = z - cz
                d2 = dx2 + dz * dz
                if inner_r2 < d2 <= r2:
                    yield (x, y, z)


def generate_sphere(center, radius, block):
    """Yield world positions for a solid sphere."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    r2 = r * r
    for x in xrange(cx - r, cx + r + 1):
        dx = x - cx
        dx2 = dx * dx
        for y in xrange(cy - r, cy + r + 1):
            dy = y - cy
            dy2 = dy * dy
            if dx2 + dy2 > r2:
                continue
            for z in xrange(cz - r, cz + r + 1):
                dz = z - cz
                if dx2 + dy2 + dz * dz <= r2:
                    yield (x, y, z)


def generate_hollow_sphere(center, radius, block):
    """Yield world positions for a hollow sphere (shell only)."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    r2 = r * r
    inner_r = max(0, r - 1)
    inner_r2 = inner_r * inner_r
    for x in xrange(cx - r, cx + r + 1):
        dx = x - cx
        dx2 = dx * dx
        for y in xrange(cy - r, cy + r + 1):
            dy = y - cy
            dy2 = dy * dy
            if dx2 + dy2 > r2:
                continue
            for z in xrange(cz - r, cz + r + 1):
                dz = z - cz
                d2 = dx2 + dy2 + dz * dz
                if inner_r2 < d2 <= r2:
                    yield (x, y, z)


def generate_pyramid(center, size, block):
    """Yield world positions for a solid pyramid."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    s = int(size)
    for layer in xrange(s + 1):
        layer_size = s - layer
        y = cy + layer
        for x in xrange(cx - layer_size, cx + layer_size + 1):
            for z in xrange(cz - layer_size, cz + layer_size + 1):
                yield (x, y, z)


def generate_cone(center, radius, height, block):
    """Yield world positions for a solid cone."""
    cx, cy, cz = int(center[0]), int(center[1]), int(center[2])
    r = int(radius)
    h = int(height)
    for y_off in xrange(h):
        y = cy + y_off
        layer_radius = r * (h - 1 - y_off) // max(h - 1, 1) if h > 1 else r
        if layer_radius < 0:
            layer_radius = 0
        lr2 = layer_radius * layer_radius
        for x in xrange(cx - layer_radius, cx + layer_radius + 1):
            dx = x - cx
            dx2 = dx * dx
            for z in xrange(cz - layer_radius, cz + layer_radius + 1):
                dz = z - cz
                if dx2 + dz * dz <= lr2:
                    yield (x, y, z)
