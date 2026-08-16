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
"""实用工具命令 //fill, //drain"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.core.history import Operation
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import parse_block_str
from WorldEditPE.utils.vectors import BlockVector3
from WorldEditPE.algorithms.fill import fill_xz, drain_area
from WorldEditPE.commands.parser import register_command

def _get_pos(player_id):
    try:
        import server.extraServerApi as serverApi
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(player_id)
        pos = pos_comp.GetPos()
        dim_comp = serverApi.GetEngineCompFactory().CreateDimension(player_id)
        dim_id = dim_comp.GetEntityDimensionId()
        return BlockVector3(int(pos[0]), int(pos[1]), int(pos[2])), dim_id
    except Exception:
        return None, 0

def cmd_fill(player_id, args):
    if len(args) < 2:
        Notifier(player_id).error('Usage: //fill <block> <radius> [depth]')
        return
    block = parse_block_str(args[0])
    try:
        radius = int(args[1])
    except ValueError:
        Notifier(player_id).error('Invalid radius.')
        return
    depth = int(args[2]) if len(args) >= 3 else 1
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    center, dim_id = _get_pos(player_id)
    if center is None:
        notifier.error('Failed to get position.')
        return
    session.set_dimension(dim_id)
    operator = session.operator
    operator.dimension_id = dim_id
    changes = fill_xz(operator, center, block, radius, depth, recursive=False)
    if not changes:
        notifier.error('No blocks to fill.')
        return
    old_blocks = {pt: operator.get_block(pt) for pt in changes}
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=fill', old_blocks, changes))
    notifier.info('Fill complete: %d blocks.' % count)

def cmd_fillr(player_id, args):
    if len(args) < 2:
        Notifier(player_id).error('Usage: //fillr <block> <radius> [depth]')
        return
    block = parse_block_str(args[0])
    try:
        radius = int(args[1])
    except ValueError:
        Notifier(player_id).error('Invalid radius.')
        return
    depth = int(args[2]) if len(args) >= 3 else 999
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    center, dim_id = _get_pos(player_id)
    if center is None:
        notifier.error('Failed to get position.')
        return
    session.set_dimension(dim_id)
    operator = session.operator
    operator.dimension_id = dim_id
    changes = fill_xz(operator, center, block, radius, depth, recursive=True)
    if not changes:
        notifier.error('No blocks to fill.')
        return
    old_blocks = {pt: operator.get_block(pt) for pt in changes}
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=fillr', old_blocks, changes))
    notifier.info('Recursive fill complete: %d blocks.' % count)

def cmd_drain(player_id, args):
    if not args:
        Notifier(player_id).error('Usage: //drain <radius>')
        return
    try:
        radius = float(args[0])
    except ValueError:
        Notifier(player_id).error('Invalid radius.')
        return
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    center, dim_id = _get_pos(player_id)
    if center is None:
        notifier.error('Failed to get position.')
        return
    session.set_dimension(dim_id)
    operator = session.operator
    operator.dimension_id = dim_id
    changes = drain_area(operator, center, radius)
    if not changes:
        notifier.error('No liquids found.')
        return
    old_blocks = {pt: operator.get_block(pt) for pt in changes}
    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=drain', old_blocks, changes))
    notifier.info('Drained %d blocks.' % count)

def init_utility_commands():
    register_command('fill', cmd_fill)
    register_command('fillr', cmd_fillr)
    register_command('drain', cmd_drain)
