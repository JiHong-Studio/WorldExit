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
"""剪贴板命令 //copy, //cut, //paste, //stack"""

from WorldEditPE.core.session import get_player_session
from WorldEditPE.core.history import Operation
from WorldEditPE.utils.vectors import BlockVector3
from WorldEditPE.utils.messages import Notifier
from WorldEditPE.utils.blocks import AIR
from WorldEditPE.commands.parser import register_command


def _get_player_pos(player_id):
    try:
        import server.extraServerApi as serverApi
        pos_comp = serverApi.GetEngineCompFactory().CreatePos(player_id)
        pos = pos_comp.GetPos()
        return BlockVector3(int(pos[0]), int(pos[1]), int(pos[2]))
    except Exception:
        return None


def cmd_copy(player_id, args):
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return

    origin = _get_player_pos(player_id)
    if origin is None:
        notifier.error('Failed to get position.')
        return

    operator = session.operator
    operator.dimension_id = sel.dimension_id

    blocks = {}
    for vec in sel.iter_positions():
        pt = vec.to_tuple()
        block = operator.get_block(vec)
        if block:
            blocks[pt] = block

    session.clipboard.store(blocks, origin)
    notifier.info('Copied %d blocks to clipboard.' % len(blocks))


def cmd_cut(player_id, args):
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)
    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return

    origin = _get_player_pos(player_id)
    if origin is None:
        notifier.error('Failed to get position.')
        return

    operator = session.operator
    operator.dimension_id = sel.dimension_id

    old_blocks = {}
    new_blocks = {}
    for vec in sel.iter_positions():
        pt = vec.to_tuple()
        block = operator.get_block(vec)
        if block:
            old_blocks[pt] = block
            new_blocks[pt] = AIR

    session.clipboard.store(old_blocks, origin)
    count = operator.set_blocks_batch(new_blocks)
    session.history.push(Operation('=cut', old_blocks, new_blocks))
    notifier.info('Cut %d blocks to clipboard.' % count)


def cmd_paste(player_id, args):
    session = get_player_session(player_id)
    notifier = Notifier(player_id)
    if session.clipboard.is_empty():
        notifier.error('Clipboard is empty. Use //copy first.')
        return

    skip_air = True
    if args and args[0] == '-a':
        skip_air = False

    target_origin = _get_player_pos(player_id)
    if target_origin is None:
        notifier.error('Failed to get position.')
        return

    try:
        import server.extraServerApi as serverApi
        dim_comp = serverApi.GetEngineCompFactory().CreateDimension(player_id)
        dim_id = dim_comp.GetEntityDimensionId()
        session.set_dimension(dim_id)
    except Exception:
        pass

    changes = session.clipboard.paste(target_origin, skip_air=skip_air)
    if not changes:
        notifier.error('No blocks to paste.')
        return

    operator = session.operator
    operator.dimension_id = session.get_dimension()

    old_blocks = {}
    for pt in changes:
        old_blocks[pt] = operator.get_block(pt)

    count = operator.set_blocks_batch(changes)
    session.history.push(Operation('=paste', old_blocks, changes))
    notifier.info('Pasted %d blocks.' % count)


def cmd_stack(player_id, args):
    """=stack <count> [direction] - 重复选区内容"""
    session = get_player_session(player_id)
    sel = session.selection
    notifier = Notifier(player_id)

    if not sel.is_complete():
        notifier.error('Make a selection first.')
        return

    if not args:
        notifier.error('Usage: =stack <count> [direction]')
        return

    try:
        count = int(args[0])
    except ValueError:
        notifier.error('Invalid count: %s' % args[0])
        return

    if count < 1:
        notifier.error('Count must be positive.')
        return

    # 解析方向
    direction = None
    if len(args) >= 2:
        dir_name = args[1].lower()
        direction_map = {
            'north': (0, 0, -1),
            'south': (0, 0, 1),
            'east': (1, 0, 0),
            'west': (-1, 0, 0),
            'up': (0, 1, 0),
            'down': (0, -1, 0),
            'me': None,
        }
        direction = direction_map.get(dir_name)
        if direction is None and dir_name != 'me':
            notifier.error('Invalid direction. Use: north, south, east, west, up, down, me')
            return

    # 如果未指定方向或指定 'me'，获取玩家面向方向
    if direction is None:
        try:
            import server.extraServerApi as serverApi
            rot_comp = serverApi.GetEngineCompFactory().CreateRot(player_id)
            rot = rot_comp.GetRot()
            dir_vec = serverApi.GetDirFromRot(rot)
            x, y, z = abs(dir_vec[0]), abs(dir_vec[1]), abs(dir_vec[2])
            if x >= y and x >= z:
                direction = (1 if dir_vec[0] > 0 else -1, 0, 0)
            elif y >= x and y >= z:
                direction = (0, 1 if dir_vec[1] > 0 else -1, 0)
            else:
                direction = (0, 0, 1 if dir_vec[2] > 0 else -1)
        except Exception as e:
            notifier.error('Could not determine direction: %s' % str(e))
            return

    # 计算选区尺寸
    minp, maxp = sel.get_min_max()
    size = (maxp.x - minp.x + 1, maxp.y - minp.y + 1, maxp.z - minp.z + 1)

    # 计算每次迭代的偏移量（根据方向取对应轴的尺寸）
    offset = (
        direction[0] * size[0] if direction[0] != 0 else 0,
        direction[1] * size[1] if direction[1] != 0 else 0,
        direction[2] * size[2] if direction[2] != 0 else 0,
    )

    # 收集选区内所有方块
    operator = session.operator
    operator.dimension_id = sel.dimension_id

    original_blocks = {}
    for vec in sel.iter_positions():
        pt = vec.to_tuple()
        block = operator.get_block(vec)
        if block:
            original_blocks[pt] = block

    if not original_blocks:
        notifier.error('No blocks to stack.')
        return

    # 执行堆叠
    old_blocks = {}
    new_blocks = {}

    for i in range(1, count + 1):
        dx = offset[0] * i
        dy = offset[1] * i
        dz = offset[2] * i

        for pt, block in original_blocks.iteritems():
            new_pt = (pt[0] + dx, pt[1] + dy, pt[2] + dz)
            old = operator.get_block(new_pt)
            if old:
                old_blocks[new_pt] = old
            new_blocks[new_pt] = block

    if new_blocks:
        operator.set_blocks_batch(new_blocks)
        session.history.push(Operation('=stack', old_blocks, new_blocks))

    notifier.info('Stacked %d blocks (%d times).' % (len(new_blocks), count))


def init_clipboard_commands():
    register_command('copy', cmd_copy)
    register_command('cut', cmd_cut)
    register_command('paste', cmd_paste)
    register_command('stack', cmd_stack)
