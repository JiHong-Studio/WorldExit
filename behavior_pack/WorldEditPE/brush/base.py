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
"""刷子系统"""

from WorldEditPE.algorithms.shapes import generate_sphere, generate_cylinder
from WorldEditPE.core.session import get_player_session
from WorldEditPE.core.history import Operation
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import block_dict_matches


def apply_brush(player_id, target_pos):
    session = get_player_session(player_id)
    if session.brush is None:
        return False

    center = target_pos  # (x, y, z) tuple
    size = session.brush_size
    pattern = session.brush_pattern
    if pattern is None:
        Notifier(player_id).error('Brush has no pattern set. Use //brush first.')
        return False

    brush_type = session.brush

    # Generate positions
    if brush_type == 'cylinder':
        pos_gen = generate_cylinder(center, size, size, pattern)
    else:
        # Default: sphere
        pos_gen = generate_sphere(center, size, pattern)

    # Convert to {pos: block_dict}
    changes = {}
    for pt in pos_gen:
        changes[pt] = pattern

    if not changes:
        return False

    operator = session.operator
    operator.dimension_id = session.get_dimension()

    # Apply mask
    mask = session.mask
    if mask is not None:
        filtered = {}
        for pt in changes:
            current = operator.get_block(pt)
            if current and block_dict_matches(current, mask):
                filtered[pt] = changes[pt]
        changes = filtered

    if not changes:
        return False

    # Record old blocks for undo
    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)

    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=brush', old_blocks, changes))
    return True
